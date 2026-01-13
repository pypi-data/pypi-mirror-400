// 预览页面逻辑

let currentImageIndex = 0;
let images = [];
let allImages = []; // 保存所有图片（未筛选）
let filteredImages = []; // 筛选后的图片
let categories = [];
let keyBindings = {
    'ArrowUp': '',
    'ArrowDown': '',
    'ArrowLeft': '',
    'ArrowRight': ''
};
let currentCategory = '';
let currentFilterCategory = ''; // 当前筛选的类别，默认为空（未分类）
let labeledCount = 0;
let preloadedImages = new Map(); // 预加载的图片缓存

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
    loadKeyBindings();
    loadImages();
    setupKeyboardListeners();
    
    // 绑定类别选择变化事件
    document.querySelectorAll('.key-category-select').forEach(select => {
        select.addEventListener('change', (e) => {
            const key = e.target.getAttribute('data-key');
            keyBindings[key] = e.target.value;
            saveKeyBindings();
        });
    });
    
    // 绑定类别筛选变化事件
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', (e) => {
            currentFilterCategory = e.target.value;
            filterImages();
        });
    }
});

// 加载类别列表
async function loadCategories() {
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/categories`);
        categories = await response.json();
        
        // 更新所有类别选择框
        document.querySelectorAll('.key-category-select').forEach(select => {
            const currentValue = select.value;
            select.innerHTML = '<option value="">未分类</option>';
            categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat;
                option.textContent = cat;
                select.appendChild(option);
            });
            select.value = currentValue;
        });
        
        // 更新类别筛选下拉框
        const categoryFilter = document.getElementById('categoryFilter');
        if (categoryFilter) {
            const currentFilterValue = categoryFilter.value;
            categoryFilter.innerHTML = '<option value="">未分类</option><option value="__all__">全部</option>';
            categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat;
                option.textContent = cat;
                categoryFilter.appendChild(option);
            });
            categoryFilter.value = currentFilterValue || '';
        }
    } catch (error) {
        console.error('加载类别失败:', error);
        showMessage('加载类别失败: ' + error.message, 'error');
    }
}

// 加载按键绑定设置
function loadKeyBindings() {
    const saved = localStorage.getItem(`keyBindings_${projectName}`);
    if (saved) {
        try {
            keyBindings = JSON.parse(saved);
            // 更新UI
            Object.keys(keyBindings).forEach(key => {
                const select = document.querySelector(`.key-category-select[data-key="${key}"]`);
                if (select) {
                    select.value = keyBindings[key];
                }
            });
        } catch (e) {
            console.error('加载按键绑定失败:', e);
        }
    }
}

// 保存按键绑定设置
function saveKeyBindings() {
    localStorage.setItem(`keyBindings_${projectName}`, JSON.stringify(keyBindings));
}

// 筛选图片
function filterImages() {
    if (currentFilterCategory === '__all__') {
        // 显示全部
        filteredImages = [...allImages];
    } else if (currentFilterCategory === '') {
        // 显示未分类（空类别）
        filteredImages = allImages.filter(img => !img.category || img.category.trim() === '');
    } else {
        // 显示指定类别
        filteredImages = allImages.filter(img => img.category === currentFilterCategory);
    }
    
    images = filteredImages;
    
    // 重置当前索引
    currentImageIndex = 0;
    
    // 清空预加载缓存
    preloadedImages.clear();
    
    if (images.length === 0) {
        document.getElementById('previewContent').innerHTML = '<div class="no-images">暂无图片</div>';
        updateStats();
        return;
    }
    
    displayCurrentImage();
    updateStats();
}

// 加载图片列表（获取所有图片）
async function loadImages() {
    try {
        // 清空预加载缓存
        preloadedImages.clear();
        
        // 获取所有图片，不分页
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/images?per_page=10000`);
        const data = await response.json();
        allImages = data.images || [];
        
        // 如果总数大于当前返回的数量，需要获取更多
        if (data.total > allImages.length) {
            // 获取剩余图片
            const remainingPages = Math.ceil((data.total - allImages.length) / 10000);
            for (let page = 2; page <= remainingPages + 1; page++) {
                const pageResponse = await fetch(`/api/projects/${encodeURIComponent(projectName)}/images?per_page=10000&page=${page}`);
                const pageData = await pageResponse.json();
                allImages = allImages.concat(pageData.images || []);
            }
        }
        
        // 统计已标注数量
        labeledCount = allImages.filter(img => img.category && img.category.trim() !== '').length;
        
        // 应用筛选（默认显示未分类）
        filterImages();
    } catch (error) {
        console.error('加载图片失败:', error);
        showMessage('加载图片失败: ' + error.message, 'error');
        document.getElementById('previewContent').innerHTML = '<div class="no-images">加载失败</div>';
    }
}

