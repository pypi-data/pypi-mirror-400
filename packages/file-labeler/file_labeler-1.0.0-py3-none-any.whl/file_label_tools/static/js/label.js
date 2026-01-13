// 标注页面逻辑

let currentPage = 1;
let perPage = 20;
let totalPages = 1;
let currentCategory = '';
let selectedImages = new Set();
let currentPreviewPath = '';
let currentImages = []; // 保存当前页的图片数据
let imageSize = 2; // 图片大小级别：0=small, 1=medium, 2=large, 3=xlarge, 4=xxlarge
const imageSizeNames = ['很小', '小', '中等', '大', '超大'];
const imageSizeGrids = ['small', 'medium', 'large', 'xlarge', 'xxlarge'];

const LS_CATEGORY_FILTER_KEY = `label_categoryFilter_${projectName}`;
const LS_LABEL_CATEGORY_KEY = `label_labelCategory_${projectName}`;

// 行全选按钮：重新计算并渲染
function addRowSelectButtons() {
    const grid = document.getElementById('imagesGrid');
    if (!grid) return;

    // 清理旧按钮
    grid.querySelectorAll('.select-row-btn').forEach(btn => btn.remove());

    const items = Array.from(grid.querySelectorAll('.image-item'));
    if (items.length === 0) return;

    // 按 offsetTop 分组为“行”（允许少量像素误差）
    const rows = [];
    const tolerance = 3;
    for (const item of items) {
        const top = item.offsetTop;
        let row = rows.find(r => Math.abs(r.top - top) <= tolerance);
        if (!row) {
            row = { top, items: [] };
            rows.push(row);
        }
        row.items.push(item);
    }
    rows.sort((a, b) => a.top - b.top);

    function decodePathFromItem(itemEl) {
        const encoded = itemEl.getAttribute('data-full-path');
        if (!encoded) return '';
        try {
            return decodeURIComponent(atob(encoded));
        } catch (e) {
            return '';
        }
    }

    for (const row of rows) {
        // 找到本行最右侧图片项
        const rightMost = row.items.reduce((best, cur) => {
            if (!best) return cur;
            return cur.offsetLeft > best.offsetLeft ? cur : best;
        }, null);
        if (!rightMost) continue;

        const rowPaths = row.items.map(decodePathFromItem).filter(Boolean);
        if (rowPaths.length === 0) continue;

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'select-row-btn';
        btn.title = '本行全选/取消';

        const updateBtnText = () => {
            const allSelected = rowPaths.every(p => selectedImages.has(p));
            btn.textContent = allSelected ? '取消本行' : '全选本行';
        };
        updateBtnText();

        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const allSelected = rowPaths.every(p => selectedImages.has(p));
            if (allSelected) {
                rowPaths.forEach(p => selectedImages.delete(p));
            } else {
                rowPaths.forEach(p => selectedImages.add(p));
            }
            updateSelectedCount();
            rowPaths.forEach(p => updateImageSelection(p));
            updateBtnText();
        });

        rightMost.appendChild(btn);
    }
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    // 恢复上次选择：默认未分类
    try {
        currentCategory = localStorage.getItem(LS_CATEGORY_FILTER_KEY) || '__uncategorized__';
    } catch (e) {
        currentCategory = '__uncategorized__';
    }

    loadCategories();
    loadImageSizeSetting();
    loadImages();
    
    // 监听每页数量变化
    document.getElementById('perPage').addEventListener('change', (e) => {
        perPage = parseInt(e.target.value) || 20;
        currentPage = 1;
        loadImages();
    });
    
    // 监听类别筛选变化
    document.getElementById('categoryFilter').addEventListener('change', (e) => {
        currentCategory = e.target.value;
        try {
            localStorage.setItem(LS_CATEGORY_FILTER_KEY, currentCategory);
        } catch (err) {
            // ignore
        }
        currentPage = 1;
        loadImages();
    });

    // 记住“选择类别”（批量标注）
    const labelSelect = document.getElementById('labelCategory');
    if (labelSelect) {
        labelSelect.addEventListener('change', (e) => {
            try {
                localStorage.setItem(LS_LABEL_CATEGORY_KEY, e.target.value);
            } catch (err) {
                // ignore
            }
        });
    }
    
    // 监听页码输入
    document.getElementById('currentPage').addEventListener('change', (e) => {
        const page = parseInt(e.target.value) || 1;
        if (page >= 1 && page <= totalPages) {
            currentPage = page;
            loadImages();
        } else {
            e.target.value = currentPage;
        }
    });

    // 窗口尺寸变化可能导致换行变化，需要重算“行全选”按钮
    window.addEventListener('resize', () => {
        requestAnimationFrame(() => addRowSelectButtons());
    });
});

