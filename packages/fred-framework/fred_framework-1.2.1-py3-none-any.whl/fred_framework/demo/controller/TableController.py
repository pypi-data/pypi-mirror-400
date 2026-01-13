# python3.11
# -*- coding: utf-8 -*-
"""
 @author: cyg
 @date: 2024/7/31 下午8:02
 @desc:
"""
from flask.views import MethodView
from flask_babelplus import gettext

from demo import demo
from demo.controller import admin_required
from demo.schema.TableSchema import TableListResponse, TableListQuery, TableSaveQuery, TableDelQuery, FieldSaveQuery, FieldTypeListQuery, FieldTypeSaveQuery, FieldTypeDelQuery, FieldTypeResponse, IndexSaveQuery, IndexListQuery, IndexDelQuery, IndexListResponse, TableDataQuery
from demo.service.TableService import TableService
from fred_framework.common.PageSchema import PageSchemaFactory

# 新增恢复表格的Schema导入
from demo.schema.TableSchema import TableDelQuery as RestoreTableQuery


@demo.route("/database/table")
class TableController(MethodView):
	@admin_required
	@demo.arguments(TableListQuery, location='query')
	@demo.response(200, PageSchemaFactory(TableListResponse))
	def get(self, args):
		"""
			查看mysql所有表
		"""
		table = TableService().table_list(args)
		return table

	@admin_required
	@demo.arguments(TableSaveQuery)
	@demo.response(200)
	def post(self, args):
		"""
			新增mysql表信息
		"""
		TableService.save_table(args)
		return gettext("保存成功")

	@admin_required
	@demo.arguments(TableSaveQuery)
	@demo.response(200)
	def put(self, args):
		"""
			保存表信息
		"""
		TableService.save_table(args)
		return gettext("保存成功")

	@admin_required
	@demo.arguments(TableDelQuery, location='query')
	@demo.response(200)
	def delete(self, args):
		"""
			删除mysql表信息
		"""
		TableService.delete_table(args)

		return gettext("删除成功")

	@admin_required
	@demo.arguments(RestoreTableQuery)
	@demo.response(200)
	def patch(self, args):
		"""
			恢复mysql表信息
		"""
		TableService.restore_table(args)

		return gettext("恢复成功")


@demo.route("/database/field_type")
class FieldTypeController(MethodView):
	@admin_required
	@demo.arguments(FieldTypeListQuery, location='query')
	@demo.response(200)
	def get(self, args):
		"""
		获取mysql字段类型列表
		"""
		return TableService.field_type_list(args)

	@admin_required
	@demo.arguments(FieldTypeSaveQuery)
	@demo.response(200)
	def post(self, args):
		"""
		新增mysql字段类型
		"""
		TableService.save_field_type(args)
		return gettext("保存成功")

	@admin_required
	@demo.arguments(FieldTypeSaveQuery)
	@demo.response(200)
	def put(self, args):
		"""
		编辑mysql字段类型
		"""
		TableService.save_field_type(args)
		return gettext("保存成功")

	@admin_required
	@demo.arguments(FieldTypeDelQuery)
	@demo.response(200)
	def delete(self, args):
		"""
		删除mysql字段类型
		"""
		TableService.delete_field_type(args)
		return gettext("操作成功")


@demo.route("/database/field")
class FieldController(MethodView):

	@admin_required
	@demo.arguments(TableDelQuery)
	@demo.response(200)
	def delete(args):
		"""
			删除mysql字段信息
		"""
		TableService.save_field(args)
		return gettext("操作成功")


@demo.route("/database/index")
class TableIndexController(MethodView):
	@admin_required
	@demo.arguments(IndexListQuery, location='query')
	@demo.response(200, IndexListResponse(many=True))
	def get(self, args):
		return TableService.index_list(args)

	@admin_required
	@demo.arguments(IndexSaveQuery)
	@demo.response(200)
	def post(self, args):
		TableService.save_index(args)
		return gettext("保存成功")

	@admin_required
	@demo.arguments(IndexSaveQuery)
	@demo.response(200)
	def put(self, args):
		TableService.save_index(args)
		return gettext("保存成功")

	@admin_required
	@demo.arguments(IndexDelQuery,location='query')
	@demo.response(200)
	def delete(self, args):
		TableService.delete_index(args)
		return gettext("删除成功")


@demo.route("/database/table/data")
class TableDataController(MethodView):
	"""
	表数据查询
	"""

	@admin_required
	@demo.arguments(TableDataQuery, location='query')
	@demo.response(200)
	def get(self, args):
		"""
		查询表的所有数据
		"""
		return TableService.query_table_data(args)
