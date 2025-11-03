import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    DATABASE = 'database/komodo_hub.db'
    DEBUG = True

    # 添加语言配置 - 将默认语言设置为英文
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['en', 'zh']
    LANGUAGE = 'en'

    # 如果需要，也可以添加时区配置
    BABEL_DEFAULT_TIMEZONE = 'UTC'