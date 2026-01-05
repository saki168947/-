// 状态管理
let isLoading = false;
let moviesData = [];

/**
 * 显示状态消息
 */
function showStatus(message, type = 'info') {
    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    statusEl.className = `status-message show ${type}`;

    // 5秒后自动隐藏
    setTimeout(() => {
        statusEl.classList.remove('show');
    }, 5000);
}

/**
 * 开始爬取数据
 */
async function startScrape() {
    console.log('Button clicked: startScrape'); // DEBUG LOG
    if (isLoading) {
        showStatus('⏳ 正在爬取中，请等待...', 'loading');
        return;
    }

    isLoading = true;
    const scrapeBtn = document.getElementById('scrapeBtn');
    const originalText = scrapeBtn.innerHTML;

    // 更新按钮状态
    scrapeBtn.disabled = true;
    scrapeBtn.innerHTML = '<span class="icon">🔄</span> 爬取中' + '<span class="loading"></span>';

    showStatus('🔄 正在爬取猫眼电影数据...', 'loading');

    try {
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (result.success) {
            moviesData = result.data;
            updateTable(moviesData);
            updateCards(moviesData.slice(0, 3)); // 更新前3名卡片
            updateJsonDisplay(moviesData);
            updateCountBadge(result.count);
            updateVisualization(); // 更新可视化
            showStatus(`✅ 成功爬取 ${result.count} 部电影！`, 'success');
        } else {
            showStatus(`❌ ${result.message}`, 'error');
        }
    } catch (error) {
        console.error('爬取失败:', error);
        showStatus(`❌ 爬取失败: ${error.message}`, 'error');
    } finally {
        isLoading = false;
        scrapeBtn.disabled = false;
        scrapeBtn.innerHTML = originalText;
    }
}

/**
 * 更新前3名卡片
 */
function updateCards(topMovies) {
    const cardsContainer = document.getElementById('topCards');
    const cardsWrapper = document.getElementById('cardsWrapper');

    if (topMovies.length === 0) {
        cardsContainer.style.display = 'none';
        return;
    }

    cardsContainer.style.display = 'block';
    cardsWrapper.innerHTML = topMovies.map((movie, index) => `
        <div class="holo-card" onclick="window.open('${movie['链接']}', '_blank')">
            <div class="card-content">
                <div class="card-rank rank-${index + 1}">${movie['排名']}</div>
                <img src="${movie['图片']}" alt="${movie['电影名称']}" class="card-image" onerror="this.src='https://via.placeholder.com/220x330?text=No+Image'">
                <div class="card-info">
                    <div class="card-title">${movie['电影名称']}</div>
                    <div class="card-score">评分: ${movie['评分']}</div>
                </div>
            </div>
        </div>
    `).join('');

    // 添加3D效果事件监听
    const cards = document.querySelectorAll('.holo-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', handleMouseMove);
        card.addEventListener('mouseleave', handleMouseLeave);
    });
}

/**
 * 处理卡片鼠标移动事件（3D效果）
 */
function handleMouseMove(e) {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = ((y - centerY) / centerY) * -10; // 最大旋转角度
    const rotateY = ((x - centerX) / centerX) * 10;

    // 设置CSS变量
    card.style.setProperty('--rx', `${rotateX}deg`);
    card.style.setProperty('--ry', `${rotateY}deg`);
    card.style.setProperty('--mx', `${x}px`);
    card.style.setProperty('--my', `${y}px`);
    card.style.setProperty('--opacity', '1');
}

/**
 * 处理卡片鼠标离开事件
 */
function handleMouseLeave(e) {
    const card = e.currentTarget;
    card.style.setProperty('--rx', '0deg');
    card.style.setProperty('--ry', '0deg');
    card.style.setProperty('--opacity', '0');
}

/**
 * 更新表格数据
 */
