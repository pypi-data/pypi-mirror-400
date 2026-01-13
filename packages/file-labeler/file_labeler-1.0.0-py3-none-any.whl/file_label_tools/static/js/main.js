// 主页面逻辑

let filterHistory = [];
let fileListPage = 1;
let fileListPerPage = 20;
let fileListTotalPages = 1;
let fileListCategory = '';

// 折叠/展开功能
function toggleCollapse(sectionId) {
    const section = document.getElementById(sectionId);
    const icon = document.getElementById(sectionId + 'Icon');
    
    if (section.classList.contains('show')) {
        // 折叠
        section.classList.remove('show');
        icon.textContent = '▶';
    } else {
        // 展开
        section.classList.add('show');
        icon.textContent = '▼';
        // 如果展开文件列表区域，自动加载文件列表
        if (sectionId === 'fileListSection') {
            loadFileList();
        }
    }
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadCategories();
    loadFolders();
    loadFilterHistory();
    initMergeCategorySearch();
    
    // 监听文件列表相关事件
    const fileListPerPageInput = document.getElementById('fileListPerPage');
    const fileListCategoryFilter = document.getElementById('fileListCategoryFilter');
    const fileListCurrentPageInput = document.getElementById('fileListCurrentPage');
    
    if (fileListPerPageInput) {
        fileListPerPageInput.addEventListener('change', (e) => {
            fileListPerPage = parseInt(e.target.value) || 20;
            fileListPage = 1;
            loadFileList();
        });
    }
    
    if (fileListCategoryFilter) {
        fileListCategoryFilter.addEventListener('change', (e) => {
            fileListCategory = e.target.value;
            fileListPage = 1;
            loadFileList();
        });
    }
    
    if (fileListCurrentPageInput) {
        fileListCurrentPageInput.addEventListener('change', (e) => {
            const page = parseInt(e.target.value) || 1;
            if (page >= 1 && page <= fileListTotalPages) {
                fileListPage = page;
                loadFileList();
            } else {
                e.target.value = fileListPage;
            }
        });
    }
});

let _mergeSearchInitialized = false;
function initMergeCategorySearch() {
    if (_mergeSearchInitialized) return;
    _mergeSearchInitialized = true;

    const input = document.getElementById('mergeSourceSearch');
    if (!input) return;

    input.addEventListener('input', () => {
        filterMergeSourceOptions(input.value);
    });
}

function filterMergeSourceOptions(keywordText) {
    const sourceSelect = document.getElementById('mergeSourceCategory');
    if (!sourceSelect) return;

    const raw = (keywordText || '').trim().toLowerCase();
    const keywords = raw ? raw.split(/\s+/).filter(Boolean) : [];

    Array.from(sourceSelect.options).forEach(opt => {
        const label = (opt.textContent || '').toLowerCase();
        const match = keywords.length === 0
            ? true
            : keywords.every(k => label.includes(k));

        // hidden 对 <option> 在多数浏览器可用；双保险加 style.display
        opt.hidden = !match;
        opt.style.display = match ? '' : 'none';
    });
}

function selectFilteredMergeSources() {
    const sourceSelect = document.getElementById('mergeSourceCategory');
    if (!sourceSelect) return;

    let selected = 0;
    Array.from(sourceSelect.options).forEach(opt => {
        const visible = !opt.hidden && opt.style.display !== 'none';
        if (visible && opt.value) {
            opt.selected = true;
            selected++;
        }
    });

    if (selected === 0) {
        showMessage('没有可选择的筛选结果', 'info');
    } else {
        showMessage(`已选择 ${selected} 个源类别`, 'success');
    }
}

function clearMergeSourceSelection() {
    const sourceSelect = document.getElementById('mergeSourceCategory');
    if (!sourceSelect) return;
    Array.from(sourceSelect.options).forEach(opt => { opt.selected = false; });
    showMessage('已清空源类别选择', 'info');
}

// 加载统计信息
async function loadStats() {
    if (typeof loadStatsChart === 'function') {
        await loadStatsChart();
    }
}

