# python3.11
# -*- coding: utf-8 -*-
"""
 @author: Administrator
 @date: 2024/10/12 20:27
"""

from marshmallow import Schema, fields, validate, EXCLUDE


class SystemConfigListQuery(Schema):
	"""
	系统配置列表查询
	"""
	page = fields.Int(required=False, load_default=1, metadata={'description': '页码'})
	limit = fields.Int(load_default=10, metadata={'description': '每页数量'})
	name = fields.Str(metadata={'description': '配置项名称'})


class SystemConfigRecord(Schema):
	"""
	系统配置记录
	"""
	id = fields.Int(metadata={'description': '配置ID'})
	name = fields.Str(metadata={'description': '配置项'})
	value = fields.Str(metadata={'description': '配置值'})
	desc = fields.Str(metadata={'description': '配置说明'})


class SystemConfigListResponse(Schema):
	"""
	系统配置列表响应
	"""
	total = fields.Int(metadata={'description': '总数'})
	records = fields.List(fields.Nested(SystemConfigRecord), metadata={'description': '列表'})
	pageNum = fields.Int(metadata={'description': '页码'})
	pageSize = fields.Int(metadata={'description': '每页数量'})


class SystemConfigSaveQuery(Schema):
	"""
	新增系统配置
	"""
	id = fields.Int(required=False, load_default=0, metadata={'description': '配置ID，0表示新增'})
	name = fields.Str(required=True, validate=validate.Length(min=1), metadata={'description': '配置项'})
	value = fields.Str(required=True, metadata={'description': '配置值'})
	desc = fields.Str(load_default='', metadata={'description': '配置说明'})

	class Meta:
		unknown = EXCLUDE


class SystemConfigDeleteQuery(Schema):
	"""
	删除系统配置
	"""
	id = fields.List(fields.Int(), required=True, data_key="id[]", metadata={'description': '配置ID列表'})


class SystemLogQuery(Schema):
	"""
	系统日志查询参数
	"""
	pageNum = fields.Int(required=False, load_default=1, metadata={'description': '页码'})
	pageSize = fields.Int(required=False, load_default=10, metadata={'description': '每页数量'})
	username = fields.Str(required=False, allow_none=True, metadata={'description': '用户名'})
	api = fields.Str(required=False, allow_none=True, metadata={'description': 'API路径'})
	method = fields.Str(required=False, allow_none=True, metadata={'description': '请求方法'})
	code = fields.Int(required=False, allow_none=True, metadata={'description': '状态码'})
	start_date = fields.Str(required=False, allow_none=True, metadata={'description': '开始日期'})
	end_date = fields.Str(required=False, allow_none=True, metadata={'description': '结束日期'})


class SystemLogRecord(Schema):
	"""
	系统日志记录
	"""
	id = fields.Int(metadata={'description': '日志ID'})
	user_id = fields.Int(metadata={'description': '用户ID'})
	username = fields.Str(metadata={'description': '用户名'})
	api = fields.Str(metadata={'description': 'API路径'})
	method = fields.Str(metadata={'description': '请求方法'})
	code = fields.Int(metadata={'description': '状态码'})
	created = fields.DateTime(format='%Y-%m-%d %H:%M:%S', metadata={'description': '创建时间'})
	api_summary = fields.Str(metadata={'description': '接口说明'})


class SystemLogDetailRecord(Schema):
	"""
	系统日志详情
	"""
	id = fields.Int(metadata={'description': '日志ID'})
	user_id = fields.Int(metadata={'description': '用户ID'})
	username = fields.Str(metadata={'description': '用户名'})
	api = fields.Str(metadata={'description': 'API路径'})
	method = fields.Str(metadata={'description': '请求方法'})
	code = fields.Int(metadata={'description': '状态码'})
	created = fields.DateTime(format='%Y-%m-%d %H:%M:%S', metadata={'description': '创建时间'})
	request = fields.Str(allow_none=True, metadata={'description': '请求数据'})
	response = fields.Str(allow_none=True, metadata={'description': '响应数据'})


class SystemLogDeleteQuery(Schema):
	"""
	删除系统日志参数
	"""
	id = fields.List(fields.Int(), required=True, data_key="id[]", metadata={'description': '日志ID列表'})


class SystemLogDetailQuery(Schema):
	"""
	获取系统日志详情参数
	"""
	id = fields.Int(required=True, metadata={'description': '日志ID'})

