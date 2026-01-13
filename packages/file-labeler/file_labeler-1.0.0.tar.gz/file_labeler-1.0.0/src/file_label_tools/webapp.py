from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from werkzeug.exceptions import RequestEntityTooLarge
import os
import json
import datetime
import secrets
from pathlib import Path
from urllib.parse import unquote
import hashlib
from functools import wraps
import logging
from importlib.resources import files as resource_files

from . import config
from .database import Database, migrate_json_to_sqlite
from .paths import get_whitelist_path, get_data_dir

_pkg_root = resource_files(__package__ or "file_label_tools")
_templates_dir = str(_pkg_root / "templates")
_static_dir = str(_pkg_root / "static")

app = Flask(__name__, template_folder=_templates_dir, static_folder=_static_dir)
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024  # 约 1GB max file size

# 安全相关配置：支持用环境变量覆盖，避免把敏感信息硬编码进包里
ENV_PASSWORD = "FILE_LABELER_PASSWORD"
ENV_SECRET_KEY = "FILE_LABELER_SECRET_KEY"

_secret_key = (os.environ.get(ENV_SECRET_KEY) or "").strip()
if not _secret_key:
    # 未设置时自动生成随机值（重启后 session 会失效）
    _secret_key = secrets.token_hex(32)
app.config['SECRET_KEY'] = _secret_key  # 用于 session 加密

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'log_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}_file_label.py.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 启动时给出安全提示（不打印具体值，避免泄露）
if not (os.environ.get(ENV_SECRET_KEY) or "").strip():
    logger.warning(
        f"未设置环境变量 {ENV_SECRET_KEY}，已为本次启动自动生成随机 SECRET_KEY（重启后 session 会失效）。"
    )
if not (os.environ.get(ENV_PASSWORD) or "").strip():
    logger.warning(
        f"未设置环境变量 {ENV_PASSWORD}，将使用默认登录密码（不建议生产环境，请尽快配置）。"
    )

# 初始化数据库（写入用户可写数据目录，兼容 Windows）
db = Database(config.DATABASE_PATH)

# 白名单JSON文件路径（写入用户可写数据目录，兼容 Windows）
WHITELIST_FILE = str(get_whitelist_path())

# 错误处理器：处理文件过大错误
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    """处理文件过大错误"""
    if request.path.startswith('/api/'):
        return jsonify({'error': '上传的文件太大，请使用服务器路径方式导入，或减小文件大小'}), 413
    # 对于非API请求，返回简单的错误页面
    return '<h1>文件太大</h1><p>上传的文件太大，请使用服务器路径方式导入，或减小文件大小</p>', 413

def get_client_key():
    """获取客户端唯一标识（IP + User-Agent）"""
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    return f"{ip}_{hashlib.md5(user_agent.encode()).hexdigest()}"