// 导入文件夹
async function importFolder() {
    const folderPath = document.getElementById('folderPath').value.trim();
    const keywordFilter = document.getElementById('keywordFilter').value.trim() || null;
    
    if (!folderPath) {
        showMessage('请输入文件夹路径', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/import/folder`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                path: folderPath,
                keyword_filter: keywordFilter
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(`成功导入 ${data.added_count} 个文件`, 'success');
            document.getElementById('folderPath').value = '';
            document.getElementById('keywordFilter').value = '';
            loadStats();
            loadFolders();
        } else {
            showMessage('导入失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('导入失败: ' + error.message, 'error');
    }
}

// 导入txt列表
async function importTxtList() {
    const serverPathInput = document.getElementById('txtListServerPath');
    const fileInput = document.getElementById('txtListFile');
    const serverPath = serverPathInput ? serverPathInput.value.trim() : '';
    const file = fileInput.files[0];
    
    if (!serverPath && !file) {
        showMessage('请提供服务器路径或选择上传文件', 'error');
        return;
    }
    
    const formData = new FormData();
    if (serverPath) {
        // 优先使用服务器路径
        formData.append('server_path', serverPath);
    } else {
        // 使用上传的文件
        formData.append('file', file);
    }
    
    try {
        showMessage('正在导入，请稍候...', 'info');
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/import/txt_list`, {
            method: 'POST',
            body: formData
        });
        
        // 检查响应类型
        const contentType = response.headers.get('content-type') || '';
        let data;
        
        if (contentType.includes('application/json')) {
            data = await response.json();
        } else {
            // 如果不是JSON，尝试读取文本内容
            const text = await response.text();
            console.error('服务器返回了非JSON响应:', text.substring(0, 200));
            showMessage('导入失败: 服务器返回了错误响应，请检查服务器日志', 'error');
            return;
        }
        
        if (response.ok) {
            showMessage(`成功导入 ${data.added_count} 个文件`, 'success');
            if (fileInput) fileInput.value = '';
            if (serverPathInput) serverPathInput.value = '';
            loadStats();
            loadCategories();
        } else {
            showMessage('导入失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        // 处理JSON解析错误
        if (error.message && error.message.includes('JSON')) {
            showMessage('导入失败: 服务器返回了无效的响应格式，请检查服务器日志或联系管理员', 'error');
        } else {
            showMessage('导入失败: ' + error.message, 'error');
        }
    }
}

// 导入带类别txt
async function importTxtLabeled() {
    const serverPathInput = document.getElementById('txtLabeledServerPath');
    const fileInput = document.getElementById('txtLabeledFile');
    const serverPath = serverPathInput ? serverPathInput.value.trim() : '';
    const file = fileInput.files[0];
    
    if (!serverPath && !file) {
        showMessage('请提供服务器路径或选择上传文件', 'error');
        return;
    }
    
    const formData = new FormData();
    if (serverPath) {
        // 优先使用服务器路径
        formData.append('server_path', serverPath);
    } else {
        // 使用上传的文件
        formData.append('file', file);
    }
    
    try {
        showMessage('正在导入，请稍候...', 'info');
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/import/txt_labeled`, {
            method: 'POST',
            body: formData
        });
        
        // 检查响应类型
        const contentType = response.headers.get('content-type') || '';
        let data;
        
        if (contentType.includes('application/json')) {
            data = await response.json();
        } else {
            // 如果不是JSON，尝试读取文本内容
            const text = await response.text();
            console.error('服务器返回了非JSON响应:', text.substring(0, 200));
            showMessage('导入失败: 服务器返回了错误响应，请检查服务器日志', 'error');
            return;
        }
        
        if (response.ok) {
            const msg = `成功导入 ${data.added_count} 个文件`;
            const categoryMsg = data.new_categories_count > 0 ? `，新增 ${data.new_categories_count} 个类别` : '';
            showMessage(msg + categoryMsg, 'success');
            if (fileInput) fileInput.value = '';
            if (serverPathInput) serverPathInput.value = '';
            loadStats();
            loadCategories();
        } else {
            showMessage('导入失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        // 处理JSON解析错误
        if (error.message && error.message.includes('JSON')) {
            showMessage('导入失败: 服务器返回了无效的响应格式，请检查服务器日志或联系管理员', 'error');
        } else {
            showMessage('导入失败: ' + error.message, 'error');
        }
    }
}

// 加载文件夹列表
async function loadFolders() {
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}`);
        const project = await response.json();
        
        const folderList = document.getElementById('folderList');
        if (project.folders && project.folders.length > 0) {
            folderList.innerHTML = project.folders.map(folder => `
                <li class="folder-item">
                    <div class="path">${escapeHtml(folder.path)}</div>
                    <div class="actions">
                        ${folder.keyword_filter ? `<span style="font-size: 12px; color: #7f8c8d;">过滤: ${escapeHtml(folder.keyword_filter)}</span>` : ''}
                        <button class="btn btn-secondary" onclick="rescanFolder('${escapeHtml(folder.path)}')" style="font-size: 12px; padding: 5px 10px;">二次扫描</button>
                    </div>
                </li>
            `).join('');
        } else {
            folderList.innerHTML = '<li style="color: #7f8c8d; padding: 10px;">暂无导入的文件夹</li>';
        }
    } catch (error) {
        console.error('加载文件夹列表失败:', error);
    }
}

// 二次扫描文件夹
async function rescanFolder(folderPath) {
    if (!confirm('确定要重新扫描该文件夹吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/rescan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                path: folderPath
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(`成功添加 ${data.added_count} 个新文件`, 'success');
            loadStats();
        } else {
            showMessage('扫描失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('扫描失败: ' + error.message, 'error');
    }
}

// 加载类别列表
async function loadCategories() {
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/categories`);
        const categories = await response.json();
        
        // 更新类别显示
        const categoriesList = document.getElementById('categoriesList');
        if (categories.length > 0) {
            categoriesList.innerHTML = categories.map((cat, index) => {
                // 使用 data 属性存储类别名称，避免特殊字符导致语法错误
                // 对 HTML 属性值进行转义，确保引号等特殊字符不会破坏属性
                const escapedCat = String(cat).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
                return `
                <span class="category-tag">
                    ${escapeHtml(cat)}
                    <span class="delete-btn" data-category="${escapedCat}" data-category-index="${index}">×</span>
                </span>
            `;
            }).join('');
            
            // 为所有删除按钮添加事件监听器
            categoriesList.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const category = this.getAttribute('data-category');
                    deleteCategory(category);
                });
            });
        } else {
            categoriesList.innerHTML = '<div style="color: #7f8c8d;">暂无类别</div>';
        }
        
        // 更新导出下拉框
        const exportSelect = document.getElementById('exportCategories');
        if (exportSelect) {
            // 添加"未分类"选项
            exportSelect.innerHTML = '<option value="__uncategorized__">未分类</option>' +
                categories.map(cat => 
                    `<option value="${escapeHtml(cat)}">${escapeHtml(cat)}</option>`
                ).join('');
        }
        
        // 更新文件列表类别筛选下拉框
        const fileListCategoryFilter = document.getElementById('fileListCategoryFilter');
        if (fileListCategoryFilter) {
            fileListCategoryFilter.innerHTML = '<option value="">全部</option>' +
                categories.map(cat => `<option value="${escapeHtml(cat)}">${escapeHtml(cat)}</option>`).join('');
        }

        // 更新“类别合并”下拉框（使用DOM API避免特殊字符问题）
        refreshMergeCategorySelects(categories || []);
    } catch (error) {
        console.error('加载类别列表失败:', error);
    }
}

function refreshMergeCategorySelects(categories) {
    const sourceSelect = document.getElementById('mergeSourceCategory');
    const targetSelect = document.getElementById('mergeTargetCategory');
    if (!sourceSelect || !targetSelect) return;

    // 允许选择“未分类”
    const allOptions = [{ value: '__uncategorized__', label: '未分类' }]
        .concat((categories || []).map(c => ({ value: c, label: c })));

    // 清空并重建
    sourceSelect.innerHTML = '';
    targetSelect.innerHTML = '';
    allOptions.forEach(opt => {
        const o1 = document.createElement('option');
        o1.value = opt.value;
        o1.textContent = opt.label;
        sourceSelect.appendChild(o1);

        const o2 = document.createElement('option');
        o2.value = opt.value;
        o2.textContent = opt.label;
        targetSelect.appendChild(o2);
    });

    // 默认：源预选第一个真实类别（如果有），目标=未分类之后的第一个类别
    if (categories && categories.length > 0) {
        // 多选：默认选中一个
        Array.from(sourceSelect.options).forEach(o => { o.selected = false; });
        const first = Array.from(sourceSelect.options).find(o => o.value === categories[0]);
        if (first) first.selected = true;
        targetSelect.value = categories.length > 1 ? categories[1] : '__uncategorized__';
    } else {
        Array.from(sourceSelect.options).forEach(o => { o.selected = false; });
        const unc = Array.from(sourceSelect.options).find(o => o.value === '__uncategorized__');
        if (unc) unc.selected = true;
        targetSelect.value = '__uncategorized__';
    }

    // 重新应用搜索过滤（如果用户已经输入了关键字）
    const input = document.getElementById('mergeSourceSearch');
    if (input) {
        filterMergeSourceOptions(input.value);
    }
}

async function mergeCategory() {
    const sourceSelect = document.getElementById('mergeSourceCategory');
    const targetSelect = document.getElementById('mergeTargetCategory');
    if (!sourceSelect || !targetSelect) return;

    const sources = Array.from(sourceSelect.selectedOptions || []).map(o => o.value).filter(Boolean);
    const target = targetSelect.value;

    if (!sources.length || !target) {
        showMessage('请选择源类别和目标类别', 'error');
        return;
    }

    // 过滤掉与目标相同的源类别（等价于无操作）
    const effectiveSources = sources.filter(s => s !== target);
    if (!effectiveSources.length) {
        showMessage('源类别不能全部等于目标类别', 'error');
        return;
    }

    const sourceLabel = effectiveSources.map(s => (s === '__uncategorized__' ? '未分类' : s)).join('、');
    const targetLabel = target === '__uncategorized__' ? '未分类' : target;

    if (!confirm(`确定要将“${sourceLabel}”合并到“${targetLabel}”吗？\n\n这会把源类别下的文件全部移动到目标类别，并默认删除源类别。`)) {
        return;
    }

    try {
        showMessage('正在合并，请稍候...', 'info');
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/categories/merge`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                source_categories: effectiveSources,
                target_category: target,
                delete_source: true
            })
        });

        const contentType = response.headers.get('content-type') || '';
        let data;
        if (contentType.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            console.error('服务器返回了非JSON响应:', text.substring(0, 200));
            showMessage('合并失败: 服务器返回了错误响应，请检查服务器日志', 'error');
            return;
        }

        if (response.ok) {
            const updated = data.updated_files || 0;
            showMessage(`合并成功：移动 ${updated} 个文件`, 'success');
            // 刷新类别与统计
            loadCategories();
            loadStats();
            // 如果文件列表区域展开了，也刷新一下列表
            const fileListSection = document.getElementById('fileListSection');
            if (fileListSection && fileListSection.classList.contains('show')) {
                loadFileList();
            }
        } else {
            showMessage('合并失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('合并失败: ' + error.message, 'error');
    }
}

