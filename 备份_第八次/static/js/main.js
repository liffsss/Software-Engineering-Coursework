// Flash消息自动消失
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.alert');

    flashMessages.forEach(message => {
        // 5秒后自动消失
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s ease-out';

            // 动画完成后移除元素
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);

        // 点击关闭按钮
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.style.background = 'none';
        closeButton.style.border = 'none';
        closeButton.style.fontSize = '20px';
        closeButton.style.cursor = 'pointer';
        closeButton.style.marginLeft = 'auto';
        closeButton.style.padding = '0';
        closeButton.style.width = '20px';
        closeButton.style.height = '20px';
        closeButton.style.display = 'flex';
        closeButton.style.alignItems = 'center';
        closeButton.style.justifyContent = 'center';

        closeButton.addEventListener('click', function() {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.3s ease-out';

            setTimeout(() => {
                message.remove();
            }, 300);
        });

        message.appendChild(closeButton);
    });
});