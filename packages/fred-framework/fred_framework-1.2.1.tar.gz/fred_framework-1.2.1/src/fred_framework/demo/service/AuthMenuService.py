import json
import time

from flask import abort, session
from flask_babelplus import gettext

from demo import demo
from model.model import AuthMenu, AdminRoleRelation, RoleMenuRelation, db, SysConfig


class AuthMenuService:
	
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
	
	def admin_menu(self):
		"""
		管理员菜单 - 根据用户角色权限获取菜单
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
		
		# 如果是系统管理员角色，返回所有菜单
		# 检查用户是否拥有系统管理员角色
		if role_ids and sys_role_id in role_ids:
			# 系统管理员返回所有未删除的菜单
			menu_items = AuthMenu.query.filter(AuthMenu.deleted == 0).order_by(AuthMenu.sort.asc()).all()
			return self.build_tree(menu_items)
		
		# 根据角色权限查询菜单
		if not role_ids:
			# 即使没有角色，也返回默认菜单（id为1）
			menu_items = AuthMenu.query.filter(
				AuthMenu.id == 1,
				AuthMenu.deleted == 0
			).order_by(AuthMenu.sort.asc()).all()
		else:
			# 通过角色菜单关系表查询用户有权限的菜单ID
			menu_ids = db.session.query(RoleMenuRelation.menu_id).filter(
				RoleMenuRelation.role_id.in_(role_ids)
			).distinct().all()
			
			menu_id_list = [menu_id[0] for menu_id in menu_ids]
			
			# 确保所有用户都有id为1的菜单权限
			if 1 not in menu_id_list:
				menu_id_list.append(1)
			
			# 获取有权限的菜单
			menu_items = AuthMenu.query.filter(
				AuthMenu.id.in_(menu_id_list),
				AuthMenu.deleted == 0
			).order_by(AuthMenu.sort.asc()).all()
		
		return self.build_tree(menu_items)
	
	def menu_list(self, args):
		page = args.get('pageNum', 1)
		per_page = args.get('pageSize', 10)
		title_kw = (args.get('title') or '').strip()
		deleted = args.get('deleted', 0)
		
		# 基础查询：一级菜单
		base_query = AuthMenu.query.filter(AuthMenu.parent_id == 0)
		# 删除状态过滤：默认仅未删除
		if deleted in (0, 1):
			base_query = base_query.filter(AuthMenu.deleted == deleted)
		
		# 如有标题关键字，需要查询匹配到的任意层级菜单，并回溯到其一级父菜单
		if title_kw:
			# 预取全部菜单（带删除状态约束）
			all_items_query = AuthMenu.query
			if deleted in (0, 1):
				all_items_query = all_items_query.filter(AuthMenu.deleted == deleted)
			all_items = all_items_query.order_by(AuthMenu.sort.asc()).all()
			
			# 找出名字或 meta.title 命中的所有菜单
			needle = title_kw.lower()
			matched_items = []
			for item in all_items:
				name_ok = (item.name or '').lower().find(needle) != -1
				meta_title = ''
				try:
					meta_title = (json.loads(item.meta).get('title') if item.meta else '') or ''
				except Exception:
					meta_title = ''
				meta_ok = meta_title.lower().find(needle) != -1
				if name_ok or meta_ok:
					matched_items.append(item)
			
			# 计算这些命中项对应的一级父菜单 id 集合
			root_ids = set()
			if matched_items:
				id_to_item = {it.id: it for it in all_items}
				for it in matched_items:
					cur = it
					while cur and cur.parent_id != 0:
						cur = id_to_item.get(cur.parent_id)
					if cur:
						root_ids.add(cur.id)
			
			# 若无匹配，直接返回空集，避免返回所有一级菜单
			if not root_ids:
				return {
					'records': [],
					'total': 0,
					'pageNum': page,
					'pageSize': per_page,
				}
			
			# 在基础查询上限定到这些根 id
			base_query = base_query.filter(AuthMenu.id.in_(list(root_ids)))
		
		# 分页取根节点
		menu_page = base_query.order_by(AuthMenu.deleted.asc(), AuthMenu.sort.asc()).paginate(page=page, per_page=per_page)
		
		# 构建整棵树，再用分页根节点挑选对应子树返回
		all_menu_items = AuthMenu.query.all()
		tree_structure = self.build_tree(all_menu_items)
		records = []
		for item in menu_page.items:
			for child in tree_structure:
				if child['id'] == item.id:
					records.append(child)
		return {
			'records': records,
			'total': menu_page.total,
			'pageNum': menu_page.page,
			'pageSize': menu_page.per_page,
		}
	
	def build_tree(self, menu_items, parent_id=0):
		tree = []
		for item in menu_items:
			if item.parent_id == parent_id:
				children = self.build_tree(menu_items, item.id)
				
				# 解析 meta 字段，确保有一个完整的 meta 对象
				try:
					meta = json.loads(item.meta) if item.meta else {}
				except json.JSONDecodeError:
					meta = {}
				
				# 确保 meta 对象有必需的字段，避免前端报错
				if not isinstance(meta, dict):
					meta = {}
				
				# 设置默认值，确保前端不会因为缺少字段而报错
				if 'isFull' not in meta:
					meta['isFull'] = False
				if 'isHide' not in meta:
					meta['isHide'] = False
				if 'isAffix' not in meta:
					meta['isAffix'] = False
				if 'isKeepAlive' not in meta:
					meta['isKeepAlive'] = True
				if 'isLink' not in meta:
					meta['isLink'] = ""
				if 'title' not in meta:
					meta['title'] = item.name or '未命名菜单'
				if 'icon' not in meta:
					meta['icon'] = 'el-icon-menu'
				
				# 构建返回的数据字典
				item_dict = {
					'id': item.id,
					'parent_id': item.parent_id,
					'path': item.path,
					'name': item.name,
					'component': item.component,
					'redirect': item.redirect,
					'meta': meta,
					'deleted': item.deleted,
					'sort': item.sort
				}
				
				if children:
					item_dict['children'] = children
				
				tree.append(item_dict)
		return tree
	
	def add_menu(self, data):
		# 如果 parent_id 未提供或为 None，则默认设置为 0（一级菜单）
		if 'parent_id' not in data or data['parent_id'] is None:
			data['parent_id'] = 0
		
		name = data['meta']['title']
		data['meta'] = json.dumps(data['meta'])
		data['name'] = name
		nowtime = int(time.time())
		data['created'] = nowtime
		data['modified'] = nowtime
		# 确保新增的菜单默认为启用状态
		data['deleted'] = 0
		menu = AuthMenu(**data)
		db.session.add(menu)
		db.session.commit()
		return menu.id
	
	def update_menu(self, data):
		menu_id = data.get("id", 0)
		menu = AuthMenu.query.get(menu_id)
		if not menu:
			abort(400, gettext('菜单不存在'))
		name = data['meta']['title']
		data['name'] = name
		data['meta'] = json.dumps(data['meta'])
		for k, v in data.items():
			setattr(menu, k, v)
		db.session.commit()
		return menu.id
	
	def delete_menu(self, args):
		id = args.get('id', 0)
		menu = AuthMenu.query.filter(AuthMenu.id == id).first()
		
		if not menu:
			abort(400, gettext('菜单不存在'))
		
		# 逻辑删除
		menu.deleted = 1
		menu.modified = int(time.time())
		db.session.commit()
		return True
	
	def restore_menu(self, args):
		id = args.get('id', 0)
		menu = AuthMenu.query.filter(AuthMenu.id == id).first()
		
		if not menu:
			abort(400, gettext('菜单不存在'))
		
		# 恢复菜单
		menu.deleted = 0
		menu.modified = int(time.time())
		db.session.commit()
		return True
