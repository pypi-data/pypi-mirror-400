"""
SQLite数据库后端模块
替代JSON文件存储，提供更好的性能
"""
import sqlite3
import datetime
import os
import json
import threading
from contextlib import contextmanager
from pathlib import Path

# 数据库连接池（每个线程一个连接）
_local = threading.local()


class Database:
    """SQLite数据库管理类"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self):
        """获取当前线程的数据库连接"""
        if not hasattr(_local, 'connection') or _local.connection is None:
            _local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            _local.connection.row_factory = sqlite3.Row
            # 启用外键约束
            _local.connection.execute('PRAGMA foreign_keys = ON')
            # 优化性能设置
            _local.connection.execute('PRAGMA journal_mode = WAL')
            _local.connection.execute('PRAGMA synchronous = NORMAL')
            _local.connection.execute('PRAGMA cache_size = -64000')  # 64MB cache
            _local.connection.execute('PRAGMA temp_store = MEMORY')
        return _local.connection
    
    @contextmanager
    def get_cursor(self):
        """获取数据库游标的上下文管理器"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def _init_db(self):
        """初始化数据库表结构"""
        with self.get_cursor() as cursor:
            # 项目表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    note TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # 文件夹表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    path TEXT NOT NULL,
                    keyword_filter TEXT DEFAULT '',
                    imported_at TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    UNIQUE(project_id, path)
                )
            ''')
            
            # 类别表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    UNIQUE(project_id, name)
                )
            ''')
            
            # 文件表（最重要的表）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    path TEXT NOT NULL,
                    category TEXT DEFAULT '',
                    imported_at TEXT NOT NULL,
                    source TEXT DEFAULT '',
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    UNIQUE(project_id, path)
                )
            ''')
            
            # 创建索引以优化查询性能（优化：移除不必要的路径索引，减少空间占用）
            # 只创建必要的索引：
            # 1. project_id索引 - 用于按项目查询（必需）
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_project_id ON files(project_id)')
            # 2. category索引 - 用于按类别筛选（必需）
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_category ON files(project_id, category)')
            # 3. 移除idx_files_path - 路径查询很少，且可通过project_id+path组合查询，节省大量空间
            # 4. folders和categories的project_id索引 - 必需
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_folders_project_id ON folders(project_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_categories_project_id ON categories(project_id)')
            
            # 尝试删除旧的路径索引（如果存在）- 这个索引占用大量空间但很少使用
            try:
                cursor.execute('DROP INDEX IF EXISTS idx_files_path')
            except:
                pass
            
            # 添加exported字段（如果不存在）
            try:
                cursor.execute('ALTER TABLE files ADD COLUMN exported INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                # 字段已存在，忽略错误
                pass
            
            # 创建exported字段的索引以优化查询
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_exported ON files(project_id, exported)')
            
            # 优化数据库设置
            cursor.execute('PRAGMA optimize')
    
    # ==================== 项目相关操作 ====================
    
    def get_project_id(self, project_name):
        """根据项目名获取项目ID"""
        with self.get_cursor() as cursor:
            cursor.execute('SELECT id FROM projects WHERE name = ?', (project_name,))
            row = cursor.fetchone()
            return row['id'] if row else None
    
    def get_all_projects(self):
        """获取所有项目列表"""
        with self.get_cursor() as cursor:
            cursor.execute('''
                SELECT p.name, p.note, p.created_at, 
                       (SELECT COUNT(*) FROM files WHERE project_id = p.id) as file_count
                FROM projects p
                ORDER BY p.updated_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def create_project(self, name, note=''):
        """创建新项目"""
        now = datetime.datetime.now().isoformat()
        with self.get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO projects (name, note, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (name, note, now, now))
            project_id = cursor.lastrowid
            return {
                'id': project_id,
                'name': name,
                'note': note,
                'created_at': now,
                'updated_at': now,
                'folders': [],
                'categories': [],
                'files': []
            }
    
    def load_project(self, project_name):
        """加载项目数据（兼容原有JSON格式）"""
        with self.get_cursor() as cursor:
            # 获取项目基本信息
            cursor.execute('SELECT * FROM projects WHERE name = ?', (project_name,))
            project_row = cursor.fetchone()
            if not project_row:
                return None
            
            project_id = project_row['id']
            
            # 获取文件夹
            cursor.execute('SELECT path, keyword_filter, imported_at FROM folders WHERE project_id = ?', (project_id,))
            folders = [dict(row) for row in cursor.fetchall()]
            
            # 获取类别
            cursor.execute('SELECT name FROM categories WHERE project_id = ?', (project_id,))
            categories = [row['name'] for row in cursor.fetchall()]
            
            # 注意：这里不加载所有文件，因为文件量可能很大
            # 文件通过分页API单独获取
            
            return {
                'name': project_row['name'],
                'note': project_row['note'],
                'created_at': project_row['created_at'],
                'updated_at': project_row['updated_at'],
                'folders': folders,
                'categories': categories,
                'files': []  # 空列表，文件通过其他方法获取
            }
    
    def load_project_full(self, project_name):
        """加载完整项目数据（包括所有文件，用于导出等场景）"""
        with self.get_cursor() as cursor:
            cursor.execute('SELECT * FROM projects WHERE name = ?', (project_name,))
            project_row = cursor.fetchone()
            if not project_row:
                return None
            
            project_id = project_row['id']
            
            cursor.execute('SELECT path, keyword_filter, imported_at FROM folders WHERE project_id = ?', (project_id,))
            folders = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('SELECT name FROM categories WHERE project_id = ?', (project_id,))
            categories = [row['name'] for row in cursor.fetchall()]
            
            cursor.execute('SELECT path, category, imported_at, source FROM files WHERE project_id = ?', (project_id,))
            files = [dict(row) for row in cursor.fetchall()]
            
            return {
                'name': project_row['name'],
                'note': project_row['note'],
                'created_at': project_row['created_at'],
                'updated_at': project_row['updated_at'],
                'folders': folders,
                'categories': categories,
                'files': files
            }
    
    def save_project(self, project_data):
        """保存项目数据（兼容原有JSON格式的完整保存）"""
        now = datetime.datetime.now().isoformat()
        with self.get_cursor() as cursor:
            # 检查项目是否存在
            cursor.execute('SELECT id FROM projects WHERE name = ?', (project_data['name'],))
            row = cursor.fetchone()
            
            if row:
                project_id = row['id']
                # 更新项目基本信息
                cursor.execute('''
                    UPDATE projects SET note = ?, updated_at = ? WHERE id = ?
                ''', (project_data.get('note', ''), now, project_id))
            else:
                # 创建新项目
                cursor.execute('''
                    INSERT INTO projects (name, note, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (project_data['name'], project_data.get('note', ''), 
                      project_data.get('created_at', now), now))
                project_id = cursor.lastrowid
            
            # 更新文件夹（先删除旧的，再插入新的）
            cursor.execute('DELETE FROM folders WHERE project_id = ?', (project_id,))
            for folder in project_data.get('folders', []):
                cursor.execute('''
                    INSERT INTO folders (project_id, path, keyword_filter, imported_at)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, folder['path'], folder.get('keyword_filter', ''), 
                      folder.get('imported_at', now)))
            
            # 更新类别
            cursor.execute('DELETE FROM categories WHERE project_id = ?', (project_id,))
            for category in project_data.get('categories', []):
                cursor.execute('''
                    INSERT INTO categories (project_id, name) VALUES (?, ?)
                ''', (project_id, category))
            
            # 更新文件（如果提供了文件列表）
            # 使用批量插入优化性能
            if 'files' in project_data and project_data['files']:
                cursor.execute('DELETE FROM files WHERE project_id = ?', (project_id,))
                cursor.executemany('''
                    INSERT INTO files (project_id, path, category, imported_at, source)
                    VALUES (?, ?, ?, ?, ?)
                ''', [(project_id, f['path'], f.get('category', ''), 
                       f.get('imported_at', now), f.get('source', '')) 
                      for f in project_data['files']])
    
    def update_project_meta(self, project_name, new_name=None, note=None):
        """更新项目元信息"""
        now = datetime.datetime.now().isoformat()
        with self.get_cursor() as cursor:
            if new_name and new_name != project_name:
                cursor.execute('''
                    UPDATE projects SET name = ?, note = ?, updated_at = ?
                    WHERE name = ?
                ''', (new_name, note or '', now, project_name))
            else:
                cursor.execute('''
                    UPDATE projects SET note = ?, updated_at = ?
                    WHERE name = ?
                ''', (note or '', now, project_name))
    
    def delete_project(self, project_name):
        """删除项目"""
        with self.get_cursor() as cursor:
            cursor.execute('DELETE FROM projects WHERE name = ?', (project_name,))
            return cursor.rowcount > 0
    
    def project_exists(self, project_name):
        """检查项目是否存在"""
        return self.get_project_id(project_name) is not None
    
    # ==================== 文件相关操作 ====================
    
    def get_files(self, project_name, category=None, page=1, per_page=20):
        """分页获取文件列表"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return None
        
        offset = (page - 1) * per_page
        
        with self.get_cursor() as cursor:
            # 构建查询
            # category 约定：
            # - None: 全部
            # - '': 未分类（兼容 NULL）
            # - 其他字符串: 指定类别
            if category is None:
                cursor.execute('''
                    SELECT path, category, imported_at, source 
                    FROM files WHERE project_id = ?
                    LIMIT ? OFFSET ?
                ''', (project_id, per_page, offset))
                files = [dict(row) for row in cursor.fetchall()]
                
                cursor.execute('''
                    SELECT COUNT(*) as count FROM files WHERE project_id = ?
                ''', (project_id,))
            elif category == '':
                cursor.execute('''
                    SELECT path, category, imported_at, source
                    FROM files
                    WHERE project_id = ? AND (category = '' OR category IS NULL)
                    LIMIT ? OFFSET ?
                ''', (project_id, per_page, offset))
                files = [dict(row) for row in cursor.fetchall()]

                cursor.execute('''
                    SELECT COUNT(*) as count FROM files
                    WHERE project_id = ? AND (category = '' OR category IS NULL)
                ''', (project_id,))
            else:
                cursor.execute('''
                    SELECT path, category, imported_at, source
                    FROM files WHERE project_id = ? AND category = ?
                    LIMIT ? OFFSET ?
                ''', (project_id, category, per_page, offset))
                files = [dict(row) for row in cursor.fetchall()]

                cursor.execute('''
                    SELECT COUNT(*) as count FROM files
                    WHERE project_id = ? AND category = ?
                ''', (project_id, category))
            
            total = cursor.fetchone()['count']
        
        return {
            'files': files,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def get_all_files(self, project_name, category=None, include_exported=True):
        """获取所有文件（用于导出等场景）
        
        Args:
            project_name: 项目名称
            category: 类别筛选（可选）
            include_exported: 是否包含已导出的文件，默认True
        """
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return []
        
        with self.get_cursor() as cursor:
            if category:
                if include_exported:
                    cursor.execute('''
                        SELECT path, category, imported_at, source, id
                        FROM files WHERE project_id = ? AND category = ?
                    ''', (project_id, category))
                else:
                    cursor.execute('''
                        SELECT path, category, imported_at, source, id
                        FROM files WHERE project_id = ? AND category = ? AND (exported = 0 OR exported IS NULL)
                    ''', (project_id, category))
            else:
                if include_exported:
                    cursor.execute('''
                        SELECT path, category, imported_at, source, id
                        FROM files WHERE project_id = ?
                    ''', (project_id,))
                else:
                    cursor.execute('''
                        SELECT path, category, imported_at, source, id
                        FROM files WHERE project_id = ? AND (exported = 0 OR exported IS NULL)
                    ''', (project_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_files_by_categories(self, project_name, categories, include_exported=True):
        """根据多个类别获取文件
        
        Args:
            project_name: 项目名称
            categories: 类别列表，如果包含空字符串''或'__uncategorized__'，则查询未分类文件
            include_exported: 是否包含已导出的文件，默认True
        """
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return []
        
        if not categories:
            return self.get_all_files(project_name, include_exported=include_exported)
        
        # 检查是否包含未分类的标记
        has_uncategorized = '' in categories or '__uncategorized__' in categories
        # 过滤掉未分类标记，保留其他类别
        regular_categories = [c for c in categories if c and c != '__uncategorized__']
        
        conditions = []
        params = [project_id]
        
        # 如果有常规类别，添加常规类别的查询条件
        if regular_categories:
            placeholders = ','.join(['?' for _ in regular_categories])
            conditions.append(f'category IN ({placeholders})')
            params.extend(regular_categories)
        
        # 如果有未分类标记，添加未分类的查询条件
        if has_uncategorized:
            conditions.append('(category = \'\' OR category IS NULL)')
        
        if not conditions:
            return []
        
        where_clause = ' OR '.join(conditions)
        exported_clause = '' if include_exported else ' AND (exported = 0 OR exported IS NULL)'
        
        with self.get_cursor() as cursor:
            cursor.execute(f'''
                SELECT path, category, imported_at, source, id
                FROM files WHERE project_id = ? AND ({where_clause}){exported_clause}
            ''', params)
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_files_as_exported(self, project_name, file_ids):
        """标记文件为已导出
        
        Args:
            project_name: 项目名称
            file_ids: 文件ID列表
        """
        if not file_ids:
            return
        
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return
        
        placeholders = ','.join(['?' for _ in file_ids])
        with self.get_cursor() as cursor:
            cursor.execute(f'''
                UPDATE files 
                SET exported = 1 
                WHERE project_id = ? AND id IN ({placeholders})
            ''', [project_id] + list(file_ids))
    
    def reset_exported_status(self, project_name, categories=None):
        """重置导出状态（将已导出文件标记为未导出）
        
        Args:
            project_name: 项目名称
            categories: 类别列表，None或空列表表示全部类别
        
        Returns:
            重置的文件数量
        """
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return 0
        
        with self.get_cursor() as cursor:
            if categories:
                # 重置指定类别的文件
                placeholders = ','.join(['?' for _ in categories])
                cursor.execute(f'''
                    UPDATE files 
                    SET exported = 0 
                    WHERE project_id = ? AND category IN ({placeholders}) AND exported = 1
                ''', [project_id] + list(categories))
            else:
                # 重置所有文件
                cursor.execute('''
                    UPDATE files 
                    SET exported = 0 
                    WHERE project_id = ? AND exported = 1
                ''', (project_id,))
            return cursor.rowcount
    
    def get_image_files(self, project_name, image_extensions, category=None, page=1, per_page=20):
        """获取图片文件列表"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return None
        
        offset = (page - 1) * per_page
        
        # 构建扩展名匹配条件
        ext_conditions = ' OR '.join([f"LOWER(path) LIKE '%{ext}'" for ext in image_extensions])
        
        with self.get_cursor() as cursor:
            # category 约定：
            # - None: 全部
            # - '': 未分类（兼容 NULL）
            # - 其他字符串: 指定类别
            if category is None:
                cursor.execute(f'''
                    SELECT path, category, imported_at, source 
                    FROM files 
                    WHERE project_id = ? AND ({ext_conditions})
                    LIMIT ? OFFSET ?
                ''', (project_id, per_page, offset))
                files = [dict(row) for row in cursor.fetchall()]
                
                cursor.execute(f'''
                    SELECT COUNT(*) as count FROM files 
                    WHERE project_id = ? AND ({ext_conditions})
                ''', (project_id,))
            elif category == '':
                cursor.execute(f'''
                    SELECT path, category, imported_at, source
                    FROM files
                    WHERE project_id = ? AND (category = '' OR category IS NULL) AND ({ext_conditions})
                    LIMIT ? OFFSET ?
                ''', (project_id, per_page, offset))
                files = [dict(row) for row in cursor.fetchall()]

                cursor.execute(f'''
                    SELECT COUNT(*) as count FROM files
                    WHERE project_id = ? AND (category = '' OR category IS NULL) AND ({ext_conditions})
                ''', (project_id,))
            else:
                cursor.execute(f'''
                    SELECT path, category, imported_at, source
                    FROM files
                    WHERE project_id = ? AND category = ? AND ({ext_conditions})
                    LIMIT ? OFFSET ?
                ''', (project_id, category, per_page, offset))
                files = [dict(row) for row in cursor.fetchall()]

                cursor.execute(f'''
                    SELECT COUNT(*) as count FROM files
                    WHERE project_id = ? AND category = ? AND ({ext_conditions})
                ''', (project_id, category))
            
            total = cursor.fetchone()['count']
        
        return {
            'images': files,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def add_files(self, project_name, files):
        """批量添加文件"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return 0
        
        now = datetime.datetime.now().isoformat()
        added_count = 0
        
        with self.get_cursor() as cursor:
            for file_info in files:
                try:
                    cursor.execute('''
                        INSERT INTO files (project_id, path, category, imported_at, source)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (project_id, file_info['path'], file_info.get('category', ''),
                          file_info.get('imported_at', now), file_info.get('source', '')))
                    added_count += 1
                except sqlite3.IntegrityError:
                    # 文件已存在，跳过
                    pass
            
            # 更新项目修改时间
            cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))
        
        return added_count
    
    def add_files_batch(self, project_name, files):
        """高效批量添加文件（使用INSERT OR IGNORE）"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return 0
        
        now = datetime.datetime.now().isoformat()
        
        with self.get_cursor() as cursor:
            # 获取添加前的文件数
            cursor.execute('SELECT COUNT(*) as count FROM files WHERE project_id = ?', (project_id,))
            before_count = cursor.fetchone()['count']
            
            # 批量插入，忽略重复
            cursor.executemany('''
                INSERT OR IGNORE INTO files (project_id, path, category, imported_at, source)
                VALUES (?, ?, ?, ?, ?)
            ''', [(project_id, f['path'], f.get('category', ''),
                   f.get('imported_at', now), f.get('source', ''))
                  for f in files])
            
            # 获取添加后的文件数
            cursor.execute('SELECT COUNT(*) as count FROM files WHERE project_id = ?', (project_id,))
            after_count = cursor.fetchone()['count']
            
            # 更新项目修改时间
            cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))
        
        return after_count - before_count
    
    def update_file_category(self, project_name, file_path, category):
        """更新单个文件的类别"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return False
        
        now = datetime.datetime.now().isoformat()
        with self.get_cursor() as cursor:
            cursor.execute('''
                UPDATE files SET category = ? WHERE project_id = ? AND path = ?
            ''', (category, project_id, file_path))
            cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))
            return cursor.rowcount > 0
    
    def update_files_category(self, project_name, file_paths, category):
        """批量更新文件类别"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return 0
        
        now = datetime.datetime.now().isoformat()
        with self.get_cursor() as cursor:
            updated_count = 0
            for path in file_paths:
                cursor.execute('''
                    UPDATE files SET category = ? WHERE project_id = ? AND path = ?
                ''', (category, project_id, path))
                updated_count += cursor.rowcount
            
            cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))
        
        return updated_count
    
    def update_files_category_batch(self, project_name, file_paths, category):
        """高效批量更新文件类别"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return 0
        
        if not file_paths:
            return 0
        
        now = datetime.datetime.now().isoformat()
        
        with self.get_cursor() as cursor:
            # 使用临时表进行批量更新
            cursor.execute('CREATE TEMP TABLE IF NOT EXISTS temp_paths (path TEXT PRIMARY KEY)')
            cursor.execute('DELETE FROM temp_paths')
            cursor.executemany('INSERT INTO temp_paths (path) VALUES (?)', [(p,) for p in file_paths])
            
            cursor.execute('''
                UPDATE files SET category = ?
                WHERE project_id = ? AND path IN (SELECT path FROM temp_paths)
            ''', (category, project_id))
            updated_count = cursor.rowcount
            
            cursor.execute('DELETE FROM temp_paths')
            cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))
        
        return updated_count
    
    def update_empty_category_files(self, project_name, file_category_map):
        """更新没有类别的文件（用于导入带类别的文件时更新已存在但无类别的文件）"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return 0
        
        now = datetime.datetime.now().isoformat()
        updated_count = 0
        
        with self.get_cursor() as cursor:
            for path, category in file_category_map.items():
                cursor.execute('''
                    UPDATE files SET category = ?
                    WHERE project_id = ? AND path = ? AND (category = '' OR category IS NULL)
                ''', (category, project_id, path))
                updated_count += cursor.rowcount
            
            if updated_count > 0:
                cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))
        
        return updated_count
    
    def delete_files_by_keyword(self, project_name, keyword):
        """删除路径包含指定关键字的文件"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return 0
        
        now = datetime.datetime.now().isoformat()
        with self.get_cursor() as cursor:
            cursor.execute('''
                DELETE FROM files WHERE project_id = ? AND path LIKE ?
            ''', (project_id, f'%{keyword}%'))
            removed_count = cursor.rowcount
            cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))
        
        return removed_count
    
    def delete_files_by_category(self, project_name, category):
        """删除指定类别的所有文件"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return 0
        
        now = datetime.datetime.now().isoformat()
        with self.get_cursor() as cursor:
            cursor.execute('''
                DELETE FROM files WHERE project_id = ? AND category = ?
            ''', (project_id, category))
            removed_count = cursor.rowcount
            cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))
        
        return removed_count
    
    def get_file_count(self, project_name):
        """获取项目文件总数"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return 0
        
        with self.get_cursor() as cursor:
            cursor.execute('SELECT COUNT(*) as count FROM files WHERE project_id = ?', (project_id,))
            return cursor.fetchone()['count']
    
    def get_existing_file_paths(self, project_name):
        """获取项目中所有文件路径（用于检查重复）"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return set()
        
        with self.get_cursor() as cursor:
            cursor.execute('SELECT path FROM files WHERE project_id = ?', (project_id,))
            return {row['path'] for row in cursor.fetchall()}
    
    def file_exists(self, project_name, file_path):
        """检查文件是否存在"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return False
        
        with self.get_cursor() as cursor:
            cursor.execute('''
                SELECT 1 FROM files WHERE project_id = ? AND path = ? LIMIT 1
            ''', (project_id, file_path))
            return cursor.fetchone() is not None
    
    # ==================== 类别相关操作 ====================
    
    def get_categories(self, project_name):
        """获取项目的所有类别"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return []
        
        with self.get_cursor() as cursor:
            cursor.execute('SELECT name FROM categories WHERE project_id = ?', (project_id,))
            return [row['name'] for row in cursor.fetchall()]
    
    def add_category(self, project_name, category):
        """添加类别"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return False
        
        now = datetime.datetime.now().isoformat()
        with self.get_cursor() as cursor:
            try:
                cursor.execute('''
                    INSERT INTO categories (project_id, name) VALUES (?, ?)
                ''', (project_id, category))
                cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))
                return True
            except sqlite3.IntegrityError:
                return False  # 类别已存在
    
    def add_categories(self, project_name, categories):
        """批量添加类别"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return 0
        
        now = datetime.datetime.now().isoformat()
        added_count = 0
        
        with self.get_cursor() as cursor:
            for category in categories:
                try:
                    cursor.execute('''
                        INSERT INTO categories (project_id, name) VALUES (?, ?)
                    ''', (project_id, category))
                    added_count += 1
                except sqlite3.IntegrityError:
                    pass
            
            if added_count > 0:
                cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))
        
        return added_count
    
    def delete_category(self, project_name, category):
        """删除类别"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return False
        
        now = datetime.datetime.now().isoformat()
        with self.get_cursor() as cursor:
            cursor.execute('''
                DELETE FROM categories WHERE project_id = ? AND name = ?
            ''', (project_id, category))
            cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))
            return cursor.rowcount > 0
    
    def category_exists(self, project_name, category):
        """检查类别是否存在"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return False
        
        with self.get_cursor() as cursor:
            cursor.execute('''
                SELECT 1 FROM categories WHERE project_id = ? AND name = ? LIMIT 1
            ''', (project_id, category))
            return cursor.fetchone() is not None

    def merge_category(self, project_name, source_category, target_category, delete_source=True):
        """合并类别：将 source_category 下的所有文件转移到 target_category

        约定：
        - 未分类使用空字符串 '' 表示（兼容旧数据可能为NULL）
        - 当 delete_source=True 且 source_category 非空时，会从 categories 表移除源类别

        Returns:
            dict: {'updated_files': int, 'deleted_source_category': bool}
        """
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return None

        # 规范化：None 视为未分类
        source_category = '' if source_category is None else str(source_category)
        target_category = '' if target_category is None else str(target_category)

        if source_category == target_category:
            return {'updated_files': 0, 'deleted_source_category': False}

        now = datetime.datetime.now().isoformat()
        deleted_source = False

        with self.get_cursor() as cursor:
            # 确保目标类别存在（目标为未分类则不落 categories 表）
            if target_category:
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (project_id, name) VALUES (?, ?)
                ''', (project_id, target_category))

            # 批量更新 files.category
            if source_category == '':
                # 未分类：兼容 NULL
                cursor.execute('''
                    UPDATE files
                    SET category = ?
                    WHERE project_id = ? AND (category = '' OR category IS NULL)
                ''', (target_category, project_id))
            else:
                cursor.execute('''
                    UPDATE files
                    SET category = ?
                    WHERE project_id = ? AND category = ?
                ''', (target_category, project_id, source_category))
            updated_files = cursor.rowcount

            # 删除源类别（可选）
            if delete_source and source_category:
                cursor.execute('''
                    DELETE FROM categories WHERE project_id = ? AND name = ?
                ''', (project_id, source_category))
                deleted_source = cursor.rowcount > 0

            cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))

        return {'updated_files': updated_files, 'deleted_source_category': deleted_source}

    def merge_categories(self, project_name, source_categories, target_category, delete_source=True):
        """合并多个源类别到同一个目标类别（单事务）

        Args:
            source_categories: list[str] 源类别列表（可包含 '' / None 表示未分类）
            target_category: str 目标类别（''/None 表示未分类）
            delete_source: bool 是否删除源类别（对未分类无效；且不会删除与目标同名的类别）
        """
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return None

        if not source_categories:
            return {'updated_files': 0, 'deleted_source_categories': 0}

        # 规范化
        target_category = '' if target_category is None else str(target_category)
        normalized_sources = []
        for c in source_categories:
            if c is None:
                normalized_sources.append('')
            else:
                normalized_sources.append(str(c))

        # 去重 & 过滤与目标相同
        normalized_sources = [c for c in dict.fromkeys(normalized_sources) if c != target_category]
        if not normalized_sources:
            return {'updated_files': 0, 'deleted_source_categories': 0}

        now = datetime.datetime.now().isoformat()

        has_uncategorized = '' in normalized_sources
        regular_sources = [c for c in normalized_sources if c]

        with self.get_cursor() as cursor:
            # 确保目标类别存在（目标为未分类则不落 categories 表）
            if target_category:
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (project_id, name) VALUES (?, ?)
                ''', (project_id, target_category))

            updated_files = 0

            # 更新常规类别
            if regular_sources:
                placeholders = ','.join(['?' for _ in regular_sources])
                cursor.execute(f'''
                    UPDATE files
                    SET category = ?
                    WHERE project_id = ? AND category IN ({placeholders})
                ''', [target_category, project_id] + list(regular_sources))
                updated_files += cursor.rowcount

            # 更新未分类（兼容 NULL）
            if has_uncategorized:
                cursor.execute('''
                    UPDATE files
                    SET category = ?
                    WHERE project_id = ? AND (category = '' OR category IS NULL)
                ''', (target_category, project_id))
                updated_files += cursor.rowcount

            deleted_count = 0
            if delete_source and regular_sources:
                # 不删除目标类别本身（已过滤同名，但再保险）
                to_delete = [c for c in regular_sources if c != target_category]
                if to_delete:
                    placeholders = ','.join(['?' for _ in to_delete])
                    cursor.execute(f'''
                        DELETE FROM categories
                        WHERE project_id = ? AND name IN ({placeholders})
                    ''', [project_id] + list(to_delete))
                    deleted_count = cursor.rowcount

            cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))

        return {'updated_files': updated_files, 'deleted_source_categories': deleted_count}
    
    # ==================== 文件夹相关操作 ====================
    
    def get_folders(self, project_name):
        """获取项目的所有文件夹"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return []
        
        with self.get_cursor() as cursor:
            cursor.execute('''
                SELECT path, keyword_filter, imported_at 
                FROM folders WHERE project_id = ?
            ''', (project_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def add_folder(self, project_name, folder_info):
        """添加文件夹"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return False
        
        now = datetime.datetime.now().isoformat()
        with self.get_cursor() as cursor:
            try:
                cursor.execute('''
                    INSERT INTO folders (project_id, path, keyword_filter, imported_at)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, folder_info['path'], 
                      folder_info.get('keyword_filter', ''),
                      folder_info.get('imported_at', now)))
                cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, project_id))
                return True
            except sqlite3.IntegrityError:
                return False  # 文件夹已存在
    
    def get_folder(self, project_name, folder_path):
        """获取指定文件夹"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return None
        
        with self.get_cursor() as cursor:
            cursor.execute('''
                SELECT path, keyword_filter, imported_at 
                FROM folders WHERE project_id = ? AND path = ?
            ''', (project_id, folder_path))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ==================== 统计相关操作 ====================
    
    def get_stats(self, project_name):
        """获取项目统计信息"""
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return None
        
        with self.get_cursor() as cursor:
            # 总文件数
            cursor.execute('SELECT COUNT(*) as count FROM files WHERE project_id = ?', (project_id,))
            total = cursor.fetchone()['count']
            
            # 已导出文件数
            cursor.execute('SELECT COUNT(*) as count FROM files WHERE project_id = ? AND exported = 1', (project_id,))
            exported_total = cursor.fetchone()['count']
            
            # 各类别文件数（所有文件）
            cursor.execute('''
                SELECT COALESCE(NULLIF(category, ''), '未分类') as cat, COUNT(*) as count 
                FROM files WHERE project_id = ?
                GROUP BY category
            ''', (project_id,))
            category_count = {row['cat']: row['count'] for row in cursor.fetchall()}
            
            # 各类别已导出文件数
            cursor.execute('''
                SELECT COALESCE(NULLIF(category, ''), '未分类') as cat, COUNT(*) as count 
                FROM files WHERE project_id = ? AND exported = 1
                GROUP BY category
            ''', (project_id,))
            exported_category_count = {row['cat']: row['count'] for row in cursor.fetchall()}
        
        return {
            'total': total,
            'exported_total': exported_total,
            'category_count': category_count,
            'exported_category_count': exported_category_count
        }
    
    # ==================== 项目操作（分割、合并、复制）====================
    
    def copy_project(self, source_name, target_name, note_suffix=''):
        """复制项目"""
        source_id = self.get_project_id(source_name)
        if source_id is None:
            return None
        
        if self.project_exists(target_name):
            return None
        
        now = datetime.datetime.now().isoformat()
        
        with self.get_cursor() as cursor:
            # 获取源项目信息
            cursor.execute('SELECT * FROM projects WHERE id = ?', (source_id,))
            source_project = cursor.fetchone()
            
            # 创建新项目
            new_note = f"{source_project['note']} {note_suffix}".strip()
            cursor.execute('''
                INSERT INTO projects (name, note, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (target_name, new_note, now, now))
            target_id = cursor.lastrowid
            
            # 复制文件夹
            cursor.execute('''
                INSERT INTO folders (project_id, path, keyword_filter, imported_at)
                SELECT ?, path, keyword_filter, imported_at FROM folders WHERE project_id = ?
            ''', (target_id, source_id))
            
            # 复制类别
            cursor.execute('''
                INSERT INTO categories (project_id, name)
                SELECT ?, name FROM categories WHERE project_id = ?
            ''', (target_id, source_id))
            
            # 复制文件
            cursor.execute('''
                INSERT INTO files (project_id, path, category, imported_at, source)
                SELECT ?, path, category, imported_at, source FROM files WHERE project_id = ?
            ''', (target_id, source_id))
            
            file_count = cursor.rowcount
        
        return {
            'name': target_name,
            'file_count': file_count
        }
    
    def split_project(self, source_name, n):
        """分割项目为N份"""
        source_id = self.get_project_id(source_name)
        if source_id is None:
            return None
        
        now = datetime.datetime.now().isoformat()
        
        with self.get_cursor() as cursor:
            # 获取源项目信息
            cursor.execute('SELECT * FROM projects WHERE id = ?', (source_id,))
            source_project = cursor.fetchone()
            
            # 获取所有文件ID并随机打乱
            cursor.execute('SELECT id FROM files WHERE project_id = ? ORDER BY RANDOM()', (source_id,))
            file_ids = [row['id'] for row in cursor.fetchall()]
            
            if not file_ids:
                return None
            
            # 获取类别
            cursor.execute('SELECT name FROM categories WHERE project_id = ?', (source_id,))
            categories = [row['name'] for row in cursor.fetchall()]
            
            split_results = []
            
            for i in range(n):
                # 分配文件ID
                split_file_ids = file_ids[i::n]
                if not split_file_ids:
                    continue
                
                new_project_name = f"{source_name}_split_{i+1}"
                
                # 检查项目名是否已存在
                if self.project_exists(new_project_name):
                    return None
                
                # 创建新项目
                new_note = f"{source_project['note']} (分割自 {source_name})"
                cursor.execute('''
                    INSERT INTO projects (name, note, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (new_project_name, new_note, now, now))
                new_project_id = cursor.lastrowid
                
                # 复制类别
                for category in categories:
                    cursor.execute('''
                        INSERT INTO categories (project_id, name) VALUES (?, ?)
                    ''', (new_project_id, category))
                
                # 复制分配的文件
                placeholders = ','.join(['?' for _ in split_file_ids])
                cursor.execute(f'''
                    INSERT INTO files (project_id, path, category, imported_at, source)
                    SELECT ?, path, category, imported_at, source 
                    FROM files WHERE id IN ({placeholders})
                ''', [new_project_id] + split_file_ids)
                
                split_results.append({
                    'name': new_project_name,
                    'file_count': len(split_file_ids)
                })
        
        return {
            'split_projects': split_results,
            'total_files': len(file_ids)
        }
    
    def merge_projects(self, source_names, target_name, conflict_resolution='first'):
        """合并多个项目"""
        if self.project_exists(target_name):
            return None
        
        now = datetime.datetime.now().isoformat()
        
        # 检查所有源项目是否存在
        source_ids = []
        for name in source_names:
            pid = self.get_project_id(name)
            if pid is None:
                return None
            source_ids.append((name, pid))
        
        with self.get_cursor() as cursor:
            # 创建目标项目
            cursor.execute('''
                INSERT INTO projects (name, note, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (target_name, f"合并自: {', '.join(source_names)}", now, now))
            target_id = cursor.lastrowid
            
            # 收集所有类别（去重）
            all_categories = set()
            for _, source_id in source_ids:
                cursor.execute('SELECT name FROM categories WHERE project_id = ?', (source_id,))
                all_categories.update(row['name'] for row in cursor.fetchall())
            
            for category in all_categories:
                cursor.execute('''
                    INSERT INTO categories (project_id, name) VALUES (?, ?)
                ''', (target_id, category))
            
            # 收集所有文件夹（去重）
            folder_paths_seen = set()
            for _, source_id in source_ids:
                cursor.execute('SELECT path, keyword_filter, imported_at FROM folders WHERE project_id = ?', (source_id,))
                for row in cursor.fetchall():
                    if row['path'] not in folder_paths_seen:
                        cursor.execute('''
                            INSERT INTO folders (project_id, path, keyword_filter, imported_at)
                            VALUES (?, ?, ?, ?)
                        ''', (target_id, row['path'], row['keyword_filter'], row['imported_at']))
                        folder_paths_seen.add(row['path'])
            
            # 合并文件（根据冲突策略）
            file_paths_seen = set()
            conflict_count = 0
            
            order = source_ids if conflict_resolution == 'first' else reversed(source_ids)
            for _, source_id in order:
                cursor.execute('''
                    SELECT path, category, imported_at, source FROM files WHERE project_id = ?
                ''', (source_id,))
                
                for row in cursor.fetchall():
                    if row['path'] not in file_paths_seen:
                        cursor.execute('''
                            INSERT INTO files (project_id, path, category, imported_at, source)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (target_id, row['path'], row['category'], row['imported_at'], row['source']))
                        file_paths_seen.add(row['path'])
                    else:
                        conflict_count += 1
            
            total_files = len(file_paths_seen)
        
        return {
            'target_project': target_name,
            'total_files': total_files,
            'conflict_count': conflict_count
        }
    
    def check_merge_conflicts(self, source_names):
        """检测合并冲突"""
        # 检查所有源项目是否存在
        source_ids = []
        for name in source_names:
            pid = self.get_project_id(name)
            if pid is None:
                return None
            source_ids.append((name, pid))
        
        # 收集所有文件路径及其来源
        file_paths = {}  # {path: [(project_name, category)]}
        
        with self.get_cursor() as cursor:
            for name, source_id in source_ids:
                cursor.execute('''
                    SELECT path, category FROM files WHERE project_id = ?
                ''', (source_id,))
                for row in cursor.fetchall():
                    path = row['path']
                    if path not in file_paths:
                        file_paths[path] = []
                    file_paths[path].append((name, row['category']))
        
        # 找出冲突
        conflicts = []
        for path, occurrences in file_paths.items():
            if len(occurrences) > 1:
                conflicts.append({
                    'file_path': path,
                    'occurrences': [{'project': p, 'category': c} for p, c in occurrences]
                })
        
            return {
                'has_conflicts': len(conflicts) > 0,
                'conflicts': conflicts,
                'total_conflicts': len(conflicts)
            }
    
    # ==================== 数据库优化和压缩 ====================
    
    def optimize(self):
        """优化数据库（分析表和更新统计信息）"""
        with self.get_cursor() as cursor:
            cursor.execute('PRAGMA optimize')
            cursor.execute('ANALYZE')
    
    def vacuum(self):
        """压缩数据库，回收空间（需要独占访问）"""
        # 关闭当前连接
        if hasattr(_local, 'connection') and _local.connection:
            _local.connection.close()
            _local.connection = None
        
        # 创建新连接执行VACUUM
        conn = sqlite3.connect(self.db_path)
        try:
            # 关闭WAL模式以便VACUUM
            conn.execute('PRAGMA journal_mode = DELETE')
            conn.commit()
            conn.execute('VACUUM')
            # 恢复WAL模式
            conn.execute('PRAGMA journal_mode = WAL')
            conn.commit()
        finally:
            conn.close()
    
    def get_database_size(self):
        """获取数据库文件大小（字节）"""
        if os.path.exists(self.db_path):
            return os.path.getsize(self.db_path)
        return 0
    
    def get_database_stats(self):
        """获取数据库统计信息"""
        with self.get_cursor() as cursor:
            cursor.execute('PRAGMA page_count')
            page_count = cursor.fetchone()[0]
            
            cursor.execute('PRAGMA page_size')
            page_size = cursor.fetchone()[0]
            
            cursor.execute('PRAGMA freelist_count')
            freelist_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM projects')
            project_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM files')
            file_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM categories')
            category_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM folders')
            folder_count = cursor.fetchone()[0]
            
            # 获取索引信息
            cursor.execute('''
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_autoindex%'
            ''')
            indexes = [row[0] for row in cursor.fetchall()]
        
        return {
            'page_count': page_count,
            'page_size': page_size,
            'freelist_count': freelist_count,
            'estimated_size': page_count * page_size,
            'project_count': project_count,
            'file_count': file_count,
            'category_count': category_count,
            'folder_count': folder_count,
            'indexes': indexes
        }


def migrate_json_to_sqlite(json_dir, db):
    """将JSON项目文件迁移到SQLite数据库"""
    import glob
    
    json_files = glob.glob(os.path.join(json_dir, '*.json'))
    migrated = []
    failed = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            project_name = project_data.get('name', '')
            if not project_name:
                failed.append((json_file, 'Missing project name'))
                continue
            
            # 检查项目是否已存在
            if db.project_exists(project_name):
                print(f"项目 {project_name} 已存在，跳过")
                continue
            
            # 保存到数据库
            db.save_project(project_data)
            migrated.append(project_name)
            print(f"成功迁移项目: {project_name}")
            
        except Exception as e:
            failed.append((json_file, str(e)))
            print(f"迁移失败 {json_file}: {e}")
    
    return {
        'migrated': migrated,
        'failed': failed
    }

