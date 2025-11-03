//static/js/admin_users.js
document.addEventListener('DOMContentLoaded', function() {
    const userEditModal = document.getElementById('userEditModal');
    const deleteUserConfirmModal = document.getElementById('deleteUserConfirmModal');
    const userForm = document.getElementById('userForm');
    let currentUserId = null;

    // 打开新增用户模态框
    document.getElementById('addUserBtn').addEventListener('click', function() {
        document.getElementById('userModalTitle').textContent = 'Add User';
        userForm.reset();
        document.getElementById('userId').value = '';
        document.getElementById('password').required = true;
        userEditModal.style.display = 'block';
    });

    // 编辑用户
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('edit-user')) {
            const userId = e.target.dataset.userId;
            loadUserData(userId);
        } else if (e.target.classList.contains('delete-user')) {
            currentUserId = e.target.dataset.userId;
            deleteUserConfirmModal.style.display = 'block';
        }
    });

    // 加载用户数据
    async function loadUserData(userId) {
        try {
            const response = await fetch(`/admin/api/users`);
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
                userEditModal.style.display = 'block';
            }
        } catch (error) {
            console.error('Error loading user data:', error);
            alert('Failed to load user data');
        }
    }

    // 提交用户表单
    userForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(userForm);
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
                userEditModal.style.display = 'none';
                location.reload(); // 刷新页面以更新列表
            } else {
                const error = await response.json();
                alert(error.error || 'Operation failed');
            }
        } catch (error) {
            console.error('Error saving user:', error);
            alert('Save failed');
        }
    });

    // 删除用户确认
    document.getElementById('confirmUserDelete').addEventListener('click', async function() {
        if (!currentUserId) return;

        try {
            const response = await fetch(`/admin/api/users/${currentUserId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                alert('User deleted successfully');
                deleteUserConfirmModal.style.display = 'none';
                location.reload(); // 刷新页面以更新列表
            } else {
                const error = await response.json();
                alert(error.error || 'Delete failed');
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            alert('Delete failed');
        }
    });

    // 取消删除
    document.getElementById('cancelUserDelete').addEventListener('click', function() {
        deleteUserConfirmModal.style.display = 'none';
        currentUserId = null;
    });

    // 关闭模态框
    document.querySelectorAll('.close, .cancel-btn').forEach(button => {
        button.addEventListener('click', function() {
            userEditModal.style.display = 'none';
            deleteUserConfirmModal.style.display = 'none';
        });
    });

    // 点击模态框外部关闭
    window.addEventListener('click', function(event) {
        if (event.target === userEditModal) {
            userEditModal.style.display = 'none';
        }
        if (event.target === deleteUserConfirmModal) {
            deleteUserConfirmModal.style.display = 'none';
        }
    });
});