// 加载类别列表
async function loadCategories() {
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/categories`);
        const categories = await response.json();
        
        // 更新筛选下拉框
        const filterSelect = document.getElementById('categoryFilter');
        filterSelect.innerHTML =
            '<option value="">全部</option>' +
            '<option value="__uncategorized__">未分类</option>' +
            categories.map(cat => `<option value="${escapeHtml(cat)}">${escapeHtml(cat)}</option>`).join('');
        // 恢复选择
        filterSelect.value = currentCategory || '';
        
        // 更新标注下拉框
        const labelSelect = document.getElementById('labelCategory');
        labelSelect.innerHTML = '<option value="">未分类</option>' +
            categories.map(cat => `<option value="${escapeHtml(cat)}">${escapeHtml(cat)}</option>`).join('');
        // 恢复选择
        try {
            const savedLabel = localStorage.getItem(LS_LABEL_CATEGORY_KEY);
            if (savedLabel !== null) {
                labelSelect.value = savedLabel;
            }
        } catch (e) {
            // ignore
        }
        
        // 更新预览标注下拉框
        const previewSelect = document.getElementById('previewLabelCategory');
        previewSelect.innerHTML = '<option value="">未分类</option>' +
            categories.map(cat => `<option value="${escapeHtml(cat)}">${escapeHtml(cat)}</option>`).join('');
    } catch (error) {
        console.error('加载类别列表失败:', error);
    }
}

// 加载图片列表
async function loadImages() {
    try {
        const params = new URLSearchParams({
            page: currentPage,
            per_page: perPage
        });
        
        if (currentCategory) {
            params.append('category', currentCategory);
        }
        
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/images?${params}`);
        const data = await response.json();
        
        totalPages = data.total_pages || 1;
        currentPage = data.page || 1;
        
        // 更新分页显示
        document.getElementById('currentPage').value = currentPage;
        document.getElementById('totalPages').textContent = totalPages;
        document.getElementById('prevBtn').disabled = currentPage === 1;
        document.getElementById('nextBtn').disabled = currentPage >= totalPages;
        
        // 保存当前图片数据
        currentImages = data.images || [];
        // 显示图片
        displayImages(currentImages);
        // 更新选中数量
        updateSelectedCount();
    } catch (error) {
        console.error('加载图片列表失败:', error);
        showMessage('加载图片失败: ' + error.message, 'error');
    }
}

