# python3.11
# -*- coding: utf-8 -*-
from flask.views import MethodView

from demo import demo
from demo.controller import admin_required
from demo.schema.AdminSchema import Records
from demo.schema.RoleSchema import AdminRoleListQuery, AdminRoleSaveQuery, AdminRoleDeleteQuery, RoleUserQuery, RoleRemoveUser, RoleRecord, UserRecord, UserRoleQuery, RoleMenuPermissionQuery, RoleButtonPermissionQuery
from demo.service.RoleService import RoleService
from fred_framework.common.PageSchema import PageSchemaFactory


@demo.route("/system/role")
class AdminRoleController(MethodView):

	@admin_required
	@demo.arguments(AdminRoleListQuery, location='query')
	@demo.response(200, PageSchemaFactory(RoleRecord))
	def get(self, args):
		"""
		角色列表
		"""
		return RoleService().role_list(args)

	@admin_required
	@demo.arguments(AdminRoleSaveQuery)
	@demo.response(200)
	def post(self, args):
		"""
		新增角色
		"""
		return RoleService().role_save(args)

	@admin_required
	@demo.arguments(AdminRoleSaveQuery)
	@demo.response(200)
	def put(self, args):
		"""
		修改角色
		"""
		return RoleService().role_save(args)

	@admin_required
	@demo.arguments(AdminRoleDeleteQuery, location='query')
	@demo.response(200)
	def delete(self, args):
		"""
		删除角色
		"""
		return RoleService().role_delete(args)


# 新增角色用户类
@demo.route("/system/role/users")
class RoleUserController(MethodView):
	"""
	角色用户列表
	"""

	@admin_required
	@demo.arguments(RoleUserQuery, location='query')
	@demo.response(200, UserRecord(many=True))
	def get(self, args):
		return RoleService().role_users(args)

	@admin_required
	@demo.arguments(RoleRemoveUser, location='query')
	@demo.response(200)
	def delete(self, args):
		"""
		从用户的角色列表中移除指定角色
		"""
		return RoleService().remove_role_from_user(args)


# 新增角色相关接口
@demo.route("/system/role/all")
class AllRoleController(MethodView):
	"""
	获取所有角色列表
	"""

	@admin_required
	@demo.response(200, RoleRecord(many=True))
	def get(self):
		return RoleService().get_all_roles()


@demo.route("/system/role/user")
class UserRoleController(MethodView):
	"""
	获取用户角色列表
	"""

	@admin_required
	@demo.arguments(UserRoleQuery, location='query')
	@demo.response(200, RoleRecord(many=True))
	def get(self, args):
		return RoleService().get_user_roles(args)


# 角色菜单权限管理
@demo.route("/system/role/menu")
class RoleMenuController(MethodView):
	"""
	角色菜单权限管理
	"""

	@admin_required
	@demo.arguments(RoleUserQuery, location='query')
	@demo.response(200)
	def get(self, args):
		"""获取角色菜单权限列表"""
		return RoleService().get_role_menus(args)

	@admin_required
	@demo.arguments(RoleMenuPermissionQuery)
	@demo.response(200)
	def post(self, args):
		"""设置角色菜单权限"""
		return RoleService().set_role_menu_permissions(args)


# 角色按钮权限管理
@demo.route("/system/role/button")
class RoleButtonController(MethodView):
	"""
	角色按钮权限管理
	"""

	@admin_required
	@demo.arguments(RoleUserQuery, location='query')
	@demo.response(200)
	def get(self, args):
		"""获取角色按钮权限列表"""
		return RoleService().get_role_buttons(args)

	@admin_required
	@demo.arguments(RoleButtonPermissionQuery)
	@demo.response(200)
	def post(self, args):
		"""设置角色按钮权限"""
		return RoleService().set_role_button_permissions(args)
