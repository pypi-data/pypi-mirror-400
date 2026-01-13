# python3.11
# -*- coding: utf-8 -*-
"""
 @author: Administrator
 @date: 2024/10/12 20:27
"""

from marshmallow import Schema, fields, validate, EXCLUDE

from fred_framework.common.Utils import Utils


class AdminLoginQuery(Schema):
	"""
		 @desc:查询参数 及验证
		 test user:
		 username: cyg
		 password: e10adc3949ba59abbe56e057f20f883e
	"""
	username = fields.Str(required=True, metadata={
		'example': 'admin',
		'description': '用户名'
	})
	password = fields.Str(required=True, validate=validate.Length(equal=32), metadata={
		'example': 'e10adc3949ba59abbe56e057f20f883e',
		'description': '密码'
	})
	captcha = fields.Str(required=True, validate=validate.Length(equal=4))


class AdminLoginResponse(Schema):
	"""
		 @desc:输出参数
	"""
	id = fields.Int()
	username = fields.Str()
	access_token = fields.Str()
	refresh_token = fields.Str()


class PhoneLoginQuery(Schema):
	phone = fields.Str(required=True, validate=Utils.validate_phone)
	sms_code = fields.Str(required=True, validate=validate.Length(min=4))


class SendCaptchaQuery(Schema):
	"""
	通过邮件或者短信 发送验证码
	"""
	acceptor = fields.Str(required=True)


# captcha_code = fields.Str(required=True)

class AdminInfoResponse(Schema):
	"""
	管理员信息
	"""
	id = fields.Int(metadata={'description': '用户id'})
	username = fields.Str(metadata={'description': '用户名/手机号'})
	avatar = fields.Str(load_default='', metadata={'description': '头像'})
	roles = fields.List(fields.Str(), load_default=[])
	buttons = fields.List(fields.Str(), load_default=[])
	routes = fields.List(fields.Str(), load_default=[])


class AdminListQuery(Schema):
	"""
	管理员列表
	"""
	page = fields.Int(required=False, load_default=1, metadata={'description': '页码'})
	limit = fields.Int(load_default=10, metadata={'description': '每页数量'})
	username = fields.Str(metadata={'description': '用户名'})
	phone = fields.Int(metadata={'description': '手机号'})
	lastLogin = fields.List(fields.DateTime(format='%Y-%m-%d %H:%M:%S'), metadata={'description': '最后登录时间'}, data_key='lastLogin[]')
	forbidden = fields.Boolean(load_default=False, metadata={'description': '是否禁用'})


class Records(Schema):
	id = fields.Int(metadata={'description': '用户id'})
	username = fields.Str(metadata={'description': '用户名'})
	avatar = fields.Str(load_default='', metadata={'description': '头像'})
	phone = fields.Str(metadata={'description': '手机号'})
	created = fields.DateTime(format='%Y-%m-%d %H:%M:%S', metadata={'description': '创建时间'})
	lastLogin = fields.DateTime(format='%Y-%m-%d %H:%M:%S', metadata={'description': '最后登录时间'})
	roleName = fields.Str(metadata={'description': '角色名称'})
	role_ids = fields.List(fields.Int(), load_default=[], metadata={'description': '角色ID列表'})
	forbidden = fields.Boolean(load_default=False, metadata={'description': '是否禁用'})


class AdminListResponse(Schema):
	"""
	管理员列表
	"""
	total = fields.Int(metadata={'description': '总数'})
	records = fields.List(fields.Nested(Records), metadata={'description': '列表'})
	pageNum = fields.Int(metadata={'description': '页码'})
	pageSize = fields.Int(metadata={'description': '每页数量'})



class RoleListResponse(Schema):
	"""
	角色列表
	"""
	id = fields.Int()
	name = fields.Str()


class RoleListQuery(Schema):
	"""
	用户id
	"""
	userId = fields.Int()


class AdminSaveQuery(Schema):
	"""
	新增用户
	"""
	id = fields.Int(required=False, load_default=0, metadata={'description': '用户id'})
	username = fields.Str(required=True, validate=validate.Length(min=1))
	avatar = fields.Str(load_default='', metadata={'description': '头像'})
	phone = fields.Str(required=False, validate=Utils.validate_phone)
	password = fields.Str(required=False, validate=validate.Length(min=6, max=20))
	role_ids = fields.List(fields.Int(), load_default=[], metadata={'description': '角色ID列表'})


