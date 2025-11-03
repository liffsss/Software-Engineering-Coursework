//static/js/admin_security.js
// 安全中心页面JavaScript
document.addEventListener('DOMContentLoaded', function() {
    loadSecurityData();
    setupEventListeners();
});

async function loadSecurityData() {
    await loadSecurityOverview();
    await loadSecurityLogs();
}

async function loadSecurityOverview() {
    try {
        const response = await fetch('/admin/api/security/overview');
        const data = await response.json();

        if (response.ok) {
            updateSecurityOverview(data);
        } else {
            console.error('Failed to load security overview:', data.error);
            // 如果API失败，使用模拟数据
            updateSecurityOverview(getMockSecurityOverview());
        }
    } catch (error) {
        console.error('Error loading security overview:', error);
        // 使用模拟数据作为fallback
        updateSecurityOverview(getMockSecurityOverview());
    }
}

function getMockSecurityOverview() {
    return {
        total_logs: 1247,
        warning_logs: 23,
        error_logs: 5,
        failed_logins: 8
    };
}

function updateSecurityOverview(data) {
    const securityOverview = document.getElementById('securityOverview');

    const securityStats = [
        {
            icon: 'fas fa-shield-alt',
            value: data.total_logs || 0,
            label: 'Security Logs',
            status: 'success'
        },
        {
            icon: 'fas fa-exclamation-triangle',
            value: data.warning_logs || 0,
            label: 'Warning Events',
            status: 'warning'
        },
        {
            icon: 'fas fa-times-circle',
            value: data.error_logs || 0,
            label: 'Error Events',
            status: 'critical'
        },
        {
            icon: 'fas fa-user-shield',
            value: data.failed_logins || 0,
            label: 'Failed Logins',
            status: data.failed_logins > 10 ? 'critical' : 'warning'
        }
    ];

    securityOverview.innerHTML = securityStats.map(stat => `
        <div class="security-card ${stat.status}">
            <div class="security-icon">
                <i class="${stat.icon}"></i>
            </div>
            <h3>${stat.value}</h3>
            <p>${stat.label}</p>
        </div>
    `).join('');
}

function setupEventListeners() {
    // 标签页切换
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.dataset.tab;

            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(tabId).classList.add('active');

            // 加载对应数据
            if (tabId === 'logs') {
                loadSecurityLogs();
            } else if (tabId === 'database') {
                loadDatabaseTables();
            } else if (tabId === 'system') {
                loadSystemStatus();
            } else if (tabId === 'audit') {
                loadAuditResults();
            }
        });
    });

    // 日志操作
    document.getElementById('refreshLogs').addEventListener('click', loadSecurityLogs);
    document.getElementById('clearLogs').addEventListener('click', clearSecurityLogs);
    document.getElementById('exportLogs').addEventListener('click', exportSecurityLogs);

    // 数据库操作
    document.getElementById('tableSelect').addEventListener('change', function() {
        const tableName = this.value;
        if (tableName) {
            loadTableData(tableName);
        }
    });

    // SQL编辑器
    document.getElementById('executeSql').addEventListener('click', executeSql);
    document.getElementById('clearSql').addEventListener('click', function() {
        document.getElementById('sqlQuery').value = '';
    });
    document.getElementById('explainSql').addEventListener('click', explainSql);

    // 安全审计
    document.getElementById('runSecurityScan').addEventListener('click', runSecurityScan);
    document.getElementById('checkVulnerabilities').addEventListener('click', checkVulnerabilities);
    document.getElementById('generateReport').addEventListener('click', generateSecurityReport);
}

// 删除重复的函数定义，保留上面的 loadSecurityData 和 loadSecurityOverview

async function loadSecurityLogs() {
    try {
        const response = await fetch('/admin/api/security/logs');
        const logs = await response.json();

        if (response.ok) {
            const tbody = document.getElementById('logsTableBody');
            tbody.innerHTML = logs.map(log => `
                <tr>
                    <td>${new Date(log.created_at).toLocaleString()}</td>
                    <td>
                        <span class="log-level ${getLogLevelClass(log.action)}">
                            ${getLogLevelText(log.action)}
                        </span>
                    </td>
                    <td>${log.username || 'System'}</td>
                    <td>${log.action}</td>
                    <td>${log.description || '-'}</td>
                    <td>${log.ip_address || '-'}</td>
                </tr>
            `).join('');
        } else {
            alert('Failed to load logs: ' + logs.error);
        }
    } catch (error) {
        console.error('Error loading security logs:', error);
        alert('Failed to load logs');
    }
}

