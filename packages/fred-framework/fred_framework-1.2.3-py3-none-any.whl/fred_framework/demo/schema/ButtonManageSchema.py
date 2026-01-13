"""
 * @Author：cyg
 * @Package：ButtonManageSchema
 * @Project：Default (Template) Project
 * @name：ButtonManageSchema
 * @Date：2025/1/20 10:00
 * @Filename：ButtonManageSchema
"""
from marshmallow import Schema, fields, validate


class ButtonListSchema(Schema):
    """
    按钮列表查询参数
    """
    pageNum = fields.Int(required=False, load_default=1, metadata={'description': '页码'})
    pageSize = fields.Int(required=False, load_default=10, metadata={'description': '每页数量'})
    menu_id = fields.Int(required=False, metadata={'description': '菜单ID'})
    button_name = fields.Str(required=False, metadata={'description': '按钮名称'})


class ApiInfoSchema(Schema):
    """
    API信息
    """
    api_url = fields.Str(required=True, metadata={'description': '接口地址'})
    method = fields.Str(required=True, validate=validate.OneOf(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']), metadata={'description': '请求方式'})


class ButtonAddSchema(Schema):
    """
    按钮新增参数
    """
    button_name = fields.Str(required=True, metadata={'description': '按钮名称'})
    menu_id = fields.Int(required=True, metadata={'description': '所属菜单ID'})
    explain = fields.Str(required=False, load_default='', metadata={'description': '按钮说明'})
    api_list = fields.List(fields.Nested(ApiInfoSchema), required=False, load_default=[], metadata={'description': 'API列表'})
    # 保持向后兼容
    api_url = fields.Str(required=False, load_default='', metadata={'description': '接口地址（已废弃，请使用api_list）'})
    method = fields.Str(required=False, load_default='GET', metadata={'description': '请求方式（已废弃，请使用api_list）'})


class ButtonUpdateSchema(Schema):
    """
    按钮更新参数
    """
    id = fields.Int(required=True, metadata={'description': '按钮ID'})
    button_name = fields.Str(required=True, metadata={'description': '按钮名称'})
    menu_id = fields.Int(required=True, metadata={'description': '所属菜单ID'})
    explain = fields.Str(required=False, load_default='', metadata={'description': '按钮说明'})
    api_list = fields.List(fields.Nested(ApiInfoSchema), required=False, load_default=[], metadata={'description': 'API列表'})
    # 保持向后兼容
    api_url = fields.Str(required=False, load_default='', metadata={'description': '接口地址（已废弃，请使用api_list）'})
    method = fields.Str(required=False, load_default='GET', metadata={'description': '请求方式（已废弃，请使用api_list）'})


class ButtonDeleteSchema(Schema):
    """
    按钮删除参数
    """
    id = fields.Int(required=True, metadata={'description': '按钮ID'})


class ButtonListResponseSchema(Schema):
    """
    按钮列表响应Schema
    """
    id = fields.Int(metadata={'description': '按钮ID'})
    button_name = fields.Str(metadata={'description': '按钮名称'})
    menu_id = fields.Int(metadata={'description': '所属菜单ID'})
    menu_name = fields.Str(metadata={'description': '所属菜单名称'})
    explain = fields.Str(metadata={'description': '按钮说明'})
    api_list = fields.List(fields.Nested(ApiInfoSchema), metadata={'description': 'API列表'})
    created = fields.DateTime(metadata={'description': '创建时间'})
    modified = fields.DateTime(metadata={'description': '修改时间'})
    api_url = fields.Str(metadata={'description': 'API地址（向后兼容）'})


class MenuOptionResponseSchema(Schema):
    """
    菜单选项响应Schema
    """
    id = fields.Int(metadata={'description': '菜单ID'})
    name = fields.Str(metadata={'description': '菜单名称'})
    children = fields.List(fields.Nested('MenuOptionResponseSchema'), metadata={'description': '子菜单列表'}, allow_none=True)


class ApiUrlResponseSchema(Schema):
    """
    API URL响应Schema
    """
    url = fields.Str(metadata={'description': '接口URL'})
    method = fields.Str(metadata={'description': '请求方法'})
    summary = fields.Str(metadata={'description': '接口摘要'})
    description = fields.Str(metadata={'description': '接口描述'})
    operation_id = fields.Str(metadata={'description': '操作ID'})
    tags = fields.List(fields.Str(), metadata={'description': '标签'})
    label = fields.Str(metadata={'description': '标签文本'})
