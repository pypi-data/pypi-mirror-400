// 项目选择页面逻辑

// 选中的项目集合
let selectedProjects = new Set();
let projectsData = []; // 存储项目数据用于显示

// 加载项目列表
async function loadProjects() {
    try {
        const response = await fetch('/api/projects');
        projectsData = await response.json();
        
        const grid = document.getElementById('projectsGrid');
        if (projectsData.length === 0) {
            grid.innerHTML = '<div style="text-align: center; padding: 40px; color: #7f8c8d;">暂无项目，请创建新项目</div>';
            return;
        }
        
        grid.innerHTML = projectsData.map(project => {
            const safeNote = (project.note || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
            const safeName = escapeHtml(project.name);
            const isChecked = selectedProjects.has(project.name) ? 'checked' : '';
            return `
            <div class="project-card">
                <div class="project-card-checkbox">
                    <input type="checkbox" class="project-checkbox" value="${safeName}" ${isChecked} onchange="updateSelection()">
                </div>
                <div class="project-card-content" onclick="openProject('${safeName}')">
                    <h3>${safeName}</h3>
                    <div class="note">${escapeHtml(project.note || '暂无备注')}</div>
                    <div class="meta">
                        <span>📄 ${project.file_count} 个文件</span>
                        <span>🕒 ${formatDate(project.created_at)}</span>
                    </div>
                </div>
                <div class="project-card-actions">
                    <button class="btn btn-edit" onclick="event.stopPropagation(); showEditProjectModal('${safeName}', '${safeNote}')" title="修改项目">✏️ 修改</button>
                    <button class="btn btn-danger" onclick="event.stopPropagation(); deleteProject('${safeName}')" title="删除项目">🗑️ 删除</button>
                </div>
            </div>
        `;
        }).join('');
        
        updateSelection();
    } catch (error) {
        showMessage('加载项目列表失败: ' + error.message, 'error');
    }
}

// 更新选择状态
function updateSelection() {
    selectedProjects.clear();
    document.querySelectorAll('.project-checkbox:checked').forEach(checkbox => {
        selectedProjects.add(checkbox.value);
    });
    
    const count = selectedProjects.size;
    const batchActions = document.getElementById('batchActions');
    const selectedCount = document.getElementById('selectedCount');
    const splitBtn = document.getElementById('splitBtn');
    const mergeBtn = document.getElementById('mergeBtn');
    const copyBtn = document.getElementById('copyBtn');
    
    selectedCount.textContent = count;
    
    if (count > 0) {
        batchActions.style.display = 'block';
        splitBtn.style.display = count === 1 ? 'inline-block' : 'none';
        mergeBtn.style.display = count >= 2 ? 'inline-block' : 'none';
        copyBtn.style.display = count === 1 ? 'inline-block' : 'none';
    } else {
        batchActions.style.display = 'none';
    }
}

// 清除选择
function clearSelection() {
    selectedProjects.clear();
    document.querySelectorAll('.project-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
    updateSelection();
}

// 打开项目
function openProject(name) {
    window.location.href = `/project/${encodeURIComponent(name)}`;
}

// 显示创建项目模态框
function showCreateProjectModal() {
    document.getElementById('createProjectModal').style.display = 'block';
    document.getElementById('projectName').focus();
}

// 关闭创建项目模态框
function closeCreateProjectModal() {
    document.getElementById('createProjectModal').style.display = 'none';
    document.getElementById('createProjectForm').reset();
}

// 创建项目
document.getElementById('createProjectForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('projectName').value.trim();
    const note = document.getElementById('projectNote').value.trim();
    
    if (!name) {
        showMessage('项目名称不能为空', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/projects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, note })
        });
        
        if (response.ok) {
            showMessage('项目创建成功', 'success');
            closeCreateProjectModal();
            loadProjects();
        } else {
            const data = await response.json();
            showMessage('创建失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('创建失败: ' + error.message, 'error');
    }
});

// 显示修改项目模态框
function showEditProjectModal(name, note) {
    document.getElementById('editProjectOriginalName').value = name;
    document.getElementById('editProjectName').value = name;
    document.getElementById('editProjectNote').value = note || '';
    document.getElementById('editProjectModal').style.display = 'block';
    document.getElementById('editProjectName').focus();
}

// 关闭修改项目模态框
function closeEditProjectModal() {
    document.getElementById('editProjectModal').style.display = 'none';
    document.getElementById('editProjectForm').reset();
}