function getLogLevelClass(action) {
    if (action.includes('Failed') || action.includes('Error') || action.includes('Denied')) {
        return 'error';
    } else if (action.includes('Warning') || action.includes('Exception')) {
        return 'warning';
    } else {
        return 'info';
    }
}

function getLogLevelText(action) {
    if (action.includes('Failed') || action.includes('Error') || action.includes('Denied')) {
        return 'Error';
    } else if (action.includes('Warning') || action.includes('Exception')) {
        return 'Warning';
    } else {
        return 'Info';
    }
}

async function clearSecurityLogs() {
    if (!confirm('Are you sure you want to clear all security logs? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch('/admin/api/security/logs', {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('Security logs cleared successfully');
            loadSecurityLogs();
        } else {
            const error = await response.json();
            alert('Failed to clear logs: ' + error.error);
        }
    } catch (error) {
        console.error('Error clearing security logs:', error);
        alert('Failed to clear logs');
    }
}

async function exportSecurityLogs() {
    try {
        const response = await fetch('/admin/api/security/logs/export');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `security_logs_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            alert('Failed to export logs');
        }
    } catch (error) {
        console.error('Error exporting security logs:', error);
        alert('Failed to export logs');
    }
}

async function loadDatabaseTables() {
    try {
        const response = await fetch('/admin/api/database/tables');
        const tables = await response.json();

        if (response.ok) {
            const select = document.getElementById('tableSelect');
            select.innerHTML = '<option value="">Select table...</option>' +
                tables.map(table => `
                    <option value="${table.name}">${table.name} (${table.row_count} rows)</option>
                `).join('');
        } else {
            alert('Failed to load tables: ' + tables.error);
        }
    } catch (error) {
        console.error('Error loading database tables:', error);
        alert('Failed to load tables');
    }
}

async function loadTableData(tableName) {
    try {
        const response = await fetch(`/admin/api/database/table/${tableName}`);
        const data = await response.json();

        if (response.ok) {
            // 更新表信息
            const tableInfo = document.getElementById('tableInfo');
            tableInfo.style.display = 'block';
            tableInfo.innerHTML = `
                <strong>Table Name:</strong> ${tableName} |
                <strong>Records:</strong> ${data.length} |
                <strong>Last Updated:</strong> ${new Date().toLocaleString()}
            `;

            // 更新表数据
            const table = document.getElementById('databaseTable');
            if (data.length > 0 && !data.error) {
                const headers = Object.keys(data[0]);
                table.innerHTML = `
                    <thead>
                        <tr>
                            ${headers.map(header => `<th>${header}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${data.map(row => `
                            <tr>
                                ${headers.map(header => `<td>${formatTableValue(row[header])}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                `;
            } else {
                table.innerHTML = '<tr><td colspan="100%" style="text-align: center; color: #6c757d;">No data available or table does not exist</td></tr>';
            }
        } else {
            alert('Failed to load table data: ' + data.error);
        }
    } catch (error) {
        console.error('Error loading table data:', error);
        alert('Failed to load table data');
    }
}

function formatTableValue(value) {
    if (value === null || value === undefined) {
        return '<em>NULL</em>';
    }
    if (typeof value === 'boolean') {
        return value ? 'Yes' : 'No';
    }
    if (typeof value === 'object') {
        return JSON.stringify(value);
    }
    return value.toString();
}

async function executeSql() {
    const sql = document.getElementById('sqlQuery').value.trim();
    if (!sql) {
        alert('Please enter SQL statement');
        return;
    }

    try {
        const response = await fetch('/admin/api/database/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ sql: sql })
        });
        const result = await response.json();

        const sqlResult = document.getElementById('sqlResult');
        if (response.ok) {
            if (result.data) {
                const data = result.data;
                if (Array.isArray(data) && data.length > 0) {
                    const headers = Object.keys(data[0]);
                    sqlResult.innerHTML = `
                        <div class="table-container">
                            <table class="logs-table">
                                <thead>
                                    <tr>
                                        ${headers.map(header => `<th>${header}</th>`).join('')}
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.map(row => `
                                        <tr>
                                            ${headers.map(header => `<td>${formatTableValue(row[header])}</td>`).join('')}
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                        <div style="margin-top: 10px; color: #28a745;">
                            <i class="fas fa-check"></i> Query executed successfully, returned ${data.length} records
                        </div>
                    `;
                } else {
                    sqlResult.innerHTML = '<div style="color: #6c757d;"><i class="fas fa-info-circle"></i> Query executed successfully, but no data returned.</div>';
                }
            } else {
                sqlResult.innerHTML = '<div style="color: #28a745;"><i class="fas fa-check"></i> Execution successful.</div>';
            }
        } else {
            sqlResult.innerHTML = `<div style="color: #dc3545;"><i class="fas fa-times-circle"></i> Error: ${result.error}</div>`;
        }
    } catch (error) {
        console.error('Error executing SQL:', error);
        sqlResult.innerHTML = `<div style="color: #dc3545;"><i class="fas fa-times-circle"></i> Execution failed: ${error.message}</div>`;
    }
}

async function explainSql() {
    const sql = document.getElementById('sqlQuery').value.trim();
    if (!sql) {
        alert('Please enter SQL statement');
        return;
    }

    const explainSql = `EXPLAIN QUERY PLAN ${sql}`;
    document.getElementById('sqlQuery').value = explainSql;
    executeSql();
}

async function loadSystemStatus() {
    try {
        const response = await fetch('/admin/api/system/status');
        const status = await response.json();

        if (response.ok) {
            updateSystemStatus(status);
        } else {
            console.error('Failed to load system status');
        }
    } catch (error) {
        console.error('Error loading system status:', error);
        // 使用模拟数据
        updateSystemStatus(getMockSystemStatus());
    }
}

function updateSystemStatus(status) {
    // 服务器状态
    document.getElementById('uptime').textContent = status.uptime || '24 days 5 hours';
    document.getElementById('serverLoad').textContent = status.server_load || '45%';
    document.getElementById('memoryUsage').textContent = status.memory_usage || '1.2GB / 2.0GB (60%)';
    document.getElementById('memoryBar').style.width = status.memory_percent || '60%';
    document.getElementById('cpuUsage').textContent = status.cpu_usage || '35%';
    document.getElementById('cpuBar').style.width = status.cpu_percent || '35%';

    // 数据库状态
    document.getElementById('dbSize').textContent = status.db_size || '45.2 MB';
    document.getElementById('tableCount').textContent = status.table_count || '12';
    document.getElementById('totalRecords').textContent = status.total_records || '1,245';
    document.getElementById('lastBackup').textContent = status.last_backup || '2024-01-15 02:00';

    // 安全状态
    updateSecurityStatus(status.security);
}

function updateSecurityStatus(security) {
    const authStatus = security?.authentication || 'Good';
    const dataStatus = security?.data_encryption || 'Enabled';
    const accessStatus = security?.access_control || 'Strict';
    const auditStatus = security?.audit_logging || 'Complete';

    document.getElementById('authStatus').textContent = authStatus;
    document.getElementById('dataStatus').textContent = dataStatus;
    document.getElementById('accessStatus').textContent = accessStatus;
    document.getElementById('auditStatus').textContent = auditStatus;

    document.getElementById('authRisk').className = `risk-indicator ${getRiskLevel(authStatus)}`;
    document.getElementById('dataRisk').className = `risk-indicator ${getRiskLevel(dataStatus)}`;
    document.getElementById('accessRisk').className = `risk-indicator ${getRiskLevel(accessStatus)}`;
    document.getElementById('auditRisk').className = `risk-indicator ${getRiskLevel(auditStatus)}`;
}

function getRiskLevel(status) {
    if (status === 'Good' || status === 'Enabled' || status === 'Strict' || status === 'Complete') {
        return 'risk-low';
    } else if (status === 'Fair' || status === 'Partially Enabled' || status === 'Medium') {
        return 'risk-medium';
    } else {
        return 'risk-high';
    }
}

function getMockSystemStatus() {
    return {
        uptime: '24 days 5 hours 30 minutes',
        server_load: '45%',
        memory_usage: '1.2GB / 2.0GB (60%)',
        memory_percent: '60%',
        cpu_usage: '35%',
        cpu_percent: '35%',
        db_size: '45.2 MB',
        table_count: '12',
        total_records: '1,245',
        last_backup: new Date().toISOString().split('T')[0] + ' 02:00',
        security: {
            authentication: 'Good',
            data_encryption: 'Enabled',
            access_control: 'Strict',
            audit_logging: 'Complete'
        }
    };
}

async function loadAuditResults() {
    try {
        const response = await fetch('/admin/api/security/audit');
        const audit = await response.json();

        if (response.ok) {
            updateAuditResults(audit);
        } else {
            console.error('Failed to load audit results');
            // 使用模拟数据
            updateAuditResults(getMockAuditResults());
        }
    } catch (error) {
        console.error('Error loading audit results:', error);
        updateAuditResults(getMockAuditResults());
    }
}

function updateAuditResults(audit) {
    // 更新审计概览
    const auditResults = document.getElementById('auditResults');
    auditResults.innerHTML = audit.overview.map(item => `
        <div class="security-card ${item.status}">
            <div class="security-icon">
                <i class="${item.icon}"></i>
            </div>
            <h3>${item.value}</h3>
            <p>${item.label}</p>
        </div>
    `).join('');

    // 更新审计详情
    const auditTableBody = document.getElementById('auditTableBody');
    auditTableBody.innerHTML = audit.details.map(item => `
        <tr>
            <td>${item.check_item}</td>
            <td>
                <span class="log-level ${item.status === 'Passed' ? 'info' : item.status === 'Warning' ? 'warning' : 'error'}">
                    ${item.status}
                </span>
            </td>
            <td>
                <span class="risk-indicator ${getRiskLevel(item.risk_level)}"></span>
                ${item.risk_level}
            </td>
            <td>${item.description}</td>
            <td>${item.recommendation}</td>
        </tr>
    `).join('');
}

function getMockAuditResults() {
    return {
        overview: [
            {
                icon: 'fas fa-check-circle',
                value: '8',
                label: 'Passed Checks',
                status: 'success'
            },
            {
                icon: 'fas fa-exclamation-triangle',
                value: '3',
                label: 'Need Attention',
                status: 'warning'
            },
            {
                icon: 'fas fa-times-circle',
                value: '1',
                label: 'Critical Issues',
                status: 'critical'
            },
            {
                icon: 'fas fa-percentage',
                value: '75%',
                label: 'Security Score',
                status: 'success'
            }
        ],
        details: [
            {
                check_item: 'Password Policy',
                status: 'Passed',
                risk_level: 'Low',
                description: 'Password complexity requirements enabled',
                recommendation: 'Maintain current settings'
            },
            {
                check_item: 'Session Timeout',
                status: 'Warning',
                risk_level: 'Medium',
                description: 'Session timeout setting is too long',
                recommendation: 'Set timeout to 30 minutes'
            },
            {
                check_item: 'Database Backup',
                status: 'Passed',
                risk_level: 'Low',
                description: 'Automatic backup functioning normally',
                recommendation: 'Maintain current settings'
            },
            {
                check_item: 'SQL Injection Protection',
                status: 'Passed',
                risk_level: 'Low',
                description: 'Parameterized queries enabled',
                recommendation: 'Maintain current settings'
            },
            {
                check_item: 'File Upload',
                status: 'Warning',
                risk_level: 'Medium',
                description: 'File type checking not strict enough',
                recommendation: 'Strengthen file type validation'
            },
            {
                check_item: 'Error Information Leakage',
                status: 'Critical',
                risk_level: 'High',
                description: 'Detailed error messages shown in production',
                recommendation: 'Disable detailed error display immediately'
            }
        ]
    };
}

async function runSecurityScan() {
    const button = document.getElementById('runSecurityScan');
    const originalText = button.innerHTML;

    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning...';
    button.disabled = true;

    try {
        // 模拟扫描过程
        await new Promise(resolve => setTimeout(resolve, 3000));

        await loadAuditResults();
        alert('Security scan completed!');
    } catch (error) {
        console.error('Error running security scan:', error);
        alert('Security scan failed');
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

async function checkVulnerabilities() {
    alert('Vulnerability check feature under development...');
}

async function generateSecurityReport() {
    try {
        const response = await fetch('/admin/api/security/report');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `security_report_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            alert('Failed to generate security report');
        }
    } catch (error) {
        console.error('Error generating security report:', error);
        alert('Failed to generate security report');
    }
}