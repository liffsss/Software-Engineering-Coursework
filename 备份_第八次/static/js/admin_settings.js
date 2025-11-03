//static/js/admin_settings.js
// 系统设置页面JavaScript
document.addEventListener('DOMContentLoaded', function() {
    loadSystemSettings();
    setupEventListeners();
});

function setupEventListeners() {
    // 设置侧边栏导航
    document.querySelectorAll('.settings-sidebar .nav-item').forEach(item => {
        item.addEventListener('click', function() {
            const sectionId = this.dataset.section;

            // 更新激活的导航项
            document.querySelectorAll('.settings-sidebar .nav-item').forEach(nav => {
                nav.classList.remove('active');
            });
            this.classList.add('active');

            // 显示对应的设置部分
            document.querySelectorAll('.settings-section').forEach(section => {
                section.classList.remove('active');
            });
            document.getElementById(sectionId).classList.add('active');
        });
    });

    // 用户角色标签
    document.querySelectorAll('.role-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const role = this.dataset.role;

            document.querySelectorAll('.role-tab').forEach(t => {
                t.classList.remove('active');
            });
            this.classList.add('active');

            document.querySelectorAll('.role-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${role}-management`).classList.add('active');

            loadUsersByRole(role);
        });
    });

    // 主题选择
    document.querySelectorAll('.theme-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.theme-option').forEach(opt => {
                opt.classList.remove('active');
            });
            this.classList.add('active');
        });
    });

    // 颜色选择
    document.querySelectorAll('.color-swatch').forEach(swatch => {
        swatch.addEventListener('click', function() {
            document.querySelectorAll('.color-swatch').forEach(s => {
                s.classList.remove('active');
            });
            this.classList.add('active');
        });
    });

    // 布局选择
    document.querySelectorAll('.layout-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.layout-option').forEach(opt => {
                opt.classList.remove('active');
            });
            this.classList.add('active');
        });
    });

    // 保存设置
    document.getElementById('saveSettings').addEventListener('click', saveSystemSettings);

    // 恢复默认
    document.getElementById('resetSettings').addEventListener('click', resetSystemSettings);

    // 备份操作
    document.getElementById('backupBtn').addEventListener('click', createBackup);
    document.getElementById('restoreBtn').addEventListener('click', restoreBackup);
    document.getElementById('downloadLogsBtn').addEventListener('click', downloadLogs);

    // 初始加载学生用户
    loadUsersByRole('student');
}

async function loadSystemSettings() {
    try {
        const response = await fetch('/admin/api/system_settings');
        const settings = await response.json();

        if (response.ok) {
            // 更新表单字段
            if (settings.system_theme) {
                const themeOption = document.querySelector(`.theme-option[data-theme="${settings.system_theme}"]`);
                if (themeOption) {
                    document.querySelectorAll('.theme-option').forEach(opt => opt.classList.remove('active'));
                    themeOption.classList.add('active');
                }
            }

            if (settings.background_color) {
                const colorSwatch = document.querySelector(`.color-swatch[data-color="${settings.background_color}"]`);
                if (colorSwatch) {
                    document.querySelectorAll('.color-swatch').forEach(swatch => swatch.classList.remove('active'));
                    colorSwatch.classList.add('active');
                }
            }

            if (settings.layout_style) {
                const layoutOption = document.querySelector(`.layout-option[data-layout="${settings.layout_style}"]`);
                if (layoutOption) {
                    document.querySelectorAll('.layout-option').forEach(opt => opt.classList.remove('active'));
                    layoutOption.classList.add('active');
                }
            }

            if (settings.max_articles_per_page) {
                document.getElementById('max_articles').value = settings.max_articles_per_page;
            }

            // 其他设置字段...
            if (settings.maintenance_mode) {
                document.getElementById('maintenance_mode').checked = settings.maintenance_mode === 'true';
            }

            if (settings.allow_registration) {
                document.getElementById('allow_registration').checked = settings.allow_registration === 'true';
            }

            if (settings.session_timeout) {
                document.getElementById('session_timeout').value = settings.session_timeout;
            }

            if (settings.backup_interval) {
                document.getElementById('backup_interval').value = settings.backup_interval;
            }
        } else {
            alert('Failed to load settings: ' + settings.error);
        }
    } catch (error) {
        console.error('Error loading system settings:', error);
        alert('Failed to load settings');
    }
}

async function loadUsersByRole(role) {
    try {
        const response = await fetch('/admin/api/users');
        const users = await response.json();

        if (response.ok) {
            const filteredUsers = users.filter(user => user.role === role);
            const tableId = `${role}sTable`;
            const tableBody = document.getElementById(tableId);

            if (filteredUsers.length > 0) {
                tableBody.innerHTML = filteredUsers.map(user => `
                    <tr data-user-id="${user.id}">
                        <td>${user.username}</td>
                        <td>${user.full_name || '-'}</td>
                        <td>${user.org_name || '-'}</td>
                        <td>${new Date(user.created_at).toLocaleDateString()}</td>
                        <td>${user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never logged in'}</td>
                        <td class="actions">
                            <button class="btn btn-secondary btn-sm edit-user" data-user-id="${user.id}">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-danger btn-sm delete-user" data-user-id="${user.id}">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </td>
                    </tr>
                `).join('');

                // 绑定编辑和删除事件
                bindUserActions();
            } else {
                tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #6c757d;">No users available</td></tr>';
            }
        } else {
            alert('Failed to load users: ' + users.error);
        }
    } catch (error) {
        console.error('Error loading users:', error);
        alert('Failed to load users');
    }
}

