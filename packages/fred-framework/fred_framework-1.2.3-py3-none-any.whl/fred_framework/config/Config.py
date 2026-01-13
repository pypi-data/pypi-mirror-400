from datetime import timedelta
from pathlib import Path
import os

class Config:
	"""
	 appliction config
	 custom config use CUSTOM_ For prefix
	"""
	PROJECT_ROOT = ""  # 项目根目录（配置文件在 项目根目录/config/Config.py）

	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:pwd@127.0.0.1:3306/db'
	# SQLALCHEMY_BINDS = {'otherdb':'mysql+pymysql://user:pwd@127.0.0.1:3306/db'}
	ENABLE_SWAGGER = True
	# Redis连接配置
	REDIS_URL = ""
	#REDIS_URL = "redis://:pwd@127.0.0.1:6379/1"
	#返回数据是否加密
	ENCRYPT_DATA = False
	# 是否启用全局异常处理
	ENABLE_GLOBAL_EXCEPTION = False

	#默认密码
	DEFAULT_PASSWORD = 'Fred@2025'
	
	# 配置邮件发送
	MAIL_SERVER = ''  # 你的邮件服务器地址
	MAIL_PORT = 25  # 你的邮件服务器端口
	MAIL_USE_TLS = True  # 是否使用 TLS
	MAIL_USERNAME = ''  # 你的邮箱用户名
	MAIL_PASSWORD = ''  # 你的邮箱密码
	MAIL_DEFAULT_SENDER = ''  # 默认发件人
	
	# JWT 配置
	JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=2)  # 有效时长
	JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
	
	# 国际化默认配置
	BABEL_DEFAULT_LOCALE = 'zh'
	BABEL_DEFAULT_TIMEZONE = 'UTC'
	
	# 使用绝对路径指向项目根目录下的translations目录
	BABEL_TRANSLATION_DIRECTORIES = os.path.join(PROJECT_ROOT, 'translations')
	
	SUPPORTED_LANGUAGES = ['en', 'zh']
	
	# Swagger UI 使用flask_smorest
	API_TITLE = 'FredFrameApi'
	API_VERSION = 'v1'
	OPENAPI_VERSION = '3.0.2'
	OPENAPI_URL_PREFIX = '/'
	OPENAPI_SWAGGER_UI_PATH = '/docs' #swagger 访问地址

	
	# Swagger  参数配置
	SPEC_KWARGS = {
		'components': {
			'securitySchemes': {
				'bearerAuth': {
					'type': 'http',
					'scheme': 'bearer',
					'bearerFormat': 'JWT'
				}
			}
		},
		'security': [{'bearerAuth': []}]  # 配置了默认方案 header中才会有Authorization
	}
	
	# aliyun Sms
	ALIBABA_SIGN_NAME = ''
	ALIBABA_KEY_ID = ''
	ALIBABA_KEY_SECRET = ''
	ALIBABA_TEMPLATE_CODE = ''
	
	# 日志配置
	LOG_LEVEL = 'DEBUG'
	LOG_FILE = 'logs/app.log'
	LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	
	#  定时任务 scheduler 配置
	SCHEDULER_API_ENABLED = True
	SCHEDULER_TIMEZONE = 'Asia/Shanghai'
	JOBS = []

	#  加载自定义模块 如果没有指定 将自动加载所有模块
	LOAD_CUSTOM_MODULES = []
	
	# 首页加载模块 如果不配置 默认根目录下第一个模块
	# HOME_MODULES = ""
	
	

	# 路由与文件夹映射配置
	# 格式: '路由前缀': '实际文件夹路径'
	# 系统会自动注册 /<路由前缀>/<path> 路由，并映射到对应文件夹
	ROUTE_CONFIG = {
		'upload': 'upload',       # /upload/<path> -> upload/
		'download': 'download'   # /download/<path> -> download/
	}