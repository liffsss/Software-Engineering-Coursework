document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.login-form');
    form.addEventListener('submit', function (event) {
        console.log('表单即将提交');
    });
});