# coding: utf-8
from marshmallow import Schema, fields, validate

"""
 * @Author：PyCharm - yougangchen
 * @Package：RoleSchem
 * @Project：fred-frame
 * @name：RoleSchem
 * @Date：2025/6/30 18:41 - 星期一
 * @Filename：RoleSchem
 
"""


class AdminRoleListQuery(Schema):
	"""
	角色列表查询
	"""
	page = fields.Int(required=False, load_default=1, metadata={'description': '页码'})
	limit = fields.Int(load_default=10, metadata={'description': '每页数量'})
	name = fields.Str(metadata={'description': '角色名称'})


class RoleRecord(Schema):
	id = fields.Int(metadata={'description': '角色id'})
	name = fields.Str(metadata={'description': '角色名称'})
	created = fields.DateTime(format='%Y-%m-%d %H:%M:%S', metadata={'description': '创建时间'})


class UserRecord(Schema):
	"""
	用户记录
	"""
	id = fields.Int(metadata={'description': '用户id'})
	username = fields.Str(metadata={'description': '用户名'})
	phone = fields.Str(metadata={'description': '手机号'})
	phone_prefix = fields.Int(metadata={'description': '手机号前缀'})
	phone_suffix = fields.Int(metadata={'description': '手机号后缀'})
	created = fields.DateTime(format='%Y-%m-%d %H:%M:%S', metadata={'description': '创建时间'})
	forbidden = fields.Int(metadata={'description': '禁用状态'})
	lastLogin = fields.DateTime(format='%Y-%m-%d %H:%M:%S', metadata={'description': '最后登录时间'})
	avatar = fields.Str(metadata={'description': '头像'})
	roleName = fields.Str(metadata={'description': '角色名称'})
	role_ids = fields.List(fields.Int(), load_default=[], metadata={'description': '角色ID列表'})


class AdminRoleSaveQuery(Schema):
	"""
	新增或修改角色
	"""
	id = fields.Int(required=False, load_default=0, metadata={'description': '角色id, 0表示新增'})
	name = fields.Str(required=True, validate=validate.Length(min=1), metadata={'description': '角色名称'})


class AdminRoleDeleteQuery(Schema):
	"""
	删除角色
	"""
	id = fields.List(fields.Int(), required=True, data_key="id[]", metadata={'description': '角色id列表'})


class RoleUserQuery(Schema):
	"""
	角色用户列表查询
	"""
	roleId = fields.Int(required=True, metadata={'description': '角色id'})


class RoleRemoveUser(Schema):
	roleId = fields.Int(required=True, metadata={'description': '角色id'})
	userIds = fields.List(fields.Int(), data_key="userIds[]", required=True, metadata={'description': '用户id列表'})


class UserRoleQuery(Schema):
	"""
	用户角色查询
	"""
	userId = fields.Int(required=True, metadata={'description': '用户id'})


class RoleMenuPermissionQuery(Schema):
	"""
	角色菜单权限设置
	"""
	roleId = fields.Int(required=True, metadata={'description': '角色id'})
	menuIds = fields.List(fields.Int(), required=True, metadata={'description': '菜单id列表'})


class RoleButtonPermissionQuery(Schema):
	"""
	角色按钮权限设置
	"""
	roleId = fields.Int(required=True, metadata={'description': '角色id'})
	buttonIds = fields.List(fields.Int(), required=True, metadata={'description': '按钮id列表'})