function bindUserActions() {
    // 编辑用户
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('edit-user') || e.target.parentElement.classList.contains('edit-user')) {
            const userId = e.target.dataset.userId || e.target.parentElement.dataset.userId;
            editUser(userId);
        } else if (e.target.classList.contains('delete-user') || e.target.parentElement.classList.contains('delete-user')) {
            const userId = e.target.dataset.userId || e.target.parentElement.dataset.userId;
            deleteUser(userId);
        }
    });
}

async function editUser(userId) {
    try {
        const response = await fetch('/admin/api/users');
        const users = await response.json();
        const user = users.find(u => u.id == userId);

        if (user) {
            document.getElementById('userModalTitle').textContent = 'Edit User';
            document.getElementById('userId').value = user.id;
            document.getElementById('username').value = user.username;
            document.getElementById('role').value = user.role;
            document.getElementById('full_name').value = user.full_name || '';
            document.getElementById('org_name').value = user.org_name || '';
            document.getElementById('password').required = false;
            document.getElementById('password').placeholder = 'Leave blank to keep current password';

            // 显示模态框
            document.getElementById('userEditModal').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading user data:', error);
        alert('Failed to load user data');
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/admin/api/users/${userId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('User deleted successfully');
            // 重新加载当前角色用户
            const activeRole = document.querySelector('.role-tab.active').dataset.role;
            loadUsersByRole(activeRole);
        } else {
            const error = await response.json();
            alert(error.error || 'Delete failed');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Delete failed');
    }
}

async function saveSystemSettings() {
    const settings = {
        system_theme: document.querySelector('.theme-option.active')?.dataset.theme || 'default',
        background_color: document.querySelector('.color-swatch.active')?.dataset.color || '#ffffff',
        layout_style: document.querySelector('.layout-option.active')?.dataset.layout || 'standard',
        max_articles_per_page: document.getElementById('max_articles').value,
        maintenance_mode: document.getElementById('maintenance_mode').checked.toString(),
        allow_registration: document.getElementById('allow_registration').checked.toString(),
        session_timeout: document.getElementById('session_timeout').value,
        backup_interval: document.getElementById('backup_interval').value
    };

    try {
        const response = await fetch('/admin/api/system_settings', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings)
        });

        if (response.ok) {
            alert('System settings saved successfully');
            // 应用设置到当前页面
            applySystemSettings(settings);
        } else {
            const error = await response.json();
            alert(error.error || 'Save failed');
        }
    } catch (error) {
        console.error('Error saving system settings:', error);
        alert('Save failed');
    }
}

function applySystemSettings(settings) {
    // 应用背景颜色
    document.body.style.backgroundColor = settings.background_color;

    // 这里可以添加更多实时应用设置的逻辑
    console.log('System settings applied:', settings);
}

function resetSystemSettings() {
    if (confirm('Are you sure you want to restore default settings? All custom settings will be lost.')) {
        // 重置表单字段到默认值
        document.querySelector('.theme-option[data-theme="default"]').classList.add('active');
        document.querySelector('.color-swatch[data-color="#ffffff"]').classList.add('active');
        document.querySelector('.layout-option[data-layout="standard"]').classList.add('active');
        document.getElementById('max_articles').value = 10;
        document.getElementById('maintenance_mode').checked = false;
        document.getElementById('allow_registration').checked = true;
        document.getElementById('session_timeout').value = 60;
        document.getElementById('backup_interval').value = 7;

        alert('Settings have been reset to default values. Please click Save to apply.');
    }
}

async function createBackup() {
    try {
        const response = await fetch('/admin/api/system/backup', {
            method: 'POST'
        });

        if (response.ok) {
            alert('Database backup created successfully');
            loadBackupFiles();
        } else {
            const error = await response.json();
            alert('Backup failed: ' + error.error);
        }
    } catch (error) {
        console.error('Error creating backup:', error);
        alert('Backup failed');
    }
}

async function restoreBackup() {
    alert('Restore backup feature under development...');
}

async function downloadLogs() {
    try {
        const response = await fetch('/admin/api/system/logs/download');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `system_logs_${new Date().toISOString().split('T')[0]}.log`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            alert('Failed to download logs');
        }
    } catch (error) {
        console.error('Error downloading logs:', error);
        alert('Failed to download logs');
    }
}

async function loadBackupFiles() {
    // 这里应该从后端获取备份文件列表
    const backupFiles = document.getElementById('backupFiles');
    backupFiles.innerHTML = `
        <div style="color: #6c757d; text-align: center; padding: 20px;">
            <i class="fas fa-info-circle"></i> Loading backup file list...
        </div>
    `;
}

// 用户表单提交
document.getElementById('userForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const userData = {
        username: formData.get('username'),
        role: formData.get('role'),
        full_name: formData.get('full_name'),
        org_name: formData.get('org_name')
    };

    if (formData.get('password')) {
        userData.password = formData.get('password');
    }

    const userId = formData.get('user_id');
    const url = userId ? `/admin/api/users/${userId}` : '/admin/api/users';
    const method = userId ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        if (response.ok) {
            alert(userId ? 'User updated successfully' : 'User created successfully');
            document.getElementById('userEditModal').style.display = 'none';

            // 重新加载当前角色用户
            const activeRole = document.querySelector('.role-tab.active').dataset.role;
            loadUsersByRole(activeRole);
        } else {
            const error = await response.json();
            alert(error.error || 'Operation failed');
        }
    } catch (error) {
        console.error('Error saving user:', error);
        alert('Save failed');
    }
});

// 关闭模态框
document.querySelectorAll('.close, .cancel-btn').forEach(button => {
    button.addEventListener('click', function() {
        document.getElementById('userEditModal').style.display = 'none';
    });
});

// 点击模态框外部关闭
window.addEventListener('click', function(event) {
    const modal = document.getElementById('userEditModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});