class AdminSavePut(Schema):
	"""
	编辑用户
	"""
	id = fields.Int(required=False, load_default=0, metadata={'description': '用户id'})
	username = fields.Str(required=True, validate=validate.Length(min=1))
	avatar = fields.Str(load_default='', metadata={'description': '头像'})
	role_ids = fields.List(fields.Int(), load_default=[], metadata={'description': '角色ID列表'})

	class Meta:
		unknown = EXCLUDE


class AdminSetRoleQuery(Schema):
	user_id = fields.Int()
	role_id_list = fields.List(fields.Int())


class AdminForbiddenQuery(Schema):
	id = fields.Int()


class AdminForbiddenResponse(Schema):
	forbidden = fields.Boolean()


class AdminDelQuery(Schema):
	id = fields.List(fields.Int(), required=True, data_key="id[]")


class UpdatePassword(Schema):
	oldPassword = fields.Str(required=True, validate=validate.Length(equal=32))
	newPassword = fields.Str(required=True, validate=validate.Length(equal=32))
	repPassword = fields.Str(required=True, validate=validate.Length(equal=32))


class RestPassword(Schema):
	id = fields.Int(metadata={'description': '用户id'})


class SceneDataSchema(Schema):
	"""
	场景数据Schema
	"""
	scene_name = fields.Str(metadata={'description': '场景名称'})
	detection_count = fields.Int(metadata={'description': '检测数量'})
	scene_labels = fields.List(fields.Str(), metadata={'description': '场景标签列表'})


class StatisticsSceneResponse(Schema):
	"""
	场景统计响应Schema
	"""
	scenes = fields.List(fields.Nested(SceneDataSchema), metadata={'description': '场景列表'})
	total_detections = fields.Int(metadata={'description': '总检测数量'})
	scene_count = fields.Int(metadata={'description': '场景数量'})
	label_type_count = fields.Int(metadata={'description': '标签类型数量'})
	today_dish_count = fields.Int(metadata={'description': '当日传菜次数'})
	today_timeout_count = fields.Int(metadata={'description': '当日清理超时次数'})


class StatisticsSceneImagesResponse(Schema):
	"""
	场景图片响应Schema
	"""
	image_path = fields.Str(metadata={'description': '图片路径'})
	image_name = fields.Str(metadata={'description': '图片名称'})
	detections = fields.List(fields.Dict(), metadata={'description': '检测结果'})
	scene_name = fields.Str(metadata={'description': '场景名称'})


class ConversationStatisticsCardSchema(Schema):
	"""
	对话统计卡片Schema
	"""
	label = fields.Str(metadata={'description': '卡片标签'})
	value = fields.Raw(metadata={'description': '卡片值（可以是数字或字符串）'})


class ConversationStatisticsChartSchema(Schema):
	"""
	对话统计图表Schema
	"""
	title = fields.Str(metadata={'description': '图表标题'})
	type = fields.Str(allow_none=True, metadata={'description': '图表类型（可选，可以是任意字符串，前端不限制）'})
	option = fields.Dict(metadata={'description': 'ECharts配置选项（可以是任意ECharts配置）'})
	code = fields.Str(allow_none=True, metadata={'description': '图表配置源代码（可选）'})


class ConversationStatisticsTableColumnSchema(Schema):
	"""
	对话统计表格列Schema
	"""
	prop = fields.Str(metadata={'description': '列属性名'})
	label = fields.Str(metadata={'description': '列标签'})
	width = fields.Int(allow_none=True, metadata={'description': '列宽度'})
	sortable = fields.Bool(load_default=False, metadata={'description': '是否可排序'})


class ConversationStatisticsDataSchema(Schema):
	"""
	对话统计数据Schema
	"""
	cards = fields.List(fields.Nested(ConversationStatisticsCardSchema), allow_none=True, metadata={'description': '统计卡片列表'})
	chart = fields.Nested(ConversationStatisticsChartSchema, allow_none=True, metadata={'description': '图表配置'})
	table = fields.List(fields.Dict(), allow_none=True, metadata={'description': '表格数据'})
	table_columns = fields.List(fields.Nested(ConversationStatisticsTableColumnSchema), allow_none=True, metadata={'description': '表格列配置'})


class ConversationStatisticsResponse(Schema):
	"""
	对话统计响应Schema
	"""
	text = fields.Str(metadata={'description': '回复文本'})
	data = fields.Nested(ConversationStatisticsDataSchema, allow_none=True, metadata={'description': '统计数据'})


