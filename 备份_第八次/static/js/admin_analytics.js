//static/js/admin_analytics.js
// 全局统计页面JavaScript
let charts = {};

document.addEventListener('DOMContentLoaded', function() {
    loadAnalyticsData();
    setupEventListeners();
    loadInitialTableData(); // 加载初始表格数据
    addTableStyles(); // 添加表格样式
});

function setupEventListeners() {
    // 时间范围选择
    document.getElementById('timeRange').addEventListener('change', function() {
        loadAnalyticsData();
    });

    // 标签页切换
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.dataset.tab;

            // 更新激活的标签
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            // 显示对应的内容
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${tabId}-tab`).classList.add('active');

            // 加载对应标签的数据
            loadTabData(tabId);
        });
    });

    // 导出数据
    document.getElementById('exportData').addEventListener('click', exportData);

    // 刷新数据
    document.getElementById('refreshData').addEventListener('click', function() {
        loadAnalyticsData();
        loadAllTableData(); // 刷新所有表格数据
    });
}

function loadInitialTableData() {
    // 默认加载用户数据
    loadUsersTableData();
}

function loadTabData(tabId) {
    switch(tabId) {
        case 'users':
            loadUsersTableData();
            break;
        case 'articles':
            loadArticlesTableData();
            break;
        case 'events':
            loadEventsTableData();
            break;
        case 'courses':
            loadCoursesTableData();
            break;
    }
}

function loadAllTableData() {
    loadUsersTableData();
    loadArticlesTableData();
    loadEventsTableData();
    loadCoursesTableData();
}

// 表格数据加载函数
async function loadUsersTableData() {
    try {
        const response = await fetch('/admin/api/analytics/users_table');
        const data = await response.json();

        if (response.ok) {
            populateUsersTable(data);
        } else {
            console.error('Failed to load users data:', data.error);
            showTableError('usersTableBody', 'Failed to load user data');
        }
    } catch (error) {
        console.error('Error loading users data:', error);
        showTableError('usersTableBody', 'Error loading user data');
    }
}

async function loadArticlesTableData() {
    try {
        const response = await fetch('/admin/api/analytics/articles_table');
        const data = await response.json();

        if (response.ok) {
            populateArticlesTable(data);
        } else {
            console.error('Failed to load articles data:', data.error);
            showTableError('articlesTableBody', 'Failed to load article data');
        }
    } catch (error) {
        console.error('Error loading articles data:', error);
        showTableError('articlesTableBody', 'Error loading article data');
    }
}

async function loadEventsTableData() {
    try {
        const response = await fetch('/admin/api/analytics/events_table');
        const data = await response.json();

        if (response.ok) {
            populateEventsTable(data);
        } else {
            console.error('Failed to load events data:', data.error);
            showTableError('eventsTableBody', 'Failed to load event data');
        }
    } catch (error) {
        console.error('Error loading events data:', error);
        showTableError('eventsTableBody', 'Error loading event data');
    }
}

async function loadCoursesTableData() {
    try {
        const response = await fetch('/admin/api/analytics/courses_table');
        const data = await response.json();

        if (response.ok) {
            populateCoursesTable(data);
        } else {
            console.error('Failed to load courses data:', data.error);
            showTableError('coursesTableBody', 'Failed to load course data');
        }
    } catch (error) {
        console.error('Error loading courses data:', error);
        showTableError('coursesTableBody', 'Error loading course data');
    }
}

// 表格填充函数
function populateUsersTable(users) {
    const tableBody = document.getElementById('usersTableBody');

    if (!tableBody) return;

    if (!users || users.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; color: #6c757d; padding: 40px;">
                    <i class="fas fa-users" style="font-size: 48px; margin-bottom: 15px; display: block; color: #dee2e6;"></i>
                    <p>No user data available</p>
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = users.map(user => `
        <tr>
            <td>${user.id}</td>
            <td>${escapeHtml(user.username)}</td>
            <td>
                <span class="role-badge role-${user.role}">
                    ${escapeHtml(user.role)}
                </span>
            </td>
            <td>${escapeHtml(user.full_name)}</td>
            <td>${escapeHtml(user.org_name)}</td>
            <td>${formatDate(user.registration_date)}</td>
            <td>${user.last_login === 'Never' ? 'Never' : formatDate(user.last_login)}</td>
        </tr>
    `).join('');
}

function populateArticlesTable(articles) {
    const tableBody = document.getElementById('articlesTableBody');

    if (!tableBody) return;

    if (!articles || articles.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; color: #6c757d; padding: 40px;">
                    <i class="fas fa-file-alt" style="font-size: 48px; margin-bottom: 15px; display: block; color: #dee2e6;"></i>
                    <p>No article data available</p>
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = articles.map(article => `
        <tr>
            <td>${article.id}</td>
            <td title="${escapeHtml(article.title)}">
                ${truncateText(escapeHtml(article.title), 50)}
            </td>
            <td>${escapeHtml(article.author)}</td>
            <td>${article.content_length}</td>
            <td>${formatDate(article.created_at)}</td>
            <td>${formatDate(article.updated_at)}</td>
            <td>${article.views}</td>
        </tr>
    `).join('');
}

function populateEventsTable(events) {
    const tableBody = document.getElementById('eventsTableBody');

    if (!tableBody) return;

    if (!events || events.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; color: #6c757d; padding: 40px;">
                    <i class="fas fa-calendar-alt" style="font-size: 48px; margin-bottom: 15px; display: block; color: #dee2e6;"></i>
                    <p>No event data available</p>
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = events.map(event => `
        <tr>
            <td>${event.id}</td>
            <td title="${escapeHtml(event.event_name)}">
                ${truncateText(escapeHtml(event.event_name), 40)}
            </td>
            <td>${escapeHtml(event.organizer)}</td>
            <td>${formatDate(event.date)}</td>
            <td>${escapeHtml(event.location)}</td>
            <td>${event.max_participants}</td>
            <td>
                <span class="participant-count ${event.registered >= event.max_participants ? 'full' : ''}">
                    ${event.registered} / ${event.max_participants}
                </span>
            </td>
        </tr>
    `).join('');
}

function populateCoursesTable(courses) {
    const tableBody = document.getElementById('coursesTableBody');

    if (!tableBody) return;

    if (!courses || courses.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; color: #6c757d; padding: 40px;">
                    <i class="fas fa-book" style="font-size: 48px; margin-bottom: 15px; display: block; color: #dee2e6;"></i>
                    <p>No course data available</p>
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = courses.map(course => `
        <tr>
            <td>${course.id}</td>
            <td title="${escapeHtml(course.course_name)}">
                ${truncateText(escapeHtml(course.course_name), 50)}
            </td>
            <td>${escapeHtml(course.teacher)}</td>
            <td>${course.student_count}</td>
            <td>${formatDate(course.created_at)}</td>
            <td>
                <span class="status-badge status-${course.status.toLowerCase()}">
                    ${course.status}
                </span>
            </td>
            <td>
                <span class="rating-stars" data-rating="${course.rating}">
                    ${generateStarRating(course.rating)}
                </span>
            </td>
        </tr>
    `).join('');
}

function showTableError(tableBodyId, message) {
    const tableBody = document.getElementById(tableBodyId);
    if (tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; color: #dc3545; padding: 40px;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; margin-bottom: 15px; display: block;"></i>
                    <p>${message}</p>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="loadTabData('${tableBodyId.replace('TableBody', '')}')">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </td>
            </tr>
        `;
    }
}