function updateTable(movies) {
    const tableBody = document.getElementById('tableBody');

    if (movies.length === 0) {
        tableBody.innerHTML = '<tr class="empty-row"><td colspan="4">暂无数据</td></tr>';
        return;
    }

    tableBody.innerHTML = movies.map((movie, index) => `
        <tr>
            <td><strong>${movie['排名']}</strong></td>
            <td><a href="${movie['链接']}" target="_blank" class="movie-link">${movie['电影名称']}</a></td>
            <td><span style="color: var(--primary-color); font-weight: bold;">${movie['评分']}</span></td>
            <td>${movie['上映时间']}</td>
        </tr>
    `).join('');
}

/**
 * 更新JSON展示
 */
function updateJsonDisplay(movies) {
    const jsonOutput = document.getElementById('jsonOutput');
    jsonOutput.textContent = JSON.stringify(movies, null, 2);
}

/**
 * 更新计数badge
 */
function updateCountBadge(count) {
    const badge = document.getElementById('countBadge');
    badge.textContent = count;

    // 添加动画效果
    badge.style.transform = 'scale(1.2)';
    setTimeout(() => {
        badge.style.transition = 'transform 0.3s ease';
        badge.style.transform = 'scale(1)';
    }, 0);
}

/**
 * 清空数据
 */
function clearData() {
    if (confirm('确定要清空所有数据吗？')) {
        moviesData = [];
        document.getElementById('tableBody').innerHTML =
            '<tr class="empty-row"><td colspan="4">暂无数据，请点击"开始爬取数据"</td></tr>';
        document.getElementById('jsonOutput').textContent = '[]';
        document.getElementById('countBadge').textContent = '0';
        document.getElementById('topCards').style.display = 'none'; // 隐藏卡片区域
        document.getElementById('vizSection').style.display = 'none'; // 隐藏可视化区域
        showStatus('✅ 数据已清空', 'success');
    }
}

/**
 * 导出为CSV
 */
async function exportCSV() {
    if (moviesData.length === 0) {
        showStatus('❌ 没有数据可导出，请先爬取数据', 'error');
        return;
    }

    try {
        const response = await fetch('/api/export/csv', {
            method: 'POST'
        });

        if (response.ok) {
            const blob = await response.blob();
            downloadFile(blob, 'maoyan_movies.csv');
            showStatus('✅ CSV文件已下载！', 'success');
        } else {
            showStatus('❌ 导出失败，请重试', 'error');
        }
    } catch (error) {
        console.error('导出失败:', error);
        showStatus(`❌ 导出失败: ${error.message}`, 'error');
    }
}

/**
 * 导出为TXT
 */
async function exportTXT() {
    if (moviesData.length === 0) {
        showStatus('❌ 没有数据可导出，请先爬取数据', 'error');
        return;
    }

    try {
        const response = await fetch('/api/export/txt', {
            method: 'POST'
        });

        if (response.ok) {
            const blob = await response.blob();
            downloadFile(blob, 'maoyan_movies.txt');
            showStatus('✅ TXT文件已下载！', 'success');
        } else {
            showStatus('❌ 导出失败，请重试', 'error');
        }
    } catch (error) {
        console.error('导出失败:', error);
        showStatus(`❌ 导出失败: ${error.message}`, 'error');
    }
}

/**
 * 下载文件的辅助函数
 */
function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

/**
 * 页面加载时获取数据
 */
// 页面加载时获取数据
document.addEventListener('DOMContentLoaded', async () => {
    // 移除自动获取数据逻辑，仅在点击按钮时爬取
    // We only want to hide the preloader
});

// Hide Preloader on Load
window.addEventListener('load', () => {
    const preloader = document.getElementById('preloader');
    if (preloader) {
        // Minimum loading time of 1s to show off the fancy animation
        setTimeout(() => {
            preloader.classList.add('hidden');
            // Ensure it doesn't block clicks even if CSS fails
            preloader.style.pointerEvents = 'none';
        }, 1000);

        // Backup safety: Force hide after 5 seconds just in case
        setTimeout(() => {
            if (!preloader.classList.contains('hidden')) {
                console.warn('Preloader force hidden by safety timeout');
                preloader.classList.add('hidden');
                preloader.style.pointerEvents = 'none';
            }
        }, 5000);
    }
});

