// static/js/admin_dashboard.js
// 添加页面加载动画
document.addEventListener('DOMContentLoaded', function() {
    // 添加卡片动画
    const cards = document.querySelectorAll('.dashboard-card, .article-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('slide-in-left');
    });

    // 添加悬停效果
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });

        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // 添加页面切换动画
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });

    document.querySelectorAll('.settings-section, .tab-content').forEach(section => {
        observer.observe(section);
    });
});

// 加载文章内容
async function loadArticleContent(articleId) {
    try {
        const response = await fetch(`/admin/api/articles/${articleId}`);
        const article = await response.json();

        const modalBody = document.querySelector('#viewArticleModal .modal-body');
        modalBody.innerHTML = `
            <h4>${article.title}</h4>
            <div class="article-meta">
                <span>Author: ${article.author || 'Unknown'}</span>
                <span>Published: ${article.created_at}</span>
            </div>
            <div class="article-content-full">
                ${article.content || 'No content available'}
            </div>
        `;
    } catch (error) {
        console.error('Error loading article:', error);
        alert('Failed to load article');
    }
}

// 加载编辑表单
async function loadEditForm(articleId) {
    try {
        const response = await fetch(`/admin/api/articles/${articleId}`);
        const article = await response.json();

        const modalBody = document.querySelector('#editArticleModal .modal-body');
        modalBody.innerHTML = `
            <form id="editArticleForm">
                <input type="hidden" name="article_id" value="${article.id}">
                <div class="form-group">
                    <label for="editTitle">Title</label>
                    <input type="text" id="editTitle" name="title" value="${article.title}" required>
                </div>
                <div class="form-group">
                    <label for="editContent">Content</label>
                    <textarea id="editContent" name="content" rows="10" required>${article.content || ''}</textarea>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                    <button type="button" class="btn btn-secondary cancel-edit">Cancel</button>
                </div>
            </form>
        `;

        // 添加表单提交事件
        document.getElementById('editArticleForm').addEventListener('submit', handleEditSubmit);
        document.querySelector('.cancel-edit').addEventListener('click', function() {
            document.getElementById('editArticleModal').style.display = 'none';
        });
    } catch (error) {
        console.error('Error loading edit form:', error);
        alert('Failed to load edit form');
    }
}

// 处理文章编辑提交
async function handleEditSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const articleId = formData.get('article_id');

    const articleData = {
        title: formData.get('title'),
        content: formData.get('content')
    };

    try {
        const response = await fetch(`/admin/api/articles/${articleId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(articleData)
        });

        if (response.ok) {
            alert('Article updated successfully');
            document.getElementById('editArticleModal').style.display = 'none';
            location.reload();
        } else {
            const error = await response.json();
            alert(error.error || 'Update failed');
        }
    } catch (error) {
        console.error('Error updating article:', error);
        alert('Update failed');
    }
}

// 删除文章
async function deleteArticle(articleId) {
    try {
        const response = await fetch(`/admin/api/articles/${articleId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('Article deleted successfully');
            document.getElementById('deleteConfirmModal').style.display = 'none';
            location.reload();
        } else {
            const error = await response.json();
            alert(error.error || 'Delete failed');
        }
    } catch (error) {
        console.error('Error deleting article:', error);
        alert('Delete failed');
    }
}

// 模态框功能
document.addEventListener('DOMContentLoaded', function() {
    // 模态框显示/隐藏逻辑
    const modals = document.querySelectorAll('.modal');
    const closeButtons = document.querySelectorAll('.close, .modal .btn-secondary');

    function openModal(modalId) {
        document.getElementById(modalId).style.display = 'block';
    }

    function closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            modal.style.display = 'none';
        });
    });

    window.addEventListener('click', function(event) {
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });

    // 文章操作事件委托
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('view-article')) {
            const articleId = e.target.dataset.articleId;
            loadArticleContent(articleId);
            openModal('viewArticleModal');
        } else if (e.target.classList.contains('edit-article')) {
            const articleId = e.target.dataset.articleId;
            loadEditForm(articleId);
            openModal('editArticleModal');
        } else if (e.target.classList.contains('delete-article')) {
            const articleId = e.target.dataset.articleId;
            document.getElementById('confirmDelete').dataset.articleId = articleId;
            openModal('deleteConfirmModal');
        }
    });

    // 删除确认
    document.getElementById('confirmDelete').addEventListener('click', function() {
        const articleId = this.dataset.articleId;
        deleteArticle(articleId);
    });
});