// 显示图片
function displayImages(images) {
    const grid = document.getElementById('imagesGrid');
    
    // 设置网格样式
    const sizeName = imageSizeGrids[imageSize];
    grid.className = `images-grid images-grid-${sizeName}`;
    
    if (images.length === 0) {
        grid.innerHTML = '<div class="loading">暂无图片</div>';
        return;
    }
    
    grid.innerHTML = images.map(image => {
        const isSelected = selectedImages.has(image.path);
        const imageUrl = `/api/projects/${encodeURIComponent(projectName)}/image/${encodeURIComponent(image.path)}`;
        const filename = image.path.split('/').pop();
        const pathHash = btoa(encodeURIComponent(image.path)).replace(/[+/=]/g, '').substring(0, 16);
        // 使用base64编码路径，避免特殊字符问题
        const encodedPath = btoa(encodeURIComponent(image.path));
        return `
            <div class="image-item ${isSelected ? 'selected' : ''}" 
                 data-path="${pathHash}"
                 data-full-path="${encodedPath}"
                 data-filename="${btoa(encodeURIComponent(filename))}">
                <input type="checkbox" class="checkbox" data-path="${pathHash}" ${isSelected ? 'checked' : ''}>
                <div class="image-wrapper">
                    <img src="${imageUrl}" alt="${escapeHtml(filename)}" 
                         onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22%3E%3Ctext x=%2250%22 y=%2250%22 text-anchor=%22middle%22%3E图片加载失败%3C/text%3E%3C/svg%3E'">
                    ${image.category ? `<div class="image-category-overlay">${escapeHtml(image.category)}</div>` : ''}
                </div>
            </div>
        `;
    }).join('');
    
    // 绑定事件监听器
    grid.querySelectorAll('.image-item').forEach((item) => {
        const encodedPath = item.getAttribute('data-full-path');
        const encodedFilename = item.getAttribute('data-filename');
        
        if (!encodedPath) {
            console.warn('图片项缺少data-full-path属性');
            return;
        }
        
        // 在闭包中保存路径，避免循环变量问题
        let path, filename;
        try {
            path = decodeURIComponent(atob(encodedPath));
            filename = encodedFilename ? decodeURIComponent(atob(encodedFilename)) : '';
        } catch (e) {
            console.error('解码路径失败:', e, encodedPath);
            return;
        }
        
        // 验证路径是否正确解码
        if (!path || path.length === 0) {
            console.warn('路径解码为空:', encodedPath);
            return;
        }
        
        // 点击图片选中 - 使用立即执行函数创建闭包
        const imageWrapper = item.querySelector('.image-wrapper');
        if (imageWrapper) {
            // 将路径存储在元素上，确保每个元素都有正确的路径
            imageWrapper.setAttribute('data-image-path', encodedPath);
            (function(p, encoded) {
                imageWrapper.addEventListener('click', function(e) {
                    e.stopPropagation();
                    e.preventDefault();
                    console.log('点击图片，编码路径:', encoded.substring(0, 30) + '...', '解码路径:', p.substring(0, 50) + '...');
                    selectImage(p);
                });
            })(path, encodedPath);
        }
        
        // 点击复选框选中 - 使用立即执行函数创建闭包
        const checkbox = item.querySelector('.checkbox');
        if (checkbox) {
            (function(p) {
                checkbox.addEventListener('click', function(e) {
                    e.stopPropagation();
                    selectImage(p);
                });
            })(path);
        }
    });

    // 行全选按钮（需在 DOM 布局完成后计算）
    requestAnimationFrame(() => addRowSelectButtons());
}

// 选中图片（点击默认选中，已选中的点击取消选中）
function selectImage(path) {
    if (!path) {
        console.error('selectImage: 路径为空');
        return;
    }
    
    console.log('selectImage 被调用，路径:', path.substring(0, 50) + '...', '当前选中数量:', selectedImages.size);
    
    if (selectedImages.has(path)) {
        selectedImages.delete(path);
        console.log('取消选中:', path.substring(0, 50) + '...');
    } else {
        selectedImages.add(path);
        console.log('选中:', path.substring(0, 50) + '...');
    }
    updateSelectedCount();
    updateImageSelection(path);
}

// 更新单个图片的选中状态显示
function updateImageSelection(path) {
    if (!path) {
        console.error('updateImageSelection: 路径为空');
        return;
    }
    
    // 使用完整的编码路径来查找元素，避免hash冲突
    const encodedPath = btoa(encodeURIComponent(path));
    const items = document.querySelectorAll('.image-item[data-full-path]');
    let found = false;
    
    items.forEach(item => {
        const itemEncodedPath = item.getAttribute('data-full-path');
        if (itemEncodedPath === encodedPath) {
            found = true;
            const checkbox = item.querySelector('.checkbox');
            const isSelected = selectedImages.has(path);
            if (checkbox) {
                checkbox.checked = isSelected;
            }
            if (isSelected) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        }
    });
    
    if (!found) {
        console.warn('未找到对应的图片项，路径:', path.substring(0, 50) + '...', '编码:', encodedPath.substring(0, 30) + '...');
    }
}