// 添加类别
async function addCategory() {
    const categoryInput = document.getElementById('newCategory');
    const category = categoryInput.value.trim();
    
    if (!category) {
        showMessage('请输入类别名称', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/categories`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ category })
        });
        
        if (response.ok) {
            showMessage('类别添加成功', 'success');
            categoryInput.value = '';
            loadCategories();
            if (typeof loadStatsChart === 'function') {
                loadStatsChart();
            }
        } else {
            const data = await response.json();
            showMessage('添加失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('添加失败: ' + error.message, 'error');
    }
}

// 删除类别
async function deleteCategory(category) {
    if (!confirm(`确定要删除类别"${category}"吗？这将同时删除该类别下的所有文件记录。`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/categories/${encodeURIComponent(category)}`, {
            method: 'DELETE'
        });
        
        // 检查响应类型
        const contentType = response.headers.get('content-type') || '';
        let data;
        
        if (contentType.includes('application/json')) {
            data = await response.json();
        } else {
            // 如果不是JSON，尝试读取文本内容
            const text = await response.text();
            console.error('服务器返回了非JSON响应:', text.substring(0, 200));
            showMessage('删除失败: 服务器返回了错误响应，请检查服务器日志', 'error');
            return;
        }
        
        if (response.ok) {
            showMessage('类别删除成功', 'success');
            loadCategories();
            if (typeof loadStatsChart === 'function') {
                loadStatsChart();
            }
        } else {
            showMessage('删除失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        // 处理JSON解析错误
        if (error.message && error.message.includes('JSON')) {
            showMessage('删除失败: 服务器返回了无效的响应格式，请检查服务器日志或联系管理员', 'error');
        } else {
            showMessage('删除失败: ' + error.message, 'error');
        }
    }
}

// 过滤筛选文件
async function filterFiles() {
    const keyword = document.getElementById('filterKeyword').value.trim();
    
    if (!keyword) {
        showMessage('请输入关键字', 'error');
        return;
    }
    
    if (!confirm(`确定要移除包含"${keyword}"的文件记录吗？此操作不可撤销。`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/files/filter`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ keyword })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(`成功移除 ${data.removed_count} 个文件记录`, 'success');
            document.getElementById('filterKeyword').value = '';
            
            // 添加到筛选历史
            filterHistory.push({
                keyword: keyword,
                removed_count: data.removed_count,
                time: new Date().toLocaleString('zh-CN')
            });
            saveFilterHistory();
            loadFilterHistory();
            
            loadStats();
        } else {
            showMessage('筛选失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('筛选失败: ' + error.message, 'error');
    }
}

// 加载筛选历史
function loadFilterHistory() {
    const historyDiv = document.getElementById('filterHistory');
    if (filterHistory.length > 0) {
        historyDiv.innerHTML = '<div style="margin-bottom: 10px; font-weight: 500;">筛选历史:</div>' +
            filterHistory.map(item => `
                <span class="filter-history-item">
                    "${escapeHtml(item.keyword)}" - 移除 ${item.removed_count} 个文件 (${item.time})
                </span>
            `).join('');
    } else {
        historyDiv.innerHTML = '';
    }
}

// 保存筛选历史到localStorage
function saveFilterHistory() {
    try {
        localStorage.setItem(`filterHistory_${projectName}`, JSON.stringify(filterHistory));
    } catch (e) {
        console.error('保存筛选历史失败:', e);
    }
}

// 从localStorage加载筛选历史
function loadFilterHistoryFromStorage() {
    try {
        const saved = localStorage.getItem(`filterHistory_${projectName}`);
        if (saved) {
            filterHistory = JSON.parse(saved);
        }
    } catch (e) {
        console.error('加载筛选历史失败:', e);
    }
}

// 导出文件
async function exportFiles() {
    const select = document.getElementById('exportCategories');
    const selectedCategories = Array.from(select.selectedOptions).map(opt => opt.value);
    const includeExported = document.getElementById('includeExported').checked;
    const markAsExported = document.getElementById('markAsExported').checked;
    const exportLimitInput = document.getElementById('exportLimit');
    const exportLimit = exportLimitInput.value.trim() ? parseInt(exportLimitInput.value) : null;
    const randomSelect = document.getElementById('randomSelect').checked;
    
    // 如果没有选择任何类别，selectedCategories为空数组，后端会将其视为导出全部
    
    // 验证导出数量
    if (exportLimit !== null && (isNaN(exportLimit) || exportLimit < 1)) {
        showMessage('导出数量必须是大于0的整数', 'error');
        return;
    }
    
    try {
        showMessage('正在导出，请稍候...', 'info');
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/export`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                categories: selectedCategories.length > 0 ? selectedCategories : [],
                include_exported: includeExported,
                limit: exportLimit,
                random: randomSelect,
                mark_as_exported: markAsExported
            })
        });
        
        // 检查响应类型
        const contentType = response.headers.get('content-type') || '';
        
        if (response.ok && contentType.includes('text/plain')) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            
            // 从Content-Disposition头获取文件名
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'export.txt';
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1].replace(/['"]/g, '');
                }
            }
            
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            const fileCount = exportLimit || '全部';
            showMessage(`导出成功！已导出 ${fileCount} 个文件`, 'success');
        } else {
            // 尝试解析JSON错误
            try {
                const data = await response.json();
                showMessage('导出失败: ' + (data.error || '未知错误'), 'error');
            } catch (e) {
                showMessage('导出失败: 服务器返回了错误响应', 'error');
            }
        }
    } catch (error) {
        showMessage('导出失败: ' + error.message, 'error');
    }
}

