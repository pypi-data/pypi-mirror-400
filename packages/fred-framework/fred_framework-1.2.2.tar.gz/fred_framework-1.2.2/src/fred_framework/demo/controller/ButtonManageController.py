"""
 * @Author：cyg
 * @Package：ButtonManageController
 * @Project：Default (Template) Project
 * @name：ButtonManageController
 * @Date：2025/1/20 10:00
 * @Filename：ButtonManageController
"""
from flask.views import MethodView

from demo import demo
from demo.controller import admin_required
from demo.service.ButtonManageService import ButtonManageService
from demo.schema.ButtonManageSchema import (
	ButtonListSchema,
	ButtonAddSchema,
	ButtonUpdateSchema,
	ButtonDeleteSchema,
	ButtonListResponseSchema,
	MenuOptionResponseSchema,
	ApiUrlResponseSchema
)
from fred_framework.common.PageSchema import PageSchemaFactory


@demo.route("/button/manage")
class ButtonManageController(MethodView):

	@admin_required
	@demo.arguments(ButtonListSchema, location='query')
	@demo.response(200, PageSchemaFactory(ButtonListResponseSchema))
	def get(self, args):
		"""
		获取按钮列表
		"""
		return ButtonManageService().button_list(args)

	@admin_required
	@demo.arguments(ButtonAddSchema)
	@demo.response(200)
	def post(self, args):
		"""
		新增按钮
		"""
		button_id = ButtonManageService().add_button(args)
		return {"id": button_id, "message": "新增成功"}

	@admin_required
	@demo.arguments(ButtonUpdateSchema)
	@demo.response(200)
	def put(self, args):
		"""
		更新按钮
		"""
		button_id = ButtonManageService().update_button(args)
		return {"id": button_id, "message": "更新成功"}

	@admin_required
	@demo.arguments(ButtonDeleteSchema, location='query')
	@demo.response(200)
	def delete(self, args):
		"""
		删除按钮
		"""
		ButtonManageService().delete_button(args)
		return {"message": "删除成功"}


@demo.route("/button/manage/menu")
class MenuController(MethodView):

	@admin_required
	@demo.response(200, MenuOptionResponseSchema(many=True))
	def get(self):
		"""
		获取菜单列表（用于下拉选择）
		"""
		return ButtonManageService().get_menu_list()


@demo.route("/button/manage/api-urls")
class ApiUrlController(MethodView):

	@admin_required
	@demo.response(200, ApiUrlResponseSchema(many=True))
	def get(self):
		"""
		获取所有接口URL列表
		"""
		return ButtonManageService().get_all_api_urls()
