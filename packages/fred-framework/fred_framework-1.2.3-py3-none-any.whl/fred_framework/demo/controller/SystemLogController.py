"""
 * @Author：Qoder
 * @Package：SystemLogController
 * @Project：admin
 * @name：SystemLogController
 * @Date：2025/12/1
 * @Filename：SystemLogController
"""
from flask.views import MethodView
from flask import abort
from flask_babelplus import gettext

from demo import demo
from demo.controller import admin_required
from demo.schema.SystemConfigSchema import SystemLogQuery, SystemLogRecord, SystemLogDetailRecord, SystemLogDeleteQuery, SystemLogDetailQuery
from demo.service.SystemLogService import SystemLogService
from fred_framework.common.PageSchema import PageSchemaFactory


@demo.route("/system/log")
class SystemLogController(MethodView):
	"""
	系统日志管理
	"""

	@admin_required
	@demo.arguments(SystemLogQuery, location='query')
	@demo.response(200, PageSchemaFactory(SystemLogRecord))
	def get(self, args):
		"""
		系统日志列表
		"""
		return SystemLogService().get_system_logs(args)

	@admin_required
	@demo.arguments(SystemLogDeleteQuery, location='query')
	@demo.response(200)
	def delete(self, args):
		"""
		删除系统日志
		"""
		ids = args.get('id', [])
		if not ids:
			abort(500, gettext("请选择要删除的日志"))

		return SystemLogService().delete_system_logs(ids)


@demo.route("/system/log/detail")
class SystemLogDetailController(MethodView):
	"""
	系统日志详情
	"""

	@admin_required
	@demo.arguments(SystemLogDetailQuery, location='query')
	@demo.response(200, SystemLogDetailRecord)
	def get(self, args):
		"""
		系统日志详情
		"""
		log_id = args.get('id')
		return SystemLogService().get_system_log_detail(log_id)
