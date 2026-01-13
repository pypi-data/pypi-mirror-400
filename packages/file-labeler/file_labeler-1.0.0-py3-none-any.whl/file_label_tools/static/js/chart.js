// 图表展示逻辑

let statsChart = null;
let exportedStatsChart = null;

// 加载统计信息并绘制图表
async function loadStatsChart() {
    try {
        const response = await fetch(`/api/projects/${encodeURIComponent(projectName)}/stats`);
        const stats = await response.json();
        
        updateChart(stats);
        updateExportedChart(stats);
        updateCategoryCountList(stats);
    } catch (error) {
        console.error('加载统计信息失败:', error);
    }
}

function updateCategoryCountList(stats) {
    const container = document.getElementById('categoryCountList');
    if (!container) return;

    const totalMap = stats.category_count || {};
    const exportedMap = stats.exported_category_count || {};

    const categories = new Set([...Object.keys(totalMap), ...Object.keys(exportedMap)]);
    const rows = Array.from(categories).map(cat => {
        const total = Number(totalMap[cat] || 0);
        const exported = Number(exportedMap[cat] || 0);
        const unexported = Math.max(0, total - exported);
        return { cat, total, exported, unexported };
    });

    // 排序：总数降序；同分按类别名
    rows.sort((a, b) => {
        if (b.total !== a.total) return b.total - a.total;
        return String(a.cat).localeCompare(String(b.cat), 'zh-CN');
    });

    if (rows.length === 0) {
        container.innerHTML = '<div class="loading">暂无数据</div>';
        return;
    }

    // 用表格展示，复用现有样式
    container.innerHTML = `
        <div class="file-list-table" style="margin: 0;">
            <table>
                <thead>
                    <tr>
                        <th style="width: 45%;">类别</th>
                        <th style="width: 18%;">总数</th>
                        <th style="width: 18%;">已导出</th>
                        <th style="width: 19%;">未导出</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows.map(r => `
                        <tr>
                            <td>
                                <span class="category-badge ${r.cat === '未分类' ? 'no-category' : ''}">
                                    ${escapeHtml(String(r.cat))}
                                </span>
                            </td>
                            <td>${r.total}</td>
                            <td>${r.exported}</td>
                            <td>${r.unexported}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// 更新所有文件图表
function updateChart(stats) {
    const ctx = document.getElementById('statsChart').getContext('2d');
    
    const labels = Object.keys(stats.category_count);
    const data = Object.values(stats.category_count);
    const colors = generateColors(labels.length);
    
    if (statsChart) {
        statsChart.destroy();
    }
    
    statsChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels.length > 0 ? labels : ['暂无数据'],
            datasets: [{
                data: data.length > 0 ? data : [1],
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 15,
                        font: {
                            size: 14
                        },
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                const dataset = data.datasets[0];
                                return data.labels.map((label, i) => {
                                    const value = dataset.data[i];
                                    const total = dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                    return {
                                        text: `${label}: ${value} (${percentage}%)`,
                                        fillStyle: dataset.backgroundColor[i],
                                        strokeStyle: dataset.borderColor || '#fff',
                                        lineWidth: dataset.borderWidth || 2,
                                        hidden: false,
                                        index: i
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                },
                datalabels: {
                    display: true,
                    color: '#333',
                    font: {
                        size: 12,
                        weight: 'bold'
                    },
                    formatter: function(value, context) {
                        const label = context.chart.data.labels[context.dataIndex];
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                        return `${label}\n${value} (${percentage}%)`;
                    },
                    anchor: 'end',
                    align: 'end',
                    offset: 10,
                    textStrokeColor: '#fff',
                    textStrokeWidth: 2
                },
                title: {
                    display: true,
                    text: `总计: ${stats.total} 个文件`,
                    position: 'bottom',
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                }
            }
        }
    });
}

// 更新已导出文件图表
function updateExportedChart(stats) {
    const ctx = document.getElementById('exportedStatsChart').getContext('2d');
    
    const labels = Object.keys(stats.exported_category_count || {});
    const data = Object.values(stats.exported_category_count || {});
    const colors = generateColors(labels.length);
    
    if (exportedStatsChart) {
        exportedStatsChart.destroy();
    }
    
    // 如果已导出文件数为0，显示特殊提示
    if (stats.exported_total === 0 || labels.length === 0) {
        exportedStatsChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['暂无已导出文件'],
                datasets: [{
                    data: [1],
                    backgroundColor: ['#e0e0e0'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    },
                    title: {
                        display: true,
                        text: `已导出: 0 个文件`,
                        position: 'bottom',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                }
            }
        });
        return;
    }
    
    exportedStatsChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 15,
                        font: {
                            size: 14
                        },
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                const dataset = data.datasets[0];
                                return data.labels.map((label, i) => {
                                    const value = dataset.data[i];
                                    const total = dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                    return {
                                        text: `${label}: ${value} (${percentage}%)`,
                                        fillStyle: dataset.backgroundColor[i],
                                        strokeStyle: dataset.borderColor || '#fff',
                                        lineWidth: dataset.borderWidth || 2,
                                        hidden: false,
                                        index: i
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                },
                datalabels: {
                    display: true,
                    color: '#333',
                    font: {
                        size: 12,
                        weight: 'bold'
                    },
                    formatter: function(value, context) {
                        const label = context.chart.data.labels[context.dataIndex];
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                        return `${label}\n${value} (${percentage}%)`;
                    },
                    anchor: 'end',
                    align: 'end',
                    offset: 10,
                    textStrokeColor: '#fff',
                    textStrokeWidth: 2
                },
                title: {
                    display: true,
                    text: `已导出: ${stats.exported_total} 个文件`,
                    position: 'bottom',
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                }
            }
        }
    });
}

// 生成颜色数组
function generateColors(count) {
    const colors = [
        '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
        '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b',
        '#27ae60', '#d35400', '#8e44ad', '#2980b9', '#f1c40f'
    ];
    
    const result = [];
    for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
    }
    return result;
}

