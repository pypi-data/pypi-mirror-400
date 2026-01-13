# coding: utf-8
from marshmallow import Schema, fields

"""
 * @Author：PyCharm - yougangchen
 * @Package：AuthMenuSechema
 * @Project：fred-frame
 * @name：AuthMenuSechema
 * @Date：2025/6/25 16:05 - 星期三
 * @Filename：AuthMenuSechema
 
"""

class MenuMetaSchema(Schema):
	"""菜单元信息"""
	title = fields.Str(metadata={'description': '菜单标题'})
	icon = fields.Str(metadata={'description': '菜单图标'})
	isFull = fields.Boolean(metadata={'description': '是否全屏'})
	isHide = fields.Boolean(metadata={'description': '是否隐藏'})
	isAffix = fields.Boolean(metadata={'description': '是否固定标签'})
	isKeepAlive = fields.Boolean(metadata={'description': '是否缓存'})
	isLink = fields.Str(metadata={'description': '是否外链'})


class MenuListResponseSchema(Schema):
	"""菜单列表响应"""
	id = fields.Int(metadata={'description': '菜单ID'})
	parent_id = fields.Int(metadata={'description': '父级菜单ID'})
	path = fields.Str(metadata={'description': '菜单路由路径'})
	name = fields.Str(metadata={'description': '菜单名称'})
	component = fields.Str(metadata={'description': '组件路径'})
	redirect = fields.Str(metadata={'description': '重定向地址'})
	meta = fields.Nested(MenuMetaSchema, metadata={'description': '菜单元信息'}, allow_none=True)
	deleted = fields.Int(metadata={'description': '删除状态：0未删除，1已删除'})
	sort = fields.Int(metadata={'description': '排序'})
	children = fields.List(fields.Nested('MenuListResponseSchema'), metadata={'description': '子菜单列表'}, allow_none=True)


class AuthMenuListSchema(Schema):
	"""
        @desc : AuthMenuListSchema
    """
	pageNum = fields.Int(required=False, load_default=1, metadata={'description': '页码'})
	pageSize = fields.Int(load_default=10, metadata={'description': '每页数量'})
	title = fields.Str(required=False, load_default=None, metadata={'description': '菜单标题，模糊查询'})
	deleted = fields.Int(required=False, load_default=0, metadata={'description': '删除状态：0未删除，1已删除'})


class AuthMenuMetaSchema(Schema):
	"""
	菜单更新参数
	"""
	icon = fields.Str(required=False, load_default="Menu", metadata={"description": "菜单图标"})
	isAffix = fields.Boolean(required=False, load_default=False, metadata={"description": "是否固定标签"})
	isFull = fields.Boolean(required=False, load_default=False, metadata={"description": "是否全屏"})
	isHide = fields.Boolean(required=False, load_default=False, metadata={"description": "是否隐藏"})
	isKeepAlive = fields.Boolean(required=False, load_default=True, metadata={"description": "是否缓存"})
	isLink = fields.Str(required=False, load_default="", metadata={"description": "是否外链"})
	title = fields.Str(required=True, metadata={"description": "菜单标题"})


class AuthMenuSaveSchema(Schema):
	"""
	菜单保存/编辑参数
	"""
	id = fields.Int(required=False, metadata={"description": "菜单ID，编辑时必传"})
	parent_id = fields.Int(required=False, metadata={"description": "父级菜单ID"})
	path = fields.Str(required=True, metadata={"description": "菜单路由路径"})
	component = fields.Str(required=False, metadata={"description": "组件路径"})
	redirect = fields.Str(required=False, metadata={"description": "重定向地址"})
	meta = fields.Nested(AuthMenuMetaSchema, required=False, metadata={"description": "菜单元信息"})
	sort = fields.Int(required=False, metadata={"description": "排序"})


class AuthMenuDeleteSchema(Schema):
	"""
	菜单删除参数
	"""
	id = fields.Int(required=True, metadata={"description": "要删除的菜单id"})