// 更新选中数量显示
function updateSelectedCount() {
    const countElement = document.getElementById('selectedCount');
    if (countElement) {
        countElement.textContent = selectedImages.size;
    }
}

// 全选
function selectAll() {
    // 将当前页的所有图片添加到选中集合
    currentImages.forEach(image => {
        selectedImages.add(image.path);
    });
    updateSelectedCount();
    // 更新所有图片的选中状态显示
    currentImages.forEach(image => {
        updateImageSelection(image.path);
    });
}

// 取消全选
function deselectAll() {
    // 清除当前页的选中状态
    currentImages.forEach(image => {
        selectedImages.delete(image.path);
    });
    updateSelectedCount();
    // 更新所有图片的选中状态显示
    currentImages.forEach(image => {
        updateImageSelection(image.path);
    });
}

// 减小图片大小
function decreaseImageSize() {
    if (imageSize > 0) {
        imageSize--;
        applyImageSize();
    }
}

// 增大图片大小
function increaseImageSize() {
    if (imageSize < imageSizeNames.length - 1) {
        imageSize++;
        applyImageSize();
    }
}

// 应用图片大小设置
function applyImageSize() {
    const sizeName = imageSizeGrids[imageSize];
    // 更新图片网格样式
    const grid = document.getElementById('imagesGrid');
    grid.className = `images-grid images-grid-${sizeName}`;
    // 更新显示文本
    const sizeDisplay = document.getElementById('imageSizeDisplay');
    if (sizeDisplay) {
        sizeDisplay.textContent = imageSizeNames[imageSize];
    }
    // 保存到localStorage
    try {
        localStorage.setItem(`imageSize_${projectName}`, imageSize.toString());
    } catch (e) {
        console.error('保存图片大小设置失败:', e);
    }

    // 图片大小变化会影响每行列数，需要重算“行全选”按钮
    requestAnimationFrame(() => addRowSelectButtons());
}

// 加载图片大小设置
function loadImageSizeSetting() {
    try {
        const savedSize = localStorage.getItem(`imageSize_${projectName}`);
        if (savedSize !== null) {
            const size = parseInt(savedSize);
            if (size >= 0 && size < imageSizeNames.length) {
                imageSize = size;
            }
        }
        applyImageSize();
    } catch (e) {
        console.error('加载图片大小设置失败:', e);
    }
}

// 标注选中的图片
async function labelSelected() {
    if (selectedImages.size === 0) {
        showMessage('请先选择要标注的图片', 'error');
        return;
    }
    
    const category = document.getElementById('labelCategory').value;
    
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/files/label`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_paths: Array.from(selectedImages),
                category: category
            })
        });
        
        if (response.ok) {
            showMessage('标注成功', 'success');
            // 清除已标注的图片的选中状态
            const labeledPaths = Array.from(selectedImages);
            labeledPaths.forEach(path => {
                selectedImages.delete(path);
            });
            updateSelectedCount();

            // 不整页刷新列表：本地更新当前页显示
            // - 若当前筛选为“未分类”且标注为非空类别，则这些图片应从列表消失
            // - 否则更新覆盖层类别文本
            const shouldRemoveFromView = (currentCategory === '__uncategorized__' && category && category.trim() !== '');
            if (shouldRemoveFromView) {
                currentImages = currentImages.filter(img => !labeledPaths.includes(img.path));
                displayImages(currentImages);
            } else {
                // 更新当前页数据
                currentImages.forEach(img => {
                    if (labeledPaths.includes(img.path)) {
                        img.category = category;
                    }
                });
                displayImages(currentImages);
            }

            // 如果可能新增了类别（输入了新类别），再刷新类别下拉框，但不影响当前选择
            loadCategories();
        } else {
            const data = await response.json();
            showMessage('标注失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('标注失败: ' + error.message, 'error');
    }
}

// 上一页
function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        loadImages();
    }
}

// 下一页
function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        loadImages();
    }
}

// 打开图片预览

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

