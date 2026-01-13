"""
 * @Author：cyg
 * @Package：SystemController
 * @Project：Default (Template) Project
 * @name：SystemController
 * @Date：2025/5/6 15:36
 * @Filename：SystemController
"""
from flask.views import MethodView

from demo import demo
from demo.controller import admin_required
from demo.schema.AuthMenuSchema import AuthMenuListSchema, AuthMenuSaveSchema, AuthMenuDeleteSchema, MenuListResponseSchema
from demo.service.AuthMenuService import AuthMenuService
from demo.schema.SystemConfigSchema import SystemConfigListQuery, SystemConfigRecord, SystemConfigSaveQuery, SystemConfigDeleteQuery
from demo.service.SystemConfigService import SysConfigService
from fred_framework.common.PageSchema import PageSchemaFactory


@demo.route("/system/menu")
class MenuController(MethodView):
	"""
	系统管理
	"""

	@admin_required
	@demo.arguments(AuthMenuListSchema, location='query')
	@demo.response(200, PageSchemaFactory(MenuListResponseSchema))
	def get(self, args):
		"""
			菜单管理
		"""
		return AuthMenuService().menu_list(args)

	@admin_required
	@demo.arguments(AuthMenuSaveSchema)
	@demo.response(200)
	def post(self, args):
		"""
		新增菜单
		"""
		return AuthMenuService().add_menu(args)

	@admin_required
	@demo.arguments(AuthMenuSaveSchema)
	@demo.response(200)
	def put(self, args):
		"""
		修改菜单
		"""
		return AuthMenuService().update_menu(args)

	@admin_required
	@demo.arguments(AuthMenuDeleteSchema, location='query')
	@demo.response(200)
	def delete(self, args):
		"""
		删除菜单
		"""
		return AuthMenuService().delete_menu(args)

	@admin_required
	@demo.arguments(AuthMenuDeleteSchema)
	@demo.response(200)
	def patch(self, args):
		"""
		恢复菜单
		"""
		return AuthMenuService().restore_menu(args)


@demo.route("/system/config")
class SystemConfigController(MethodView):
	"""
	系统配置管理
	"""

	@admin_required
	@demo.arguments(SystemConfigListQuery, location='query')
	@demo.response(200, PageSchemaFactory(SystemConfigRecord))
	def get(self, args):
		"""
		系统配置列表
		"""
		return SysConfigService().config_list(args)

	@admin_required
	@demo.arguments(SystemConfigSaveQuery)
	@demo.response(200)
	def post(self, args):
		"""
		新增系统配置
		"""
		return SysConfigService().config_save(args)

	@admin_required
	@demo.arguments(SystemConfigSaveQuery)
	@demo.response(200)
	def put(self, args):
		"""
		修改系统配置
		"""
		return SysConfigService().config_save(args)

	@admin_required
	@demo.arguments(SystemConfigDeleteQuery, location='query')
	@demo.response(200)
	def delete(self, args):
		"""
		删除系统配置
		"""
		return SysConfigService().config_delete(args)