class ConversationStatisticsQuery(Schema):
	"""
	对话统计查询参数Schema
	"""
	query = fields.Str(required=True, metadata={'description': '用户查询内容'})
	store_id = fields.Int(allow_none=True, metadata={'description': '门店ID'})


class StatisticsSceneQuery(Schema):
	"""
	场景统计查询参数Schema
	"""
	store_id = fields.Int(allow_none=True, metadata={'description': '门店ID'})


class StatisticsSceneImagesQuery(Schema):
	"""
	场景图片查询参数Schema
	"""
	scene_name = fields.Str(required=True, metadata={'description': '场景名称'})


class StatisticsSceneDailyQuery(Schema):
	"""
	场景每日统计查询参数Schema
	"""
	store_id = fields.Int(allow_none=True, metadata={'description': '门店ID'})
	days = fields.Int(load_default=30, validate=validate.Range(min=1, max=365), metadata={'description': '查询天数，默认30天'})


class StatisticsSceneStatusQuery(Schema):
	"""
	场景状态统计查询参数Schema
	"""
	store_id = fields.Int(allow_none=True, metadata={'description': '门店ID'})
	scene_id = fields.Int(load_default=2, metadata={'description': '场景ID，默认2'})
	days = fields.Int(load_default=30, validate=validate.Range(min=1, max=365), metadata={'description': '查询天数，默认30天'})


class StatisticsSceneStoreDailyQuery(Schema):
	"""
	场景门店每日统计查询参数Schema
	"""
	store_id = fields.Int(allow_none=True, metadata={'description': '门店ID'})
	days = fields.Int(load_default=30, validate=validate.Range(min=1, max=30), metadata={'description': '查询天数，默认30天，最多30天'})


class StatisticsEmployeeDishTodayQuery(Schema):
	"""
	员工当日传菜统计查询参数Schema
	"""
	store_id = fields.Int(allow_none=True, metadata={'description': '门店ID'})


class StatisticsEmployeeDishTrendQuery(Schema):
	"""
	员工传菜趋势统计查询参数Schema
	"""
	store_id = fields.Int(allow_none=True, metadata={'description': '门店ID'})
	days = fields.Int(load_default=30, validate=validate.Range(min=1, max=365), metadata={'description': '查询天数，默认30天'})


class StatisticsEmployeeDishFirstRecordQuery(Schema):
	"""
	员工传菜第一条记录查询参数Schema
	"""
	store_id = fields.Int(required=True, metadata={'description': '门店ID'})
	job_number = fields.Str(required=True, metadata={'description': '员工工号，如果是"-1"表示未知员工'})
	date = fields.Str(required=True, validate=validate.Length(equal=10), metadata={'description': '日期，格式为YYYY-MM-DD'})


class AuthMenuMetaSchema(Schema):
	"""
	菜单Meta信息Schema
	"""
	title = fields.Str(metadata={'description': '菜单标题'})
	icon = fields.Str(metadata={'description': '菜单图标'})
	isLink = fields.Str(metadata={'description': '是否外部链接'})
	isHide = fields.Boolean(metadata={'description': '是否隐藏'})
	isFull = fields.Boolean(metadata={'description': '是否全屏'})
	isAffix = fields.Boolean(metadata={'description': '是否固定在标签'})
	isKeepAlive = fields.Boolean(metadata={'description': '是否缓存'})


class AuthMenuResponseSchema(Schema):
	"""
	权限菜单响应Schema
	"""
	id = fields.Int(metadata={'description': '菜单ID'})
	parent_id = fields.Int(metadata={'description': '父菜单ID'})
	name = fields.Str(metadata={'description': '菜单名称'})
	path = fields.Str(metadata={'description': '菜单路径'})
	component = fields.Str(metadata={'description': '组件路径'})
	redirect = fields.Str(metadata={'description': '重定向地址'})
	meta = fields.Nested(AuthMenuMetaSchema, metadata={'description': '菜单Meta信息'})
	children = fields.List(fields.Nested(lambda: AuthMenuResponseSchema()), metadata={'description': '子菜单'})


class SuccessResponseSchema(Schema):
	"""
	成功响应Schema
	"""
	message = fields.Str(metadata={'description': '响应消息'})


class AdminStatusResponseSchema(Schema):
	"""
	管理员状态响应Schema
	"""
	status = fields.Str(metadata={'description': '状态'})
	online = fields.Boolean(metadata={'description': '是否在线'})