// 预加载图片
function preloadImage(index) {
    if (index < 0 || index >= images.length) {
        return;
    }
    
    const image = images[index];
    const imageUrl = `/api/projects/${encodeURIComponent(projectName)}/image/${encodeURIComponent(image.path)}`;
    
    // 如果已经预加载过，跳过
    if (preloadedImages.has(imageUrl)) {
        return;
    }
    
    // 创建 Image 对象预加载，使用更高优先级
    const img = new Image();
    img.loading = 'eager'; // 立即加载，不使用懒加载
    img.onload = function() {
        preloadedImages.set(imageUrl, true);
    };
    img.onerror = function() {
        // 预加载失败也记录，避免重复尝试
        preloadedImages.set(imageUrl, false);
    };
    img.src = imageUrl;
}

// 预加载多张图片（当前图片前后各几张）
function preloadMultipleImages() {
    if (images.length === 0) {
        return;
    }
    
    // 预加载当前图片前后各3张
    const preloadCount = 3;
    for (let i = -preloadCount; i <= preloadCount; i++) {
        if (i === 0) continue; // 跳过当前图片
        const index = (currentImageIndex + i + images.length) % images.length;
        preloadImage(index);
    }
}

// 显示当前图片
function displayCurrentImage() {
    if (images.length === 0) {
        document.getElementById('previewContent').innerHTML = '<div class="no-images">暂无图片</div>';
        return;
    }
    
    const image = images[currentImageIndex];
    const imageUrl = `/api/projects/${encodeURIComponent(projectName)}/image/${encodeURIComponent(image.path)}`;
    const filename = image.path.split('/').pop();
    currentCategory = image.category || '';
    
    // 检查图片是否已预加载
    const isPreloaded = preloadedImages.has(imageUrl);
    
    // 先创建容器结构，保持布局稳定
    document.getElementById('previewContent').innerHTML = `
        <div class="preview-image-container">
            <div class="preview-image-wrapper">
                <img src="${imageUrl}" alt="${escapeHtml(filename)}" class="preview-image" 
                     loading="eager"
                     ${isPreloaded ? 'style="opacity: 1;"' : 'style="opacity: 0;"'}
                     onload="this.style.opacity='1'"
                     onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22%3E%3Ctext x=%2250%22 y=%2250%22 text-anchor=%22middle%22%3E图片加载失败%3C/text%3E%3C/svg%3E'; this.style.opacity='1'">
            </div>
            <div class="preview-info">
                <div>${escapeHtml(filename)}</div>
                <div style="margin-top: 10px; color: var(--text-secondary);">${image.path}</div>
            </div>
        </div>
    `;
    
    // 设置图片初始透明度和过渡效果
    const img = document.querySelector('.preview-image');
    if (img) {
        if (!isPreloaded) {
            img.style.transition = 'opacity 0.2s ease-in-out';
        }
        
        // 禁止图片上的所有交互
        img.addEventListener('dragstart', (e) => e.preventDefault());
        img.addEventListener('contextmenu', (e) => e.preventDefault());
        img.addEventListener('selectstart', (e) => e.preventDefault());
        
        // 禁止鼠标滚轮缩放
        img.addEventListener('wheel', (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, { passive: false });
        
        // 禁止触摸滑动
        img.addEventListener('touchmove', (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, { passive: false });
        
        img.addEventListener('touchstart', (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, { passive: false });
    }
    
    // 禁止图片包装器上的滑动
    const wrapper = document.querySelector('.preview-image-wrapper');
    if (wrapper) {
        wrapper.addEventListener('wheel', (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, { passive: false });
        
        wrapper.addEventListener('touchmove', (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, { passive: false });
    }
    
    updateStats();
    
    // 预加载多张图片（当前图片前后各3张）
    preloadMultipleImages();
}

// 更新统计信息
function updateStats() {
    document.getElementById('currentIndex').textContent = currentImageIndex + 1;
    document.getElementById('totalImages').textContent = images.length;
    document.getElementById('totalImages2').textContent = images.length;
    document.getElementById('labeledCount').textContent = labeledCount;
    document.getElementById('currentCategory').textContent = currentCategory || '未分类';
}

// 设置键盘监听
function setupKeyboardListeners() {
    document.addEventListener('keydown', (e) => {
        // 如果焦点在输入框或选择框上，不处理
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') {
            return;
        }
        
        const key = e.key;
        // 只处理已绑定的按键标注功能
        if (keyBindings[key] !== undefined && keyBindings[key] !== '') {
            e.preventDefault();
            labelImageWithCategory(keyBindings[key]);
        }
    });
}

// 使用指定类别标注当前图片
async function labelImageWithCategory(category) {
    if (images.length === 0) {
        return;
    }
    
    const image = images[currentImageIndex];
    
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/files/label`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_paths: [image.path],
                category: category
            })
        });
        
        if (response.ok) {
            // 更新本地数据（同时更新allImages和images）
            const imageInAll = allImages.find(img => img.path === image.path);
            if (imageInAll) {
                imageInAll.category = category;
            }
            image.category = category;
            currentCategory = category;
            
            // 更新已标注数量
            labeledCount = allImages.filter(img => img.category && img.category.trim() !== '').length;
            
            // 当前筛选为“未分类”时，标注成非空类别应直接从当前列表移除并显示下一张
            if (currentFilterCategory === '' && category && category.trim() !== '') {
                images.splice(currentImageIndex, 1);
                // 同步 filteredImages（images 通常就是 filteredImages 的引用，这里再保险）
                filteredImages = images;

                if (images.length === 0) {
                    document.getElementById('previewContent').innerHTML = '<div class="no-images">暂无图片</div>';
                    updateStats();
                    showMessage(`已标注为: ${category}`, 'success');
                    return;
                }

                if (currentImageIndex >= images.length) {
                    currentImageIndex = 0;
                }

                // 清空预加载缓存，避免缓存占用
                preloadedImages.clear();
                displayCurrentImage();
                updateStats();
                showMessage(`已标注为: ${category}`, 'success');
                return;
            }

            updateStats();
            showMessage(`已标注为: ${category}`, 'success');

            // 自动加载下一张（延迟时间缩短，因为已经预加载）
            setTimeout(() => {
                nextImage();
            }, 100);
        } else {
            const data = await response.json();
            showMessage('标注失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('标注失败: ' + error.message, 'error');
    }
}

// 手动标注当前图片
async function labelCurrentImage() {
    if (images.length === 0) {
        return;
    }
    
    const category = prompt('请输入类别名称（留空表示未分类）:');
    if (category === null) {
        return; // 用户取消
    }
    
    await labelImageWithCategory(category || '');
}

// 上一张图片
function previousImage() {
    if (images.length === 0) {
        return;
    }
    
    currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
    displayCurrentImage();
}

// 下一张图片
function nextImage() {
    if (images.length === 0) {
        return;
    }
    
    currentImageIndex = (currentImageIndex + 1) % images.length;
    displayCurrentImage();
}

// 跳过当前图片
function skipImage() {
    nextImage();
}

// 显示消息
function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
    
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 3000);
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

