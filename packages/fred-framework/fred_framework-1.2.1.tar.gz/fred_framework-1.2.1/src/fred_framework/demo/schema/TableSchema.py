# coding: utf-8
from marshmallow import Schema, fields

"""
 * @Author：PyCharm - yougangchen
 * @Package：TableSchema
 * @Project：fred-frame
 * @name：TableSchema
 * @Date：2025/7/2 10:50 - 星期三
 * @Filename：TableSchema
 
"""


class FieldResponseSchema(Schema):
	"""
		 @desc:字段参数
	"""
	id = fields.Int()
	table_id = fields.Int(required=False)
	field_name = fields.Str(required=True, metadata={'description': '字段名'})
	field_type = fields.Int(required=True, metadata={'description': '字段类型'})
	field_desc = fields.Str(required=True, metadata={'description': '字段描述'})
	default = fields.Str(required=False, allow_none=True, metadata={'description': '默认值'})
	is_index = fields.Boolean()


class TableListResponse(Schema):
	"""
		 @desc:输出参数
	"""
	id = fields.Int()
	name = fields.Str(metadata={'description': '表名'})
	desc = fields.Str(metadata={'description': '描述'})
	deleted = fields.Int(metadata={'description': '删除状态'})
	created = fields.DateTime(format='%Y-%m-%d %H:%M:%S', metadata={'description': '创建时间'})
	modified = fields.DateTime(format='%Y-%m-%d %H:%M:%S', metadata={'description': '修改时间'})
	field = fields.List(fields.Nested(FieldResponseSchema, metadata={'description': '字段列表'}))


class TableListQuery(Schema):
	"""
		 @desc:查询参数 及验证
	"""
	name = fields.String(metadata={'description': '表名'})
	desc = fields.String(metadata={'description': '描述'})
	pageSize = fields.Int(load_default=10, metadata={'description': '每页数量'})
	pageNum = fields.Int(required=False, load_default=1, metadata={'description': '页码'})


class FieldSaveQuery(Schema):
	"""
		 @desc:查询参数 及验证
	"""
	id = fields.Int(load_default=0, allow_none=True)
	table_id = fields.Int(required=False, allow_none=True)
	field_name = fields.Str(required=True, metadata={'description': '字段名'})
	field_type = fields.Int(required=True, allow_none=False, metadata={'description': '字段类型'})
	field_desc = fields.Str(required=True, metadata={'description': '字段描述'})
	default = fields.Str(required=False, allow_none=True, metadata={'description': '默认值'})


class TableSaveQuery(Schema):
	"""
		 @desc:查询参数 及验证
	"""
	id = fields.Integer(load_default=0)
	name = fields.String(required=True)
	desc = fields.String(required=True)
	field = fields.List(fields.Nested(FieldSaveQuery), required=True)


class TableDelQuery(Schema):
	"""
		 @desc:查询参数 及验证
	"""
	id = fields.Integer(required=True)
	deleted = fields.Integer(required=True)


class FieldTypeListQuery(Schema):
	"""
		 @desc: 查询参数及验证
	"""
	field_type = fields.String(metadata={'description': '类型'})
	desc = fields.String(metadata={'description': '说明'})
	select_all = fields.Boolean(load_default=False, metadata={'description': '是否输出所有'})
	pageSize = fields.Int(load_default=10, metadata={'description': '每页数量'})
	pageNum = fields.Int(required=False, load_default=1, metadata={'description': '页码'})


class FieldTypeSaveQuery(Schema):
	"""
		 @desc: 新增/编辑参数及验证
	"""
	id = fields.Integer(load_default=0)
	field_type = fields.String(required=True, metadata={'description': '类型'})
	desc = fields.String(required=True, metadata={'description': '说明'})


class FieldTypeDelQuery(Schema):
	"""
		 @desc: 删除参数及验证
	"""
	id = fields.Integer(required=True)
	deleted = fields.Integer(required=True)


class FieldTypeResponse(Schema):
	"""
		 @desc: 输出参数
	"""
	id = fields.Int()
	field_type = fields.Str(metadata={'description': '类型'})
	desc = fields.Str(metadata={'description': '说明'})


class IndexSaveQuery(Schema):
	id = fields.Int(load_default=0)
	table_id = fields.Int(required=True)
	index_name = fields.Str(required=True)
	index_fields = fields.Str(required=True)  # 逗号分隔
	index_type = fields.Str(load_default='INDEX')


class IndexListQuery(Schema):
	table_id = fields.Int(required=True)


class IndexDelQuery(Schema):
	id = fields.Int(required=True)


class IndexListResponse(Schema):
	id = fields.Int()
	table_id = fields.Int()
	index_name = fields.Str()
	index_fields = fields.Str()
	is_unique = fields.Boolean()
	index_type = fields.Str()
	created = fields.DateTime()
	modified = fields.DateTime()


class TableDataQuery(Schema):
	"""
	 @desc:查询表数据参数
	"""
	table_id = fields.Int(required=True, metadata={'description': '表ID'})
	pageSize = fields.Int(load_default=10, metadata={'description': '每页数量'})
	pageNum = fields.Int(required=False, load_default=1, metadata={'description': '页码'})