// 重置导出状态
async function resetExportedStatus() {
    const select = document.getElementById('exportCategories');
    const selectedCategories = Array.from(select.selectedOptions).map(opt => opt.value);
    
    const categoryText = selectedCategories.length > 0 
        ? `选定的 ${selectedCategories.length} 个类别` 
        : '所有类别';
    
    if (!confirm(`确定要重置 ${categoryText} 的导出状态吗？这将把所有已导出的文件标记为未导出。`)) {
        return;
    }
    
    try {
        showMessage('正在重置，请稍候...', 'info');
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/reset-exported`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                categories: selectedCategories
            })
        });
        
        // 检查响应类型
        const contentType = response.headers.get('content-type') || '';
        let data;
        
        if (contentType.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            console.error('服务器返回了非JSON响应:', text.substring(0, 200));
            showMessage('重置失败: 服务器返回了错误响应，请检查服务器日志', 'error');
            return;
        }
        
        if (response.ok) {
            showMessage(`重置成功！已重置 ${data.reset_count} 个文件的导出状态`, 'success');
            // 刷新统计信息
            if (typeof loadStatsChart === 'function') {
                loadStatsChart();
            }
        } else {
            showMessage('重置失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        if (error.message && error.message.includes('JSON')) {
            showMessage('重置失败: 服务器返回了无效的响应格式，请检查服务器日志或联系管理员', 'error');
        } else {
            showMessage('重置失败: ' + error.message, 'error');
        }
    }
}

// 显示消息
function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = `message ${type} show`;
    setTimeout(() => {
        messageDiv.classList.remove('show');
    }, 3000);
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 页面加载时加载筛选历史
loadFilterHistoryFromStorage();

// ==================== 文件列表查看功能 ====================

// 加载文件列表
async function loadFileList() {
    try {
        const params = new URLSearchParams({
            page: fileListPage,
            per_page: fileListPerPage
        });
        
        if (fileListCategory) {
            params.append('category', fileListCategory);
        }
        
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/files?${params}`);
        const data = await response.json();
        
        if (response.ok) {
            fileListTotalPages = data.total_pages || 1;
            fileListPage = data.page || 1;
            
            // 更新分页显示
            const currentPageInput = document.getElementById('fileListCurrentPage');
            const totalPagesSpan = document.getElementById('fileListTotalPages');
            const totalSpan = document.getElementById('fileListTotal');
            const pagination = document.getElementById('fileListPagination');
            const prevBtn = document.getElementById('fileListPrevBtn');
            const nextBtn = document.getElementById('fileListNextBtn');
            
            if (currentPageInput) currentPageInput.value = fileListPage;
            if (totalPagesSpan) totalPagesSpan.textContent = fileListTotalPages;
            if (totalSpan) totalSpan.textContent = data.total || 0;
            if (pagination) pagination.style.display = data.total > 0 ? 'flex' : 'none';
            if (prevBtn) prevBtn.disabled = fileListPage === 1;
            if (nextBtn) nextBtn.disabled = fileListPage >= fileListTotalPages;
            
            // 显示文件列表
            displayFileList(data.files || []);
        } else {
            showMessage('加载文件列表失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('加载文件列表失败: ' + error.message, 'error');
    }
}

// 显示文件列表
function displayFileList(files) {
    const container = document.getElementById('fileListContainer');
    
    if (files.length === 0) {
        container.innerHTML = '<div class="loading">暂无文件</div>';
        return;
    }
    
    container.innerHTML = `
        <div class="file-list-table">
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">#</th>
                        <th style="width: 60%;">文件路径</th>
                        <th style="width: 15%;">类别</th>
                        <th style="width: 10%;">来源</th>
                        <th style="width: 10%;">导入时间</th>
                    </tr>
                </thead>
                <tbody>
                    ${files.map((file, index) => {
                        const fileNum = (fileListPage - 1) * fileListPerPage + index + 1;
                        const filename = file.path.split('/').pop();
                        const importDate = file.imported_at ? new Date(file.imported_at).toLocaleString('zh-CN') : '-';
                        return `
                            <tr>
                                <td>${fileNum}</td>
                                <td class="file-path" title="${escapeHtml(file.path)}">
                                    <span class="file-name">${escapeHtml(filename)}</span>
                                    <div class="file-full-path">${escapeHtml(file.path)}</div>
                                </td>
                                <td>
                                    <span class="category-badge ${file.category ? '' : 'no-category'}">
                                        ${escapeHtml(file.category || '未分类')}
                                    </span>
                                </td>
                                <td>${escapeHtml(file.source || '-')}</td>
                                <td style="font-size: 12px; color: var(--text-tertiary);">${importDate}</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// 文件列表上一页
function fileListPreviousPage() {
    if (fileListPage > 1) {
        fileListPage--;
        loadFileList();
    }
}

// 文件列表下一页
function fileListNextPage() {
    if (fileListPage < fileListTotalPages) {
        fileListPage++;
        loadFileList();
    }
}

