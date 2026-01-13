"""
 * @Author：cyg
 * @Package：AuthButtonsController
 * @Project：Default (Template) Project
 * @name：AuthButtonsController
 * @Date：2025/4/25 14:18
 * @Filename：AuthButtonsController
"""
from flask.views import MethodView

from demo import demo
from demo.controller import admin_required
from demo.service.AuthButtonsService import AuthButtonsService
from demo.service.AuthMenuService import AuthMenuService
# Schema 已定义，但不再使用装饰器序列化，直接返回数据让框架处理


@demo.route("/admin_auth/buttons")
class AuthButtonsController(MethodView):
	
	@admin_required
	def get(self):
		"""
		获取按钮的权限
		"""
		
		data = AuthButtonsService().get_button_list()
		return data


@demo.route("/admin_auth/menu")
class AuthMenuController(MethodView):
	
	@admin_required
	def get(self):
		"""
		获取用户权限菜单
		"""
		return AuthMenuService().admin_menu()
