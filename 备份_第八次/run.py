# run.py
from app import create_app

# 创建 Flask 应用实例
app = create_app()

if __name__ == '__main__':
    # 启动应用，开启调试模式
    app.run(debug=True)