// 修改项目
document.getElementById('editProjectForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const originalName = document.getElementById('editProjectOriginalName').value.trim();
    const name = document.getElementById('editProjectName').value.trim();
    const note = document.getElementById('editProjectNote').value.trim();
    
    if (!name) {
        showMessage('项目名称不能为空', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(originalName)}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, note })
        });
        
        if (response.ok) {
            showMessage('项目修改成功', 'success');
            closeEditProjectModal();
            loadProjects();
        } else {
            const data = await response.json();
            showMessage('修改失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('修改失败: ' + error.message, 'error');
    }
});

// 删除项目
async function deleteProject(name) {
    if (!confirm(`确定要删除项目 "${name}" 吗？此操作不可恢复！`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(name)}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showMessage('项目删除成功', 'success');
            loadProjects();
        } else {
            const data = await response.json();
            showMessage('删除失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('删除失败: ' + error.message, 'error');
    }
}

// ==================== 分割项目功能 ====================

// 显示分割项目模态框
function showSplitProjectModal() {
    const selected = Array.from(selectedProjects);
    if (selected.length !== 1) {
        showMessage('请选择一个项目进行分割', 'error');
        return;
    }
    
    const projectName = selected[0];
    const project = projectsData.find(p => p.name === projectName);
    
    if (!project) {
        showMessage('项目不存在', 'error');
        return;
    }
    
    document.getElementById('splitProjectInfo').innerHTML = `
        <strong>${escapeHtml(projectName)}</strong><br>
        <span style="color: var(--text-secondary);">${project.file_count} 个文件</span>
    `;
    document.getElementById('splitCount').value = 2;
    document.getElementById('splitProjectModal').style.display = 'block';
}

// 关闭分割项目模态框
function closeSplitProjectModal() {
    document.getElementById('splitProjectModal').style.display = 'none';
    document.getElementById('splitProjectForm').reset();
}

// 分割项目表单提交
document.getElementById('splitProjectForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const selected = Array.from(selectedProjects);
    if (selected.length !== 1) {
        showMessage('请选择一个项目进行分割', 'error');
        return;
    }
    
    const projectName = selected[0];
    const n = parseInt(document.getElementById('splitCount').value);
    
    if (n < 2) {
        showMessage('分割份数必须大于等于2', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/split`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ n })
        });
        
        if (response.ok) {
            const data = await response.json();
            showMessage(`成功分割成 ${data.split_projects.length} 个项目`, 'success');
            closeSplitProjectModal();
            clearSelection();
            loadProjects();
        } else {
            const data = await response.json();
            showMessage('分割失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('分割失败: ' + error.message, 'error');
    }
});

// ==================== 合并项目功能 ====================

// 显示合并项目模态框
async function showMergeProjectsModal() {
    const selected = Array.from(selectedProjects);
    if (selected.length < 2) {
        showMessage('请至少选择2个项目进行合并', 'error');
        return;
    }
    
    // 显示源项目列表
    const sourceProjectsDiv = document.getElementById('mergeSourceProjects');
    sourceProjectsDiv.innerHTML = selected.map(name => {
        const project = projectsData.find(p => p.name === name);
        return `<div style="margin-bottom: 5px;">• ${escapeHtml(name)} (${project ? project.file_count : 0} 个文件)</div>`;
    }).join('');
    
    // 清空目标项目名
    document.getElementById('mergeTargetProject').value = '';
    
    // 检测冲突
    await checkMergeConflicts(selected);
    
    document.getElementById('mergeProjectsModal').style.display = 'block';
}

// 检测合并冲突
async function checkMergeConflicts(projectNames) {
    try {
        const response = await fetch('/api/projects/check-conflicts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ source_projects: projectNames })
        });
        
        if (response.ok) {
            const data = await response.json();
            const conflictsDiv = document.getElementById('mergeConflicts');
            const conflictsList = document.getElementById('conflictsList');
            
            if (data.has_conflicts) {
                conflictsDiv.style.display = 'block';
                conflictsList.innerHTML = data.conflicts.slice(0, 10).map(conflict => {
                    const occurrences = conflict.occurrences.map(occ => 
                        `${escapeHtml(occ.project)} (${escapeHtml(occ.category || '未分类')})`
                    ).join(', ');
                    return `<div style="margin-bottom: 8px; padding: 8px; background: white; border-radius: 4px;">
                        <strong>${escapeHtml(conflict.file_path.split('/').pop())}</strong><br>
                        <small style="color: #666;">出现在: ${occurrences}</small>
                    </div>`;
                }).join('');
                
                if (data.total_conflicts > 10) {
                    conflictsList.innerHTML += `<div style="color: #856404; margin-top: 10px;">... 还有 ${data.total_conflicts - 10} 个冲突文件</div>`;
                }
            } else {
                conflictsDiv.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('检测冲突失败:', error);
    }
}

// 关闭合并项目模态框
function closeMergeProjectsModal() {
    document.getElementById('mergeProjectsModal').style.display = 'none';
    document.getElementById('mergeProjectsForm').reset();
    document.getElementById('mergeConflicts').style.display = 'none';
}

// 合并项目表单提交
document.getElementById('mergeProjectsForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const selected = Array.from(selectedProjects);
    if (selected.length < 2) {
        showMessage('请至少选择2个项目进行合并', 'error');
        return;
    }
    
    const targetProject = document.getElementById('mergeTargetProject').value.trim();
    if (!targetProject) {
        showMessage('目标项目名称不能为空', 'error');
        return;
    }
    
    const conflictResolution = document.getElementById('conflictResolution').value;
    
    try {
        const response = await fetch('/api/projects/merge', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                source_projects: selected,
                target_project: targetProject,
                conflict_resolution: conflictResolution
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            showMessage(`合并成功！共 ${data.total_files} 个文件${data.conflict_count > 0 ? `，${data.conflict_count} 个冲突已解决` : ''}`, 'success');
            closeMergeProjectsModal();
            clearSelection();
            loadProjects();
        } else {
            const data = await response.json();
            showMessage('合并失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('合并失败: ' + error.message, 'error');
    }
});

// ==================== 复制项目功能 ====================

// 显示复制项目模态框
function showCopyProjectModal() {
    const selected = Array.from(selectedProjects);
    if (selected.length !== 1) {
        showMessage('请选择一个项目进行复制', 'error');
        return;
    }
    
    const projectName = selected[0];
    const project = projectsData.find(p => p.name === projectName);
    
    if (!project) {
        showMessage('项目不存在', 'error');
        return;
    }
    
    document.getElementById('copyProjectInfo').innerHTML = `
        <strong>${escapeHtml(projectName)}</strong><br>
        <span style="color: var(--text-secondary);">${project.file_count} 个文件</span>
    `;
    document.getElementById('copyProjectName').value = '';
    document.getElementById('copyProjectModal').style.display = 'block';
    document.getElementById('copyProjectName').focus();
}

// 关闭复制项目模态框
function closeCopyProjectModal() {
    document.getElementById('copyProjectModal').style.display = 'none';
    document.getElementById('copyProjectForm').reset();
}

// 复制项目表单提交
document.getElementById('copyProjectForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const selected = Array.from(selectedProjects);
    if (selected.length !== 1) {
        showMessage('请选择一个项目进行复制', 'error');
        return;
    }
    
    const projectName = selected[0];
    const newName = document.getElementById('copyProjectName').value.trim();
    
    if (!newName) {
        showMessage('新项目名称不能为空', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/copy`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ new_name: newName })
        });
        
        if (response.ok) {
            showMessage('项目复制成功', 'success');
            closeCopyProjectModal();
            clearSelection();
            loadProjects();
        } else {
            const data = await response.json();
            showMessage('复制失败: ' + (data.error || '未知错误'), 'error');
        }
    } catch (error) {
        showMessage('复制失败: ' + error.message, 'error');
    }
});

// 点击模态框外部关闭
window.onclick = function(event) {
    const createModal = document.getElementById('createProjectModal');
    const editModal = document.getElementById('editProjectModal');
    const splitModal = document.getElementById('splitProjectModal');
    const mergeModal = document.getElementById('mergeProjectsModal');
    const copyModal = document.getElementById('copyProjectModal');
    
    if (event.target === createModal) {
        closeCreateProjectModal();
    }
    if (event.target === editModal) {
        closeEditProjectModal();
    }
    if (event.target === splitModal) {
        closeSplitProjectModal();
    }
    if (event.target === mergeModal) {
        closeMergeProjectsModal();
    }
    if (event.target === copyModal) {
        closeCopyProjectModal();
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

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
}

// 页面加载时加载项目列表
loadProjects();

