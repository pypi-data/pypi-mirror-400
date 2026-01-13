# 路由控制
import json

from flask import request, session, abort, current_app
from flask_babelplus import gettext
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, get_jwt
from six import wraps

from demo import demo
from demo.service.AuthButtonsService import AuthButtonsService
from fred_framework.common.Utils import Utils
from model.model import Admin


def admin_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		verify_jwt_in_request()
		claims = get_jwt()
		redis_client = current_app.extensions.get('redis')
		jti = claims.get('jti')
		if claims.get('role') != demo.name:
			abort(401, description=gettext('未登录或登录失效!'))
		if redis_client and redis_client.get(jti):
			abort(401, description="Token 已注销，请重新登录")
		key = f'{demo.name}_user_info'
		if session.get(key) is None:
			abort(401, description=gettext('未登录或登录失效.'))

		return f(*args, **kwargs)

	return wrapper


@demo.before_request
def get_admin_info():
	admin_info = None

	try:
		verify_jwt_in_request()
		claims = get_jwt()
		info = json.loads(get_jwt_identity())
		if claims.get('role') == demo.name:
			admin_info = Utils.query_to_dict(Admin.query.filter_by(id=info['id']).first())
			#TODO: 需要优化，这里每次请求都会查询一次权限，可以考虑缓存 需要验证path格式
			is_auth = AuthButtonsService().check_api_permission(admin_info['id'], request.path, request.method)
			if not is_auth:
				abort(401, description=gettext('无权限访问'))

	except:
		pass

	key = f'{demo.name}_user_info'
	session[key] = admin_info
	return None
