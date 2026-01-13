# python3.11
# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime

from flask import abort
from flask_babelplus import gettext

from fred_framework.common.Utils import Utils
from model.model import AdminRoleRelation
from model.model import RoleButtonRelation, AuthButton
from model.model import RoleMenuRelation, AuthMenu
from model.model import db, AdminRole, Admin


class RoleService:

	def admin_roles(self, user_id=0):
		"""
		管理员 角色列表
		"""

		data = {}
		roles = AdminRole.query.with_entities(AdminRole.id, AdminRole.name.label('roleName')).all()
		data['allRolesList'] = Utils.query_to_dict_list(roles)
		if user_id == 0:
			return data

		# 使用 admin_role_relation 表查询用户已分配的角色
		roles = AdminRole.query \
			.join(AdminRoleRelation, AdminRole.id == AdminRoleRelation.role) \
			.with_entities(AdminRole.id, AdminRole.name.label('roleName')) \
			.filter(AdminRoleRelation.admin_id == user_id).all()
		data['assignRoles'] = Utils.query_to_dict_list(roles)
		return data

	def role_list(self, args):
		"""
		角色列表
		"""
		page = args.get('page', 1)
		per_page = args.get('limit', 10)
		query = AdminRole.query
		if args.get('name'):
			query = query.filter(AdminRole.name.like(f"%{args.get('name')}%"))

		data = query.paginate(page=page, per_page=per_page)
		records = Utils.query_to_dict_list(data.items)
		for item in records:
			item['created'] = Utils.timestamp_to_utc(item['created'])
		return {
			"total": data.total,
			"records": records,
			"pageNum": data.page,
			"pageSize": data.per_page
		}

	def role_save(self, args):
		"""
		新增/修改角色
		"""
		id = args.get('id', 0)
		if id == 0:
			# 新增
			role = AdminRole(name=args['name'], created=int(time.time()))
			db.session.add(role)
		else:
			# 修改
			role = AdminRole.query.filter_by(id=args['id']).first()
			if not role:
				abort(400, description=gettext("角色不存在"))
			role.name = args['name']

		db.session.commit()
		return None

	def role_delete(self, args):
		"""
		删除角色
		"""

		role_ids = args['id']

		# 检查是否包含超级管理员角色（ID为1），禁止删除
		if 1 in role_ids:
			abort(400, description=gettext("超级管理员角色不能删除"))

		# 检查是否有用户使用这些角色
		relation_count = AdminRoleRelation.query.filter(AdminRoleRelation.role.in_(role_ids)).count()
		if relation_count > 0:
			abort(400, description=gettext("所选角色中有正在被使用的角色，无法删除"))

		AdminRole.query.filter(AdminRole.id.in_(role_ids)).delete(synchronize_session=False)
		db.session.commit()
		return ""

	def get_all_roles(self):
		"""
		获取所有角色列表（用于下拉选择）
		"""
		roles = AdminRole.query.with_entities(
			AdminRole.id,
			AdminRole.name,
			AdminRole.created
		).all()
		records = Utils.query_to_dict_list(roles)
		for item in records:
			item['created'] = Utils.timestamp_to_utc(item['created'])
		return records

	def get_user_roles(self, args):
		"""
		获取用户角色列表
		"""

		roles = AdminRole.query \
			.join(AdminRoleRelation, AdminRole.id == AdminRoleRelation.role) \
			.with_entities(AdminRole.id, AdminRole.name) \
			.filter(AdminRoleRelation.admin_id == args['userId']).all()
		return Utils.query_to_dict_list(roles)

	def get_role_menus(self, args):
		"""
		获取角色菜单权限列表
		"""

		role_id = args.get('roleId', 0)
		menus = AuthMenu.query \
			.join(RoleMenuRelation, AuthMenu.id == RoleMenuRelation.menu_id) \
			.with_entities(AuthMenu.id, AuthMenu.name, AuthMenu.path) \
			.filter(RoleMenuRelation.role_id == role_id, AuthMenu.deleted == 0).all()
		return Utils.query_to_dict_list(menus)

	def set_role_menu_permissions(self, args):
		"""
		设置角色菜单权限
		"""

		role_id = args['roleId']
		menu_ids = args['menuIds']

		# 删除该角色的所有菜单权限
		RoleMenuRelation.query.filter_by(role_id=role_id).delete()

		# 添加新的菜单权限
		for menu_id in menu_ids:
			menu_relation = RoleMenuRelation(
				role_id=role_id,
				menu_id=menu_id,
				created=datetime.now()
			)
			db.session.add(menu_relation)

		db.session.commit()
		return ""

	def role_users(self, args):
		"""
		角色用户列表
		"""

		role_id = args.get('roleId', 0)

		# 使用 with_entities 明确指定返回的字段
		with_entities = (
			Admin.id,
			Admin.username,
			Admin.phone_prefix,
			Admin.phone_suffix,
			Admin.created,
			Admin.forbidden,
			Admin.last_login.label('lastLogin'),
			Admin.avatar
		)

		user_list = Admin.query \
			.join(AdminRoleRelation, Admin.id == AdminRoleRelation.admin_id) \
			.filter(
			AdminRoleRelation.role == role_id,
			Admin.deleted == 0
		).with_entities(*with_entities).all()

		if not user_list:
			return []

		# 获取所有用户的角色ID列表
		user_ids = [user.id for user in user_list]
		user_role_ids_map = {}
		if user_ids:
			role_relations = AdminRoleRelation.query \
				.filter(AdminRoleRelation.admin_id.in_(user_ids)) \
				.with_entities(AdminRoleRelation.admin_id, AdminRoleRelation.role) \
				.all()

			for admin_id, role_id_val in role_relations:
				if admin_id not in user_role_ids_map:
					user_role_ids_map[admin_id] = []
				user_role_ids_map[admin_id].append(role_id_val)

		# 手动构建返回数据，确保所有字段都返回
		return_data = []
		for user in user_list:
			# 安全处理可能为 None 的字段
			last_login = user.lastLogin if user.lastLogin else 0
			phone_prefix = user.phone_prefix if user.phone_prefix else 0
			phone_suffix = user.phone_suffix if user.phone_suffix else 0

			user_dict = {
				'id': user.id,
				'username': user.username if user.username else '',
				'phone_prefix': phone_prefix,
				'phone_suffix': phone_suffix,
				'created': user.created,
				'forbidden': user.forbidden,
				'lastLogin': last_login,
				'avatar': user.avatar if user.avatar else '',
				'phone': f"{str(phone_prefix)}****{str(phone_suffix)}",
				'roleName': '',
				'role_ids': user_role_ids_map.get(user.id, [])
			}
			# 格式化时间
			user_dict['created'] = Utils.timestamp_to_utc(user_dict['created'])
			user_dict['lastLogin'] = Utils.timestamp_to_utc(user_dict['lastLogin'])
			return_data.append(user_dict)

		return return_data

	def remove_role_from_user(self, args):
		"""
		从用户的角色列表中移除指定角色（支持批量）
		"""

		user_ids = args.get('userIds', [])
		role_id = args.get('roleId', 0)
		if not user_ids:
			abort(400, description=gettext("请选择要移除的用户"))

		# 从 admin_role_relation 表中删除指定的角色关系
		AdminRoleRelation.query.filter(
			AdminRoleRelation.admin_id.in_(user_ids),
			AdminRoleRelation.role == role_id
		).delete(synchronize_session=False)

		db.session.commit()
		return True

	def get_role_menus(self, args):
		"""
		获取角色菜单权限列表
		"""

		role_id = args.get('roleId', 0)
		if role_id == 0:
			return []

		# 获取所有菜单
		all_menus = AuthMenu.query.filter(AuthMenu.deleted == 0).all()

		# 角色ID为1时，表示拥有所有菜单权限
		if role_id == 1:
			assigned_menu_ids = [menu.id for menu in all_menus]
		else:
			# 获取角色已分配的菜单
			assigned_menus = RoleMenuRelation.query.filter_by(role_id=role_id).all()
			assigned_menu_ids = [relation.menu_id for relation in assigned_menus]
			# 确保所有角色都默认包含ID为1的菜单
			if 1 not in assigned_menu_ids:
				assigned_menu_ids.append(1)

		# 构建菜单树结构
		def build_menu_tree(menus, parent_id=0):
			tree = []
			for menu in menus:
				if menu.parent_id == parent_id:
					menu_dict = Utils.query_to_dict(menu)
					# 确保ID是字符串类型
					menu_dict['id'] = str(menu.id)

					# 处理meta字段
					if menu.meta:
						try:
							menu_dict['meta'] = json.loads(menu.meta) if isinstance(menu.meta, str) else menu.meta
						except:
							menu_dict['meta'] = {'title': menu.name, 'icon': ''}
					else:
						menu_dict['meta'] = {'title': menu.name, 'icon': ''}

					# 递归构建子菜单
					children = build_menu_tree(menus, menu.id)
					if children:
						menu_dict['children'] = children

					# 设置assigned状态：只有当菜单本身被分配且所有子菜单都被分配时，父菜单才显示为assigned=true
					menu_dict['assigned'] = menu.id in assigned_menu_ids

					# 如果有子菜单，需要检查子菜单的分配状态
					if children:
						# 检查是否所有子菜单都被分配
						all_children_assigned = all(child['assigned'] for child in children)
						# 只有当父菜单被分配且所有子菜单都被分配时，父菜单才显示为assigned=true
						menu_dict['assigned'] = menu.id in assigned_menu_ids and all_children_assigned

					tree.append(menu_dict)
			return tree

		return build_menu_tree(all_menus)

	def set_role_menu_permissions(self, args):
		"""
		设置角色菜单权限
		"""

		role_id = args.get('roleId', 0)
		menu_ids = args.get('menuIds', [])

		if role_id == 0:
			abort(400, description=gettext("角色ID不能为空"))

		# 角色ID为1时，不保存权限（超级管理员拥有所有权限）
		if role_id == 1:
			return True

		# 确保所有角色都包含ID为1的菜单
		if 1 not in menu_ids:
			menu_ids.append(1)

		# 删除现有权限
		RoleMenuRelation.query.filter_by(role_id=role_id).delete()

		# 添加新权限
		created = Utils.timestamp_format(0)
		for menu_id in menu_ids:
			relation = RoleMenuRelation(role_id=role_id, menu_id=menu_id, created=created)
			db.session.add(relation)

		db.session.commit()
		return True

	def get_role_buttons(self, args):
		"""
		获取角色按钮权限列表 - 按菜单分组的树形结构
		"""

		role_id = args.get('roleId', 0)
		if role_id == 0:
			return []

		# 获取所有菜单
		all_menus = AuthMenu.query.filter(AuthMenu.deleted == 0).order_by(AuthMenu.sort).all()

		# 获取所有按钮
		all_buttons = AuthButton.query.all()

		# 角色ID为1时，表示拥有所有按钮权限
		if role_id == 1:
			assigned_button_ids = [button.id for button in all_buttons]
		else:
			# 获取角色已分配的按钮
			assigned_buttons = RoleButtonRelation.query.filter_by(role_id=role_id).all()
			assigned_button_ids = [relation.button_id for relation in assigned_buttons]

		# 构建菜单树结构
		def build_menu_tree(menus, parent_id=0):
			tree = []
			for menu in menus:
				if menu.parent_id == parent_id:
					menu_dict = Utils.query_to_dict(menu)
					# 确保ID是字符串类型
					menu_dict['id'] = str(menu.id)

					# 处理meta字段
					if menu.meta:
						try:
							menu_dict['meta'] = json.loads(menu.meta) if isinstance(menu.meta, str) else menu.meta
						except:
							menu_dict['meta'] = {'title': menu.name, 'icon': ''}
					else:
						menu_dict['meta'] = {'title': menu.name, 'icon': ''}

					# 获取该菜单下的按钮，作为子节点
					menu_buttons = [btn for btn in all_buttons if btn.menu_id == menu.id]
					button_children = []
					for button in menu_buttons:
						button_dict = Utils.query_to_dict(button)
						button_dict['id'] = f"button_{button.id}"  # 使用button_前缀区分按钮ID
						button_dict['assigned'] = button.id in assigned_button_ids
						button_dict['isButton'] = True  # 标记这是按钮节点
						button_dict['buttonId'] = button.id  # 保存原始按钮ID
						button_dict['name'] = button.button_name
						button_dict['meta'] = {
							'title': button.button_name,
							'icon': 'Operation'
						}
						button_children.append(button_dict)

					# 递归构建子菜单
					children = build_menu_tree(menus, menu.id)

					# 合并按钮和子菜单
					all_children = []
					if button_children:
						all_children.extend(button_children)
					if children:
						all_children.extend(children)

					if all_children:
						menu_dict['children'] = all_children

					# 设置菜单的按钮权限状态
					menu_dict['hasButtons'] = len(button_children) > 0
					menu_dict['assignedButtons'] = len([btn for btn in button_children if btn['assigned']])
					menu_dict['totalButtons'] = len(button_children)

					tree.append(menu_dict)
			return tree

		return build_menu_tree(all_menus)

	def set_role_button_permissions(self, args):
		"""
		设置角色按钮权限
		"""

		role_id = args.get('roleId', 0)
		button_ids = args.get('buttonIds', [])

		if role_id == 0:
			abort(400, description=gettext("角色ID不能为空"))

		# 角色ID为1时，不保存权限（超级管理员拥有所有权限）
		if role_id == 1:
			return True

		# 删除现有权限
		RoleButtonRelation.query.filter_by(role_id=role_id).delete()

		# 添加新权限
		created = Utils.timestamp_format(0)
		for button_id in button_ids:
			relation = RoleButtonRelation(role_id=role_id, button_id=button_id, created=created)
			db.session.add(relation)

		db.session.commit()
		return True