// 工具函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function formatDate(dateString) {
    if (!dateString || dateString === 'Never') return 'N/A';

    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (e) {
        return 'Invalid Date';
    }
}

function generateStarRating(rating) {
    if (rating === 'N/A') return 'N/A';

    const numRating = parseFloat(rating);
    if (isNaN(numRating)) return 'N/A';

    const fullStars = Math.floor(numRating);
    const halfStar = numRating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);

    let stars = '';

    // 满星
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star text-warning"></i>';
    }

    // 半星
    if (halfStar) {
        stars += '<i class="fas fa-star-half-alt text-warning"></i>';
    }

    // 空星
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star text-warning"></i>';
    }

    return stars + ` <small class="text-muted">(${numRating.toFixed(1)})</small>`;
}

// 添加CSS样式
function addTableStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .role-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: capitalize;
        }

        .role-platform_admin {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .role-teacher {
            background: #4facfe;
            color: white;
        }

        .role-student {
            background: #00f2fe;
            color: white;
        }

        .role-community_org {
            background: #f093fb;
            color: white;
        }

        .status-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .status-active {
            background: #d4edda;
            color: #155724;
        }

        .status-inactive {
            background: #f8d7da;
            color: #721c24;
        }

        .participant-count.full {
            color: #dc3545;
            font-weight: bold;
        }

        .rating-stars {
            white-space: nowrap;
        }

        .btn-outline-primary {
            border: 1px solid #667eea;
            color: #667eea;
        }

        .btn-outline-primary:hover {
            background: #667eea;
            color: white;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
}

// 原有的图表和词云功能
async function loadAnalyticsData() {
    const timeRange = document.getElementById('timeRange').value;

    try {
        // 显示加载状态
        showLoadingState();

        // 加载统计数据
        const response = await fetch(`/admin/api/analytics/data?range=${timeRange}`);
        const data = await response.json();

        if (response.ok) {
            updateStatsOverview(data);
            createCharts(data);
        } else {
            alert('Failed to load data: ' + data.error);
        }

        // 加载词云数据
        await loadWordCloudData();

        // 隐藏加载状态
        hideLoadingState();
    } catch (error) {
        console.error('Error loading analytics data:', error);
        alert('Failed to load data');
        hideLoadingState();
    }
}

function showLoadingState() {
    const wordcloudElement = document.getElementById('wordcloud');
    if (wordcloudElement) {
        wordcloudElement.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; flex-direction: column;">
                <div class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite;"></div>
                <p style="margin-top: 15px; color: #6c757d;">Loading word cloud data...</p>
            </div>
        `;
    }
}

function hideLoadingState() {
    // 加载状态会在词云生成时自动清除
}

async function loadWordCloudData() {
    try {
        console.log('Loading word cloud data...');
        const response = await fetch('/admin/api/analytics/wordcloud');
        const data = await response.json();

        console.log('Word cloud data received:', data);

        if (response.ok && data && data.length > 0) {
            generateWordCloud(data);
        } else {
            console.error('Failed to load word cloud data or data is empty:', data);
            generateWordCloud(getDefaultWordCloudData());
        }
    } catch (error) {
        console.error('Error loading word cloud data:', error);
        generateWordCloud(getDefaultWordCloudData());
    }
}

function getDefaultWordCloudData() {
    // 默认词云数据
    return [
        { text: 'Education', weight: 13, freq: 25 },
        { text: 'Learning', weight: 12, freq: 22 },
        { text: 'Courses', weight: 11, freq: 20 },
        { text: 'Students', weight: 10, freq: 18 },
        { text: 'Teachers', weight: 9, freq: 16 },
        { text: 'Community', weight: 8, freq: 14 },
        { text: 'Events', weight: 7, freq: 12 },
        { text: 'Technology', weight: 6, freq: 10 },
        { text: 'Development', weight: 5, freq: 8 },
        { text: 'Programming', weight: 4, freq: 6 },
        { text: 'Projects', weight: 3, freq: 4 },
        { text: 'Collaboration', weight: 2, freq: 2 }
    ];
}

function updateStatsOverview(data) {
    const statsOverview = document.getElementById('statsOverview');

    const stats = [
        {
            icon: 'fas fa-users',
            value: data.user_stats.total,
            label: 'Total Users',
            color: '#667eea'
        },
        {
            icon: 'fas fa-user-graduate',
            value: data.user_stats.students,
            label: 'Students',
            color: '#4facfe'
        },
        {
            icon: 'fas fa-chalkboard-teacher',
            value: data.user_stats.teachers,
            label: 'Teachers',
            color: '#00f2fe'
        },
        {
            icon: 'fas fa-users-cog',
            value: data.user_stats.organizers,
            label: 'Organizers',
            color: '#764ba2'
        },
        {
            icon: 'fas fa-file-alt',
            value: data.content_stats.articles,
            label: 'Articles',
            color: '#f093fb'
        },
        {
            icon: 'fas fa-calendar-alt',
            value: data.content_stats.events,
            label: 'Events',
            color: '#f5576c'
        },
        {
            icon: 'fas fa-book',
            value: data.content_stats.courses,
            label: 'Courses',
            color: '#4ecdc4'
        },
        {
            icon: 'fas fa-chart-line',
            value: data.user_stats.active,
            label: 'Active Users',
            color: '#ff6b6b'
        }
    ];

    statsOverview.innerHTML = stats.map(stat => `
        <div class="stat-card">
            <div class="stat-icon" style="color: ${stat.color}">
                <i class="${stat.icon}"></i>
            </div>
            <h3>${stat.value}</h3>
            <p>${stat.label}</p>
        </div>
    `).join('');
}

function createCharts(data) {
    // 销毁现有图表
    Object.values(charts).forEach(chart => {
        if (chart) chart.destroy();
    });

    // 用户分布饼图
    const userDistributionCtx = document.getElementById('userDistributionChart');
    if (userDistributionCtx) {
        charts.userDistribution = new Chart(userDistributionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Students', 'Teachers', 'Community Organizers'],
                datasets: [{
                    data: [data.user_stats.students, data.user_stats.teachers, data.user_stats.organizers],
                    backgroundColor: ['#4facfe', '#00f2fe', '#667eea'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // 内容统计柱状图
    const contentStatsCtx = document.getElementById('contentStatsChart');
    if (contentStatsCtx) {
        charts.contentStats = new Chart(contentStatsCtx, {
            type: 'bar',
            data: {
                labels: ['Articles', 'Events', 'Courses'],
                datasets: [{
                    label: 'Count',
                    data: [data.content_stats.articles, data.content_stats.events, data.content_stats.courses],
                    backgroundColor: ['#4facfe', '#00f2fe', '#667eea'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // 活跃用户趋势图
    const activeUsersCtx = document.getElementById('activeUsersChart');
    if (activeUsersCtx) {
        const activeUsersData = {};
        data.active_users.forEach(item => {
            activeUsersData[item.role] = item.count;
        });

        charts.activeUsers = new Chart(activeUsersCtx, {
            type: 'line',
            data: {
                labels: ['Students', 'Teachers', 'Organizers'],
                datasets: [{
                    label: 'Active Users',
                    data: [
                        activeUsersData.student || 0,
                        activeUsersData.teacher || 0,
                        activeUsersData.community_org || 0
                    ],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // 文章分类饼图
    const articleCategoriesCtx = document.getElementById('articleCategoriesChart');
    if (articleCategoriesCtx) {
        charts.articleCategories = new Chart(articleCategoriesCtx, {
            type: 'pie',
            data: {
                labels: data.article_categories.map(item => item.category),
                datasets: [{
                    data: data.article_categories.map(item => item.count),
                    backgroundColor: ['#4facfe', '#00f2fe', '#667eea', '#f093fb', '#f5576c']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

function generateWordCloud(wordData) {
    const wordcloudElement = document.getElementById('wordcloud');
    const wordcloudStats = document.getElementById('wordcloudStats');

    if (!wordcloudElement) {
        console.error('Word cloud element not found');
        return;
    }

    // 清空容器
    wordcloudElement.innerHTML = '';

    console.log('Generating word cloud with data:', wordData);

    if (!wordData || wordData.length === 0) {
        wordcloudElement.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #6c757d; font-size: 16px; text-align: center;">
                <div>
                    <i class="fas fa-exclamation-circle" style="font-size: 48px; margin-bottom: 15px; display: block;"></i>
                    <p>No word cloud data available</p>
                    <p style="font-size: 14px; margin-top: 10px;">Try adding more content to your platform</p>
                </div>
            </div>
        `;

        if (wordcloudStats) {
            wordcloudStats.innerHTML = 'No keywords found in platform content';
        }
        return;
    }

    try {
        // 更新统计信息
        if (wordcloudStats) {
            const totalWords = wordData.length;
            const topWord = wordData[0];
            wordcloudStats.innerHTML = `Displaying ${totalWords} keywords. Most frequent: "${topWord.text}" (${topWord.freq} occurrences)`;
        }

        // 准备词云数据 - 确保格式正确
        const wordList = wordData.map(item => {
            // 确保text是字符串，weight是数字
            const text = String(item.text || '');
            const weight = Number(item.weight || 5);
            return [text, weight];
        }).filter(item => item[0] && item[1] > 0);

        console.log('Processed word list:', wordList);

        if (wordList.length === 0) {
            throw new Error('No valid words for word cloud');
        }

        // 生成词云
        WordCloud(wordcloudElement, {
            list: wordList,
            gridSize: Math.round(16 * wordcloudElement.offsetWidth / 1024),
            weightFactor: function(size) {
                return Math.pow(size, 2.3) * wordcloudElement.offsetWidth / 1024;
            },
            fontFamily: 'Arial, Helvetica, sans-serif',
            color: function(word, weight) {
                return (weight >= 15) ? '#667eea' :
                       (weight >= 10) ? '#4facfe' :
                       (weight >= 7) ? '#00f2fe' :
                       (weight >= 5) ? '#764ba2' : '#f093fb';
            },
            rotateRatio: 0.5,
            rotationSteps: 2,
            backgroundColor: '#ffffff',
            minSize: 8,
            drawOutOfBound: false,
            shrinkToFit: true,
            ellipticity: 0.8,
            hover: function(item, dimension, event) {
                if (!item) return;
                console.log('Word hover:', item);
            }
        });

        console.log('Word cloud generated successfully');

    } catch (error) {
        console.error('Error generating word cloud:', error);
        wordcloudElement.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #6c757d; font-size: 16px; text-align: center;">
                <div>
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; margin-bottom: 15px; display: block;"></i>
                    <p>Error generating word cloud</p>
                    <p style="font-size: 14px; margin-top: 10px;">${error.message}</p>
                </div>
            </div>
        `;

        if (wordcloudStats) {
            wordcloudStats.innerHTML = 'Error generating word cloud visualization';
        }
    }
}

async function exportData() {
    try {
        alert('Export feature would be implemented here');
        // 实际的导出实现
    } catch (error) {
        console.error('Error exporting data:', error);
        alert('Failed to export data');
    }
}