def load_whitelist():
    """从JSON文件加载白名单"""
    try:
        if os.path.exists(WHITELIST_FILE):
            with open(WHITELIST_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 将字符串格式的日期时间转换回datetime对象
                whitelist = {}
                now = datetime.datetime.now()
                for key, expiry_str in data.items():
                    try:
                        expiry = datetime.datetime.fromisoformat(expiry_str)
                        # 只加载未过期的项
                        if expiry > now:
                            whitelist[key] = expiry
                    except (ValueError, TypeError):
                        # 如果日期格式无效，跳过该项
                        continue
                return whitelist
        return {}
    except Exception as e:
        logger.error(f"加载白名单失败: {str(e)}", exc_info=True)
        return {}

def save_whitelist(whitelist):
    """保存白名单到JSON文件"""
    try:
        # 清理过期项
        now = datetime.datetime.now()
        cleaned_whitelist = {k: v.isoformat() for k, v in whitelist.items() if v > now}
        
        # 保存到文件
        with open(WHITELIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(cleaned_whitelist, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存白名单失败: {str(e)}", exc_info=True)

def is_authorized():
    """检查是否在白名单中且未过期"""
    client_key = get_client_key()
    whitelist = load_whitelist()
    if client_key in whitelist:
        expiry = whitelist[client_key]
        if datetime.datetime.now() < expiry:
            return True
        else:
            # 过期了，从文件中删除
            whitelist.pop(client_key, None)
            save_whitelist(whitelist)
    return False

def add_to_whitelist():
    """将当前客户端添加到白名单，有效期1天"""
    client_key = get_client_key()
    expiry = datetime.datetime.now() + datetime.timedelta(days=1)
    whitelist = load_whitelist()
    whitelist[client_key] = expiry
    save_whitelist(whitelist)

def get_expected_password() -> str:
    """获取期望的登录密码（优先环境变量），避免硬编码敏感信息。"""
    configured = (os.environ.get(ENV_PASSWORD) or "").strip()
    if configured:
        return configured
    # 兼容旧行为：未配置时使用默认值，但会在启动时 warning
    print(f"未设置环境变量 {ENV_PASSWORD}，将使用默认登录密码 admin（不建议生产环境，请尽快配置）。")
    return "admin"

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authorized():
            # 对于API请求，返回JSON错误；对于页面请求，重定向到登录页
            if request.path.startswith('/api/'):
                return jsonify({'error': '未授权，请先登录'}), 401
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def is_image_file(filepath):
    """判断是否为图片文件"""
    ext = Path(filepath).suffix.lower()
    return ext in config.IMAGE_EXTENSIONS

def get_image_mirror_path(original_path):
    """获取图片在镜像目录中的路径"""
    # 使用文件路径的hash值作为镜像文件名，避免路径冲突
    path_hash = hashlib.md5(original_path.encode('utf-8')).hexdigest()
    file_ext = Path(original_path).suffix
    return os.path.join(config.IMAGE_MIRROR_DIR, f"{path_hash}{file_ext}")

def ensure_image_mirror(original_path):
    """确保图片在镜像目录中存在（创建符号链接或复制）"""
    mirror_path = get_image_mirror_path(original_path)
    
    # 如果镜像文件已存在，检查是否有效
    if os.path.exists(mirror_path):
        # 如果是符号链接，检查目标是否存在
        if os.path.islink(mirror_path):
            try:
                link_target = os.readlink(mirror_path)
                if os.path.exists(link_target):
                    return mirror_path
                else:
                    # 符号链接目标不存在，删除旧链接
                    print(f"符号链接目标不存在: {link_target}, 删除旧链接")
                    try:
                        os.remove(mirror_path)
                    except:
                        pass
            except Exception as e:
                print(f"读取符号链接失败: {e}")
                try:
                    os.remove(mirror_path)
                except:
                    pass
        else:
            # 普通文件，检查是否可读
            try:
                with open(mirror_path, 'rb') as f:
                    f.read(1)
                return mirror_path
            except:
                # 文件损坏，删除它
                print(f"镜像文件损坏，删除: {mirror_path}")
                try:
                    os.remove(mirror_path)
                except:
                    pass
    
    # 检查原始文件是否存在
    original_file = Path(original_path)
    if not original_file.exists():
        print(f"原始文件不存在: {original_path}")
        return None
    
    if not original_file.is_file():
        print(f"路径不是文件: {original_path}")
        return None
    
    # 检查文件是否可读
    try:
        with open(original_path, 'rb') as f:
            f.read(1)
    except Exception as e:
        print(f"原始文件不可读: {original_path}, 错误: {e}")
        return None
    
    try:
        # 创建符号链接
        if os.name == 'nt':  # Windows系统
            # Windows需要管理员权限创建符号链接，如果失败则复制文件
            try:
                os.symlink(original_path, mirror_path)
                print(f"创建符号链接成功: {mirror_path} -> {original_path}")
                return mirror_path
            except (OSError, PermissionError) as e:
                print(f"创建符号链接失败: {e}, 尝试复制文件...")
                # 如果无法创建符号链接，则复制文件
                import shutil
                shutil.copy2(original_path, mirror_path)
                print(f"复制文件成功: {original_path} -> {mirror_path}")
                return mirror_path
        else:  # Linux/Unix系统
            try:
                os.symlink(original_path, mirror_path)
                print(f"创建符号链接成功: {mirror_path} -> {original_path}")
                return mirror_path
            except (OSError, PermissionError) as e:
                print(f"创建符号链接失败: {e}, 尝试复制文件...")
                # 如果符号链接失败，尝试复制文件
                import shutil
                shutil.copy2(original_path, mirror_path)
                print(f"复制文件成功: {original_path} -> {mirror_path}")
                return mirror_path
    except Exception as e:
        print(f"创建镜像失败 {original_path}: {e}")
        # 最后尝试复制文件
        try:
            import shutil
            shutil.copy2(original_path, mirror_path)
            print(f"复制文件成功（异常处理）: {original_path} -> {mirror_path}")
            return mirror_path
        except Exception as e2:
            print(f"复制文件失败 {original_path}: {e2}")
            return None

def scan_folder(folder_path, keyword_filter=None):
    """扫描文件夹，返回文件列表"""
    files = []
    folder_path = Path(folder_path)
    if not folder_path.exists() or not folder_path.is_dir():
        return files
    
    for file_path in folder_path.rglob('*'):
        if file_path.is_file():
            file_str = str(file_path.absolute())
            if keyword_filter:
                if keyword_filter not in file_str:
                    continue
            files.append(file_str)
    return files

# ==================== 项目管理API ====================

@app.route('/api/projects', methods=['GET'])
@login_required
def get_projects():
    """获取所有项目列表"""
    projects = db.get_all_projects()
    return jsonify(projects)

@app.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    """创建新项目"""
    data = request.json
    name = data.get('name', '').strip()
    note = data.get('note', '').strip()
    
    if not name:
        return jsonify({'error': '项目名称不能为空'}), 400
    
    # 检查项目是否已存在
    if db.project_exists(name):
        return jsonify({'error': '项目已存在'}), 400
    
    project_data = db.create_project(name, note)
    return jsonify(project_data), 201

@app.route('/api/projects/<name>', methods=['GET'])
@login_required
def get_project(name):
    """获取项目详情"""
    project_data = db.load_project(name)
    if not project_data:
        return jsonify({'error': '项目不存在'}), 404
    return jsonify(project_data)

@app.route('/api/projects/<name>', methods=['PUT'])
@login_required
def update_project(name):
    """更新项目"""
    if not db.project_exists(name):
        return jsonify({'error': '项目不存在'}), 404
    
    data = request.json
    new_name = data.get('name', '').strip()
    note = data.get('note', '').strip()
    
    if not new_name:
        return jsonify({'error': '项目名称不能为空'}), 400
    
    # 如果项目名称改变，检查新名称是否已存在
    if new_name != name and db.project_exists(new_name):
        return jsonify({'error': '项目名称已存在'}), 400
    
    db.update_project_meta(name, new_name, note)
    project_data = db.load_project(new_name)
    return jsonify(project_data), 200

@app.route('/api/projects/<name>', methods=['DELETE'])
@login_required
def delete_project(name):
    """删除项目"""
    if db.delete_project(name):
        return jsonify({'message': '项目已删除'}), 200
    return jsonify({'error': '项目不存在'}), 404

@app.route('/api/projects/<name>/split', methods=['POST'])
@login_required
def split_project(name):
    """分割项目：将项目文件随机平均分割成N份，创建新项目，不影响原项目"""
    if not db.project_exists(name):
        return jsonify({'error': '项目不存在'}), 404
    
    data = request.json
    n = int(data.get('n', 2))
    
    if n < 2:
        return jsonify({'error': '分割份数必须大于等于2'}), 400
    
    # 检查分割后的项目名是否已存在
    for i in range(n):
        new_project_name = f"{name}_split_{i+1}"
        if db.project_exists(new_project_name):
            return jsonify({'error': f'项目 {new_project_name} 已存在'}), 400
    
    result = db.split_project(name, n)
    if result is None:
        return jsonify({'error': '项目中没有文件或分割失败'}), 400
    
    return jsonify({
        'message': f'成功分割成 {len(result["split_projects"])} 个项目',
        'split_projects': result['split_projects'],
        'total_files': result['total_files']
    }), 200

@app.route('/api/projects/check-conflicts', methods=['POST'])
@login_required
def check_merge_conflicts():
    """检测项目合并时的文件冲突"""
    data = request.json
    source_projects = data.get('source_projects', [])
    
    if len(source_projects) < 2:
        return jsonify({'error': '至少需要2个项目才能合并'}), 400
    
    result = db.check_merge_conflicts(source_projects)
    if result is None:
        return jsonify({'error': '部分项目不存在'}), 404
    
    return jsonify(result), 200

@app.route('/api/projects/merge', methods=['POST'])
@login_required
def merge_projects():
    """合并多个项目到一个新项目，不影响源项目"""
    data = request.json
    source_projects = data.get('source_projects', [])
    target_project = data.get('target_project', '').strip()
    conflict_resolution = data.get('conflict_resolution', 'first')  # 'first' 或 'last'
    
    if len(source_projects) < 2:
        return jsonify({'error': '至少需要2个项目才能合并'}), 400
    
    if not target_project:
        return jsonify({'error': '目标项目名称不能为空'}), 400
    
    # 检查目标项目是否已存在
    if db.project_exists(target_project):
        return jsonify({'error': f'目标项目 {target_project} 已存在'}), 400
    
    result = db.merge_projects(source_projects, target_project, conflict_resolution)
    if result is None:
        return jsonify({'error': '部分源项目不存在'}), 404
    
    return jsonify({
        'message': '项目合并成功',
        'target_project': result['target_project'],
        'total_files': result['total_files'],
        'conflict_count': result['conflict_count'],
        'source_projects': source_projects
    }), 200

@app.route('/api/projects/<name>/copy', methods=['POST'])
@login_required
def copy_project(name):
    """复制项目"""
    if not db.project_exists(name):
        return jsonify({'error': '项目不存在'}), 404
    
    data = request.json
    new_name = data.get('new_name', '').strip()
    
    if not new_name:
        return jsonify({'error': '新项目名称不能为空'}), 400
    
    # 检查新项目名是否已存在
    if db.project_exists(new_name):
        return jsonify({'error': f'项目 {new_name} 已存在'}), 400
    
    result = db.copy_project(name, new_name, f"(复制自 {name})")
    if result is None:
        return jsonify({'error': '复制失败'}), 500
    
    return jsonify({
        'message': '项目复制成功',
        'new_project': result['name'],
        'file_count': result['file_count']
    }), 200

# ==================== 文件导入API ====================

@app.route('/api/projects/<name>/import/folder', methods=['POST'])
@login_required
def import_folder(name):
    """导入文件夹"""
    if not db.project_exists(name):
        return jsonify({'error': '项目不存在'}), 404
    
    data = request.json
    folder_path = data.get('path', '').strip()
    keyword_filter = data.get('keyword_filter') or ''
    keyword_filter = keyword_filter.strip() if keyword_filter else None
    
    if not folder_path:
        return jsonify({'error': '文件夹路径不能为空'}), 400
    
    folder_path = str(Path(folder_path).absolute())
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return jsonify({'error': '文件夹不存在'}), 400
    
    # 扫描文件
    files = scan_folder(folder_path, keyword_filter)
    
    # 添加文件夹记录
    folder_info = {
        'path': folder_path,
        'keyword_filter': keyword_filter or '',
        'imported_at': datetime.datetime.now().isoformat()
    }
    db.add_folder(name, folder_info)
    
    # 添加文件记录
    now = datetime.datetime.now().isoformat()
    files_to_add = [{
        'path': file_path,
        'category': '',
        'imported_at': now,
        'source': 'folder'
    } for file_path in files]
    
    added_count = db.add_files_batch(name, files_to_add)
    
    return jsonify({'message': f'成功导入 {added_count} 个文件', 'added_count': added_count}), 200

@app.route('/api/projects/<name>/import/txt_list', methods=['POST'])
@login_required
def import_txt_list(name):
    """导入txt列表文件（支持上传文件或服务器绝对路径）"""
    try:
        if not db.project_exists(name):
            return jsonify({'error': '项目不存在'}), 404
        
        # 优先检查是否提供了服务器路径
        server_path = request.form.get('server_path', '').strip() if request.form else ''
        
        lines = []
        if server_path:
            # 从服务器绝对路径读取
            txt_path = Path(server_path)
            if not txt_path.exists() or not txt_path.is_file():
                return jsonify({'error': f'服务器文件不存在: {server_path}'}), 400
            
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f if line.strip()]
            except Exception as e:
                return jsonify({'error': f'读取文件失败: {str(e)}'}), 400
        else:
            # 从上传的文件读取
            if 'file' not in request.files:
                return jsonify({'error': '未上传文件且未提供服务器路径'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '文件名为空'}), 400
            
            try:
                content = file.read().decode('utf-8')
                lines = [line.strip() for line in content.split('\n') if line.strip()]
            except Exception as e:
                return jsonify({'error': f'读取文件失败: {str(e)}'}), 400
        
        if not lines:
            return jsonify({'error': '文件为空或没有有效行'}), 400
        
        # 获取已存在的文件路径
        existing_paths = db.get_existing_file_paths(name)
        now = datetime.datetime.now().isoformat()
        files_to_add = []
        
        for line in lines:
            file_path = Path(line)
            if not file_path.is_absolute():
                file_path = file_path.resolve()
            file_str = str(file_path)
            
            if file_str not in existing_paths:
                if file_path.exists() and file_path.is_file():
                    files_to_add.append({
                        'path': file_str,
                        'category': '',
                        'imported_at': now,
                        'source': 'txt_list'
                    })
                    existing_paths.add(file_str)
        
        added_count = db.add_files_batch(name, files_to_add)
        
        return jsonify({'message': f'成功导入 {added_count} 个文件', 'added_count': added_count}), 200
    except Exception as e:
        logger.error(f"导入txt列表文件时发生未预期的错误: {str(e)}", exc_info=True)
        return jsonify({'error': f'导入失败: {str(e)}'}), 500

@app.route('/api/projects/<name>/import/txt_labeled', methods=['POST'])
@login_required
def import_txt_labeled(name):
    """导入带类别的txt文件（支持上传文件或服务器绝对路径）"""
    try:
        logger.info(f"开始导入带类别的txt文件，项目名: {name}")
        
        if not db.project_exists(name):
            logger.error(f"项目不存在: {name}")
            return jsonify({'error': '项目不存在'}), 404
        
        # 优先检查是否提供了服务器路径
        server_path = request.form.get('server_path', '').strip() if request.form else ''
        logger.info(f"服务器路径参数: {server_path if server_path else '未提供'}")
        
        lines = []
        if server_path:
            logger.info(f"从服务器路径读取文件: {server_path}")
            txt_path = Path(server_path)
            if not txt_path.exists() or not txt_path.is_file():
                logger.error(f"服务器文件不存在: {server_path}")
                return jsonify({'error': f'服务器文件不存在: {server_path}'}), 400
            
            try:
                logger.info(f"开始读取文件: {server_path}")
                with open(txt_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f if line.strip()]
                logger.info(f"文件读取成功，共 {len(lines)} 行有效数据")
            except Exception as e:
                logger.error(f"读取文件失败: {str(e)}", exc_info=True)
                return jsonify({'error': f'读取文件失败: {str(e)}'}), 400
        else:
            logger.info("从上传的文件读取")
            if 'file' not in request.files:
                logger.error("未上传文件且未提供服务器路径")
                return jsonify({'error': '未上传文件且未提供服务器路径'}), 400
            
            file = request.files['file']
            if file.filename == '':
                logger.error("文件名为空")
                return jsonify({'error': '文件名为空'}), 400
            
            logger.info(f"上传的文件名: {file.filename}")
            try:
                content = file.read().decode('utf-8')
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                logger.info(f"文件读取成功，共 {len(lines)} 行有效数据")
            except Exception as e:
                logger.error(f"读取上传文件失败: {str(e)}", exc_info=True)
                return jsonify({'error': f'读取文件失败: {str(e)}'}), 400
        
        if not lines:
            logger.warning("文件为空或没有有效行")
            return jsonify({'error': '文件为空或没有有效行'}), 400
        
        logger.info(f"开始处理 {len(lines)} 行数据")
        
        # 获取已存在的文件路径
        existing_paths = db.get_existing_file_paths(name)
        logger.info(f"项目中已存在 {len(existing_paths)} 个文件路径")
        
        # 获取现有类别
        existing_categories = set(db.get_categories(name))
        
        files_to_add = []
        new_categories = []
        file_category_updates = {}  # {path: category} 用于更新已存在但无类别的文件
        now = datetime.datetime.now().isoformat()
        
        # 统计信息
        skipped_existing = 0
        skipped_not_found = 0
        skipped_invalid_format = 0
        
        for idx, line in enumerate(lines, 1):
            parts = line.split(' ', 1)
            if len(parts) != 2:
                skipped_invalid_format += 1
                if idx <= 5:
                    logger.warning(f"第 {idx} 行格式无效: {line[:100]}")
                continue
            
            file_path_str = parts[0].strip()
            category = parts[1].strip()
            
            file_path = Path(file_path_str)
            if not file_path.is_absolute():
                file_path = file_path.resolve()
            file_str = str(file_path)
            
            if file_str in existing_paths:
                # 文件已存在，记录需要更新类别的（如果有类别的话）
                if category:
                    file_category_updates[file_str] = category
                    if category not in existing_categories:
                        existing_categories.add(category)
                        new_categories.append(category)
                skipped_existing += 1
            else:
                if file_path.exists() and file_path.is_file():
                    if category and category not in existing_categories:
                        existing_categories.add(category)
                        new_categories.append(category)
                    
                    files_to_add.append({
                        'path': file_str,
                        'category': category,
                        'imported_at': now,
                        'source': 'txt_labeled'
                    })
                    existing_paths.add(file_str)
                else:
                    skipped_not_found += 1
                    if skipped_not_found <= 5:
                        logger.warning(f"文件不存在: {file_str}")
        
        logger.info(f"处理完成: 格式错误={skipped_invalid_format}, 已存在={skipped_existing}, 文件不存在={skipped_not_found}, 新增={len(files_to_add)}")
        
        # 添加新类别
        if new_categories:
            logger.info(f"添加 {len(new_categories)} 个新类别")
            db.add_categories(name, new_categories)
        
        # 更新已存在但无类别的文件
        updated_categories = 0
        if file_category_updates:
            updated_categories = db.update_empty_category_files(name, file_category_updates)
            logger.info(f"更新了 {updated_categories} 个已存在文件的类别")
        
        # 批量添加新文件
        added_count = db.add_files_batch(name, files_to_add)
        logger.info(f"导入完成: 新增文件 {added_count} 个")
        
        return jsonify({
            'message': f'成功导入 {added_count} 个文件，更新 {updated_categories} 个文件的类别',
            'added_count': added_count,
            'updated_categories_count': updated_categories,
            'new_categories_count': len(new_categories),
            'skipped_existing': skipped_existing,
            'skipped_not_found': skipped_not_found,
            'skipped_invalid_format': skipped_invalid_format
        }), 200
    except Exception as e:
        logger.error(f"导入带类别txt文件时发生未预期的错误: {str(e)}", exc_info=True)
        return jsonify({'error': f'导入失败: {str(e)}'}), 500

@app.route('/api/projects/<name>/rescan', methods=['POST'])
@login_required
def rescan_folder(name):
    """二次扫描文件夹"""
    if not db.project_exists(name):
        return jsonify({'error': '项目不存在'}), 404
    
    data = request.json
    folder_path = data.get('path', '').strip()
    
    if not folder_path:
        return jsonify({'error': '文件夹路径不能为空'}), 400
    
    # 查找文件夹记录
    folder_info = db.get_folder(name, folder_path)
    if not folder_info:
        return jsonify({'error': '未找到该文件夹记录'}), 404
    
    # 扫描新文件
    files = scan_folder(folder_path, folder_info.get('keyword_filter'))
    existing_paths = db.get_existing_file_paths(name)
    now = datetime.datetime.now().isoformat()
    
    files_to_add = []
    for file_path in files:
        if file_path not in existing_paths:
            files_to_add.append({
                'path': file_path,
                'category': '',
                'imported_at': now,
                'source': 'folder'
            })
    
    added_count = db.add_files_batch(name, files_to_add)
    return jsonify({'message': f'成功添加 {added_count} 个新文件', 'added_count': added_count}), 200

# ==================== 类别管理API ====================

@app.route('/api/projects/<name>/categories', methods=['GET'])
@login_required
def get_categories(name):
    """获取所有类别"""
    if not db.project_exists(name):
        return jsonify({'error': '项目不存在'}), 404
    return jsonify(db.get_categories(name))

@app.route('/api/projects/<name>/categories', methods=['POST'])
@login_required
def add_category(name):
    """添加类别"""
    if not db.project_exists(name):
        return jsonify({'error': '项目不存在'}), 404
    
    data = request.json
    category = data.get('category', '').strip()
    
    if not category:
        return jsonify({'error': '类别名称不能为空'}), 400
    
    db.add_category(name, category)
    return jsonify({'message': '类别已添加'}), 200

@app.route('/api/projects/<name>/categories/<category>', methods=['DELETE'])
@login_required
def delete_category(name, category):
    """删除类别（同时删除该类别下的文件记录）"""
    try:
        if not db.project_exists(name):
            return jsonify({'error': '项目不存在'}), 404
        
        category = unquote(category)
        
        # 删除类别
        db.delete_category(name, category)
        # 删除该类别下的文件
        db.delete_files_by_category(name, category)
        
        return jsonify({'message': '类别已删除'}), 200
    except Exception as e:
        logger.error(f"删除类别时发生未预期的错误: {str(e)}", exc_info=True)
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


@app.route('/api/projects/<name>/categories/merge', methods=['POST'])
@login_required
def merge_category(name):
    """合并类别：将一个类别合并到另一个类别中（移动文件归属，并可删除源类别）

    Request JSON:
    - source_category: 源类别（'__uncategorized__' 表示未分类）【兼容旧格式】
    - source_categories: 源类别列表（支持多选；'__uncategorized__' 表示未分类）
    - target_category: 目标类别（'__uncategorized__' 表示未分类）
    - delete_source: 是否删除源类别（默认 True；源为未分类时无效）
    """
    try:
        if not db.project_exists(name):
            return jsonify({'error': '项目不存在'}), 404

        data = request.json or {}
        source_category = (data.get('source_category') or '').strip()
        source_categories = data.get('source_categories', None)
        target_category = (data.get('target_category') or '').strip()
        delete_source = data.get('delete_source', True)

        # 兼容：如果传了 source_categories，用它；否则退化为单个 source_category
        if isinstance(source_categories, list):
            sources = [str(x).strip() for x in source_categories if str(x).strip() != '']
        else:
            sources = [source_category]

        # 统一未分类标记
        normalized_sources = []
        for c in sources:
            if c == '__uncategorized__':
                normalized_sources.append('')
            else:
                normalized_sources.append(c)
        if target_category == '__uncategorized__':
            target_category = ''

        # 去重并过滤空值（空字符串表示未分类，允许）
        # 注意：不能把 '' 过滤掉
        normalized_sources = list(dict.fromkeys(normalized_sources))
        normalized_sources = [c for c in normalized_sources if c is not None]

        if not normalized_sources:
            return jsonify({'error': '源类别不能为空'}), 400

        if all((c or '') == (target_category or '') for c in normalized_sources):
            return jsonify({'error': '源类别不能全部等于目标类别'}), 400

        # 目标类别如果为空字符串，表示合并到未分类
        if target_category and not db.category_exists(name, target_category):
            db.add_category(name, target_category)

        # 批量合并
        result = db.merge_categories(
            name,
            normalized_sources,
            target_category,
            delete_source=bool(delete_source)
        )
        if result is None:
            return jsonify({'error': '合并失败'}), 500

        source_label = '、'.join([(c if c else '未分类') for c in normalized_sources])
        target_label = target_category if target_category else '未分类'

        return jsonify({
            'message': f'合并完成："{source_label}" -> "{target_label}"',
            'updated_files': result.get('updated_files', 0),
            'deleted_source_categories': result.get('deleted_source_categories', 0),
            'source_categories': normalized_sources,
            'target_category': target_category
        }), 200
    except Exception as e:
        logger.error(f"合并类别时发生未预期的错误: {str(e)}", exc_info=True)
        return jsonify({'error': f'合并失败: {str(e)}'}), 500

# ==================== 文件管理API ====================

@app.route('/api/projects/<name>/files', methods=['GET'])
@login_required
def get_files(name):
    """获取文件列表（支持分页、筛选）"""
    if not db.project_exists(name):
        return jsonify({'error': '项目不存在'}), 404
    
    category_filter = request.args.get('category', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    # 兼容“未分类”筛选：前端传 __uncategorized__
    if category_filter == '__uncategorized__':
        category_arg = ''
    else:
        category_arg = category_filter or None

    result = db.get_files(name, category_arg, page, per_page)
    return jsonify(result)

@app.route('/api/projects/<name>/stats', methods=['GET'])
@login_required
def get_stats(name):
    """获取统计信息"""
    if not db.project_exists(name):
        return jsonify({'error': '项目不存在'}), 404
    
    stats = db.get_stats(name)
    return jsonify(stats)

@app.route('/api/projects/<name>/files/label', methods=['POST'])
@login_required
def label_files(name):
    """标注文件（单个或批量）"""
    if not db.project_exists(name):
        return jsonify({'error': '项目不存在'}), 404
    
    data = request.json
    file_paths = data.get('file_paths', [])
    category = data.get('category', '').strip()
    
    if not file_paths:
        return jsonify({'error': '文件路径列表不能为空'}), 400
    
    # 如果类别不在类别列表中，自动添加
    if category and not db.category_exists(name, category):
        db.add_category(name, category)
    
    # 批量更新文件类别
    updated_count = db.update_files_category_batch(name, file_paths, category)
    
    return jsonify({'message': f'成功标注 {updated_count} 个文件', 'updated_count': updated_count}), 200

@app.route('/api/projects/<name>/files/filter', methods=['POST'])
@login_required
def filter_files(name):
    """过滤筛选文件（移除包含指定关键字的文件记录）"""
    if not db.project_exists(name):
        return jsonify({'error': '项目不存在'}), 404
    
    data = request.json
    keyword = data.get('keyword', '').strip()
    
    if not keyword:
        return jsonify({'error': '关键字不能为空'}), 400
    
    removed_count = db.delete_files_by_keyword(name, keyword)
    
    return jsonify({
        'message': f'成功移除 {removed_count} 个文件记录',
        'removed_count': removed_count
    }), 200

# ==================== 图片预览API ====================

@app.route('/api/projects/<name>/images', methods=['GET'])
@login_required
def get_images(name):
    """获取图片列表（分页、类别筛选）"""
    if not db.project_exists(name):
        return jsonify({'error': '项目不存在'}), 404
    
    category_filter = request.args.get('category', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    # 兼容“未分类”筛选：前端传 __uncategorized__
    if category_filter == '__uncategorized__':
        category_arg = ''
    else:
        category_arg = category_filter or None

    result = db.get_image_files(name, config.IMAGE_EXTENSIONS, category_arg, page, per_page)
    return jsonify(result)

@app.route('/api/projects/<name>/image/<path:filepath>', methods=['GET'])
@login_required
def get_image(name, filepath):
    """获取图片文件"""
    if not db.project_exists(name):
        return jsonify({'error': '项目不存在'}), 404
    
    # 验证文件路径
    filepath = unquote(filepath)
    # 如果路径不是以/开头，说明是绝对路径但被Flask路由去掉了开头的斜杠，需要补上
    if not filepath.startswith('/'):
        filepath = '/' + filepath
    file_path = Path(filepath)
    
    if not is_image_file(filepath):
        return jsonify({'error': '不是图片文件'}), 400
    
    # 首先检查镜像目录中是否已有该文件的镜像
    mirror_path = get_image_mirror_path(filepath)
    if os.path.exists(mirror_path):
        try:
            # 如果是符号链接，检查目标是否存在
            if os.path.islink(mirror_path):
                link_target = os.readlink(mirror_path)
                if os.path.exists(link_target):
                    return send_file(mirror_path, mimetype='image/jpeg')
                else:
                    # 符号链接目标不存在，删除旧链接
                    print(f"符号链接目标不存在: {link_target}, 删除旧链接")
                    try:
                        os.remove(mirror_path)
                    except:
                        pass
            else:
                # 普通文件，直接返回
                return send_file(mirror_path, mimetype='image/jpeg')
        except Exception as e:
            print(f"访问镜像文件失败 {mirror_path}: {e}")
            # 镜像文件损坏，删除它
            try:
                os.remove(mirror_path)
            except:
                pass
    
    # 检查原始文件是否存在
    if file_path.exists() and file_path.is_file():
        # 尝试直接访问原始文件
        try:
            return send_file(filepath, mimetype='image/jpeg')
        except Exception as e:
            print(f"直接访问文件失败 {filepath}: {e}, 尝试创建镜像...")
            # 如果直接访问失败，创建镜像
            mirror_path = ensure_image_mirror(filepath)
            if mirror_path and os.path.exists(mirror_path):
                try:
                    return send_file(mirror_path, mimetype='image/jpeg')
                except Exception as e2:
                    print(f"访问新创建的镜像文件失败 {mirror_path}: {e2}")
    else:
        # 文件不存在，尝试创建镜像（可能文件在其他位置）
        print(f"原始文件不存在: {filepath}, 尝试创建镜像...")
        mirror_path = ensure_image_mirror(filepath)
        if mirror_path and os.path.exists(mirror_path):
            try:
                return send_file(mirror_path, mimetype='image/jpeg')
            except Exception as e:
                print(f"访问镜像文件失败 {mirror_path}: {e}")
    
    # 如果都失败，返回404
    return jsonify({'error': f'文件不存在或无法访问: {filepath}'}), 404

# ==================== 导出API ====================

@app.route('/api/projects/<name>/export', methods=['POST'])
@login_required
def export_files(name):
    """导出文件
    
    支持参数：
    - categories: 类别列表，空列表表示全部，['__uncategorized__'] 或 [''] 表示仅导出未分类
    - include_exported: 是否包含已导出的文件，默认True
    - limit: 导出数量限制，None表示不限制
    - random: 是否随机选择，默认True
    - mark_as_exported: 是否标记为已导出，默认True（导出未分类时建议设为False）
    """
    try:
        if not db.project_exists(name):
            return jsonify({'error': '项目不存在'}), 404
        
        data = request.json
        categories = data.get('categories', [])  # 空列表表示全部
        include_exported = data.get('include_exported', True)  # 是否包含已导出的文件
        limit = data.get('limit', None)  # 导出数量限制，None表示不限制
        random_select = data.get('random', True)  # 是否随机选择，默认True
        mark_as_exported = data.get('mark_as_exported', True)  # 是否标记为已导出，默认True
        
        # 根据类别获取文件
        if categories:
            files = db.get_files_by_categories(name, categories, include_exported=include_exported)
        else:
            files = db.get_all_files(name, include_exported=include_exported)
        
        # 随机选择
        if random_select and len(files) > 0:
            import random
            if limit and limit < len(files):
                files = random.sample(files, limit)
            else:
                random.shuffle(files)
        elif limit and limit < len(files):
            # 如果不随机，只取前limit个
            files = files[:limit]
        
        if not files:
            return jsonify({'error': '没有符合条件的文件可导出'}), 400
        
        # 生成导出内容
        content = '\n'.join([f['path'] for f in files])
        
        # 生成文件名（包含数量）
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_count = len(files)
        # 如果是导出未分类，在文件名中标注
        is_uncategorized = categories and ('' in categories or '__uncategorized__' in categories)
        uncategorized_tag = '_未分类' if is_uncategorized else ''
        filename = f"{name}{uncategorized_tag}_{file_count}files_{timestamp}.txt"
        
        # 获取文件ID列表，用于标记为已导出
        file_ids = [f['id'] for f in files if 'id' in f]
        
        # 创建临时文件
        import tempfile
        import atexit
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
        temp_file.write(content)
        temp_file.close()
        temp_path = temp_file.name
        
        # 根据参数决定是否标记文件为已导出
        if mark_as_exported and file_ids:
            db.mark_files_as_exported(name, file_ids)
        
        # 注册清理函数
        def cleanup():
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
        
        atexit.register(cleanup)
        
        return send_file(temp_path, as_attachment=True, download_name=filename, mimetype='text/plain')
    except Exception as e:
        logger.error(f"导出文件时发生未预期的错误: {str(e)}", exc_info=True)
        return jsonify({'error': f'导出失败: {str(e)}'}), 500

@app.route('/api/projects/<name>/reset-exported', methods=['POST'])
@login_required
def reset_exported(name):
    """重置导出状态（将所有已导出文件标记为未导出）"""
    try:
        if not db.project_exists(name):
            return jsonify({'error': '项目不存在'}), 404
        
        data = request.json or {}
        categories = data.get('categories', [])  # 空列表表示全部类别
        
        # 重置导出状态
        reset_count = db.reset_exported_status(name, categories)
        
        return jsonify({
            'message': f'成功重置 {reset_count} 个文件的导出状态',
            'reset_count': reset_count
        }), 200
    except Exception as e:
        logger.error(f"重置导出状态时发生未预期的错误: {str(e)}", exc_info=True)
        return jsonify({'error': f'重置失败: {str(e)}'}), 500

# ==================== 数据迁移API ====================

@app.route('/api/migrate', methods=['POST'])
@login_required
def migrate_data():
    """将JSON数据迁移到SQLite数据库"""
    result = migrate_json_to_sqlite(config.PROJECTS_DIR, db)
    return jsonify({
        'message': f'迁移完成，成功: {len(result["migrated"])} 个，失败: {len(result["failed"])} 个',
        'migrated': result['migrated'],
        'failed': result['failed']
    }), 200

# ==================== 数据库优化API ====================

@app.route('/api/database/stats', methods=['GET'])
@login_required
def get_database_stats():
    """获取数据库统计信息"""
    stats = db.get_database_stats()
    size = db.get_database_size()
    
    return jsonify({
        'size': size,
        'size_mb': size / 1024 / 1024,
        **stats
    })

@app.route('/api/database/optimize', methods=['POST'])
@login_required
def optimize_database():
    """优化数据库（分析表和更新统计信息）"""
    try:
        db.optimize()
        stats = db.get_database_stats()
        size = db.get_database_size()
        
        return jsonify({
            'message': '数据库优化完成',
            'size': size,
            'size_mb': size / 1024 / 1024,
            **stats
        }), 200
    except Exception as e:
        logger.error(f"数据库优化失败: {e}", exc_info=True)
        return jsonify({'error': f'优化失败: {str(e)}'}), 500

@app.route('/api/database/vacuum', methods=['POST'])
@login_required
def vacuum_database():
    """压缩数据库（需要独占访问，可能较慢）"""
    try:
        size_before = db.get_database_size()
        db.vacuum()
        size_after = db.get_database_size()
        
        saved = size_before - size_after if size_before > size_after else 0
        
        return jsonify({
            'message': '数据库压缩完成',
            'size_before': size_before,
            'size_before_mb': size_before / 1024 / 1024,
            'size_after': size_after,
            'size_after_mb': size_after / 1024 / 1024,
            'saved': saved,
            'saved_mb': saved / 1024 / 1024 if saved > 0 else 0
        }), 200
    except Exception as e:
        logger.error(f"数据库压缩失败: {e}", exc_info=True)
        return jsonify({'error': f'压缩失败: {str(e)}'}), 500

# ==================== 授权相关API ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        if password == get_expected_password():
            add_to_whitelist()
            session['authorized'] = True
            # 重定向到原始请求的页面，如果没有则重定向到首页
            next_page = request.args.get('next', '/')
            return redirect(next_page)
        else:
            return render_template('login.html', error='密码错误')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """登出"""
    client_key = get_client_key()
    whitelist = load_whitelist()
    if client_key in whitelist:
        del whitelist[client_key]
        save_whitelist(whitelist)
    session.pop('authorized', None)
    return redirect(url_for('login'))

# ==================== 页面路由 ====================

@app.route('/')
@login_required
def index():
    """项目选择页面"""
    return render_template('index.html')

@app.route('/project/<name>')
@login_required
def project_main(name):
    """主页面"""
    return render_template('main.html', project_name=name)

@app.route('/project/<name>/label')
@login_required
def project_label(name):
    """标注页面"""
    return render_template('label.html', project_name=name)

@app.route('/project/<name>/preview')
@login_required
def project_preview(name):
    """预览页面"""
    return render_template('preview.html', project_name=name)

# 应用启动时初始化白名单
def init_whitelist():
    """初始化白名单，清理过期项"""
    whitelist = load_whitelist()
    save_whitelist(whitelist)  # 保存时会自动清理过期项
    logger.info(f"白名单初始化完成，当前有效项数: {len(whitelist)}")

# 在应用启动时初始化
init_whitelist()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=17007)