// Expose startScrape globally to ensure HTML onClick can find it
window.startScrape = startScrape;

// 键盘快捷键支持
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + S 导出CSV
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        exportCSV();
    }

    // Ctrl/Cmd + E 导出TXT
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        exportTXT();
    }
});

/**
 * 更新可视化图表
 */
async function updateVisualization() {
    const vizSection = document.getElementById('vizSection');
    vizSection.style.display = 'block';

    try {
        // 获取统计数据
        const response = await fetch('/api/stats');
        const result = await response.json();

        if (result.success) {
            renderCharts(result.score_distribution, result.year_distribution);
        }

        // 生成词云
        const wordCloudImg = document.getElementById('wordCloudImg');
        const loadingText = document.getElementById('wordCloudLoading');

        loadingText.style.display = 'block';
        wordCloudImg.style.display = 'none';

        // 加载词云图片
        wordCloudImg.src = `/api/wordcloud?t=${new Date().getTime()}`;
        wordCloudImg.onload = () => {
            loadingText.style.display = 'none';
            wordCloudImg.style.display = 'block';
        };

    } catch (error) {
        console.error('可视化更新失败:', error);
    }
}

function renderCharts(scoreDist, yearDist) {
    // 评分分布图
    const scoreChart = echarts.init(document.getElementById('scoreChart'));
    const scoreOption = {
        backgroundColor: 'transparent', // Ensure transparency
        tooltip: { trigger: 'item' },
        legend: { top: '5%', left: 'center', textStyle: { color: '#fff' } },
        series: [{
            name: '评分分布',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 10,
                borderColor: 'rgba(255,255,255,0.2)',
                borderWidth: 1
            },
            label: { show: false, position: 'center' },
            emphasis: {
                label: { show: true, fontSize: 20, fontWeight: 'bold', color: '#fff' }
            },
            labelLine: { show: false },
            data: Object.entries(scoreDist).map(([key, value]) => ({ value, name: key }))
        }]
    };
    scoreChart.setOption(scoreOption);

    // 年份分布图
    const yearChart = echarts.init(document.getElementById('yearChart'));
    const yearOption = {
        backgroundColor: 'transparent', // Ensure transparency
        tooltip: { trigger: 'axis' },
        xAxis: {
            type: 'category',
            data: Object.keys(yearDist),
            axisLabel: { color: '#fff', rotate: 45 }
        },
        yAxis: {
            type: 'value',
            axisLabel: { color: '#fff' },
            splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
        },
        series: [{
            data: Object.values(yearDist),
            type: 'bar',
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: '#83bff6' },
                    { offset: 0.5, color: '#188df0' },
                    { offset: 1, color: '#188df0' }
                ])
            },
            emphasis: {
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#2378f7' },
                        { offset: 0.7, color: '#2378f7' },
                        { offset: 1, color: '#83bff6' }
                    ])
                }
            }
        }]
    };
    yearChart.setOption(yearOption);

    // 响应式调整
    window.addEventListener('resize', () => {
        scoreChart.resize();
        yearChart.resize();
    });
}

/*
// Global 3D Tilt Effect - Temporarily Disabled for Debugging
let isTicking = false;
document.addEventListener('mousemove', (e) => {
    if (!isTicking) {
        window.requestAnimationFrame(() => {
            const container = document.querySelector('.container');
            if (container) {
                // Calculate rotation based on mouse position
                // Sensitivity factor (higher = less movement)
                const sensitivity = 100; 
                
                const x = (window.innerWidth / 2 - e.clientX) / sensitivity;
                const y = (window.innerHeight / 2 - e.clientY) / sensitivity;

                // Apply rotation
                // Limit rotation to avoid extreme angles
                const rotateY = Math.max(-5, Math.min(5, x));
                const rotateX = Math.max(-5, Math.min(5, y));

                container.style.transform = `rotateY(${rotateY}deg) rotateX(${rotateX}deg)`;
            }
            isTicking = false;
        });
        isTicking = true;
    }
});
*/
