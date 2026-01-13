# coding: utf-8
"""
 * @Author：cyg
 * @Package：AuthButtonsService
 * @Project：Default (Template) Project
 * @name：AuthButtonsService
 * @Date：2025/9/19 15:55
 * @Filename：AuthButtonsService
"""
from flask import abort, session
from flask_babelplus import gettext

from demo import demo
from model.model import AuthButton, AuthMenu, AdminRoleRelation, RoleButtonRelation, SysConfig, db


class AuthButtonsService:
	def get_sys_role_id(self):
		"""
		获取系统管理员角色ID - 从system_config表中获取sys_role_id配置项的值
		:return: int 系统管理员角色ID，如果配置不存在则返回默认值1
		"""
		config = SysConfig.query.filter_by(name='sys_role_id').first()
		if config and config.value:
			# 去除前后空格并转换为字符串
			value_str = str(config.value).strip()
			if value_str:
				try:
					return int(value_str)
				except (ValueError, TypeError):
					# 如果配置值无法转换为整数，返回默认值1
					return 1
		# 如果配置不存在，返回默认值1
		return 1
	
	def get_button_list(self):
		"""
		获取按钮权限列表 - 根据用户角色权限获取按钮
		"""
		# 获取当前登录用户信息
		key = f'{demo.name}_user_info'
		admin_info = session.get(key)
		if not admin_info:
			abort(401, gettext('未登录或登录失效'))
		
		admin_id = admin_info['id']
		
		# 查询用户角色
		user_roles = AdminRoleRelation.query.filter_by(admin_id=admin_id).all()
		role_ids = [int(role.role) for role in user_roles if role.role is not None]
		
		# 获取系统管理员角色ID
		sys_role_id = self.get_sys_role_id()
		
		# 如果是系统管理员角色，返回所有按钮权限
		if sys_role_id in role_ids:
			auth_list = AuthButton.query.with_entities(AuthButton.button_name, AuthMenu.name) \
				.outerjoin(AuthMenu, AuthButton.menu_id == AuthMenu.id).all()
		else:
			# 根据角色权限查询按钮
			if not role_ids:
				return {}
			
			# 通过角色按钮关系表查询用户有权限的按钮ID
			button_ids = db.session.query(RoleButtonRelation.button_id).filter(
				RoleButtonRelation.role_id.in_(role_ids)
			).distinct().all()
			
			button_id_list = [button_id[0] for button_id in button_ids]
			
			if not button_id_list:
				return {}
			
			# 获取有权限的按钮
			auth_list = AuthButton.query.with_entities(AuthButton.button_name, AuthMenu.name) \
				.outerjoin(AuthMenu, AuthButton.menu_id == AuthMenu.id) \
				.filter(AuthButton.id.in_(button_id_list)).all()
		
		# 构建返回数据
		data = {}
		for item in auth_list:
			# menu_name 是菜单名称，button_name 是按钮名称
			menu_name = item[1]
			button_name = item[0]
			
			# 如果菜单名不存在或为空，跳过
			if not menu_name or not button_name:
				continue
			
			if menu_name not in data:
				data[menu_name] = []
			data[menu_name].append(button_name)
		
		return data

	def check_api_permission(self, admin_id, api_url, method):
		"""
		检查接口权限 - 根据用户ID、接口地址和请求方式判断是否有权限
		:param admin_id: 用户ID
		:param api_url: 接口地址
		:param method: 请求方式 (GET, POST, PUT, DELETE等)
		:return: bool 是否有权限
		"""
		# 查询用户角色
		user_roles = AdminRoleRelation.query.filter_by(admin_id=admin_id).all()
		role_ids = [int(role.role) for role in user_roles if role.role is not None]
		
		# 获取系统管理员角色ID
		sys_role_id = self.get_sys_role_id()
		
		# 如果是系统管理员角色，直接返回True
		if sys_role_id in role_ids:
			return True
		
		# 如果没有角色，返回False
		if not role_ids:
			return False
		
		# 通过角色按钮关系表查询用户有权限的按钮ID
		button_ids = db.session.query(RoleButtonRelation.button_id).filter(
			RoleButtonRelation.role_id.in_(role_ids)
		).distinct().all()
		
		button_id_list = [button_id[0] for button_id in button_ids]
		
		# 如果没有按钮权限，返回False
		if not button_id_list:
			return False
		
		# 查询是否有匹配的接口权限
		# 支持精确匹配和通配符匹配
		api_permission = AuthButton.query.filter(
			AuthButton.id.in_(button_id_list),
			AuthButton.api_url == api_url,
			AuthButton.method == method.upper()
		).first()
		
		# 如果找到精确匹配的权限，返回True
		if api_permission:
			return True
		
		# 如果没有精确匹配，尝试通配符匹配（支持*结尾的URL）
		wildcard_permissions = AuthButton.query.filter(
			AuthButton.id.in_(button_id_list),
			AuthButton.method == method.upper(),
			AuthButton.api_url.like('%*')
		).all()
		
		for permission in wildcard_permissions:
			# 移除末尾的*进行匹配
			pattern = permission.api_url.rstrip('*')
			if api_url.startswith(pattern):
				return True
		
		return False
