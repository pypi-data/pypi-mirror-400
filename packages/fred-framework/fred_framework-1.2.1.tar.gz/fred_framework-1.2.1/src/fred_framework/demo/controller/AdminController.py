# python3.11
# -*- coding: utf-8 -*-
"""
 @author: Administrator
 @date: 2024/9/27 下午10:07  
 @desc:
"""

from flask import send_file, session
from flask.views import MethodView
from flask_babelplus import gettext
from flask_jwt_extended import jwt_required

from demo import demo
from demo.controller import admin_required
from demo.schema.AdminSchema import AdminLoginQuery, AdminLoginResponse, PhoneLoginQuery, \
	SendCaptchaQuery, AdminListQuery, AdminListResponse, AdminInfoResponse, RoleListResponse, \
	RoleListQuery, AdminSaveQuery, AdminSetRoleQuery, AdminForbiddenResponse, AdminForbiddenQuery, UpdatePassword, AdminDelQuery, AdminSavePut, \
	RestPassword, SuccessResponseSchema, AdminStatusResponseSchema
from demo.service.AdminService import AdminService


@demo.route("/login")
class Login(MethodView):
	@demo.arguments(AdminLoginQuery)
	@demo.response(200, AdminLoginResponse)
	def post(self, args):
		"""
		管理员帐号密码登录
		"""
		return AdminService().login(args)


@demo.route("/img_captcha")
class ImgCaptcha(MethodView):
	
	@demo.response(200, content_type="image/png")
	def get(self):
		"""
		图片验证码接口
		"""
		img = AdminService().img_captcha()
		return send_file(img, mimetype='image/png', as_attachment=False)


@demo.route("/logout")
class Logout(MethodView):
	@demo.response(200, SuccessResponseSchema)
	def post(self):
		"""
		管理员退出登录
		"""
		AdminService().logout()
		return None


@demo.route("/refresh_token")
class RefreshToken(MethodView):
	@jwt_required(refresh=True)
	@demo.response(200, SuccessResponseSchema)
	def post(self):
		"""
		刷新token
		"""
		return AdminService().refresh()


@demo.route("/send_captcha")
class SendCaptcha(MethodView):
	@demo.arguments(SendCaptchaQuery)
	@demo.response(200, SuccessResponseSchema)
	def post(self, args):
		"""
		发送验证码
		"""
		return AdminService().send_captcha(args)


@demo.route("/admin_list")
class AdminUserListController(MethodView):
	
	@admin_required
	@demo.arguments(AdminListQuery, location='query')
	@demo.response(200, AdminListResponse())
	def get(self, args):
		"""
			管理员列表
		"""
		return_data = AdminService().admin_list(args)
		return return_data


@demo.route("/admin_info")
class AdminInfoController(MethodView):
	@admin_required
	@demo.response(200, AdminInfoResponse)
	def get(self):
		"""
		获取管理员信息
		"""
		key = f'{demo.name}_user_info'
		admin_info = session[key]
		admin_info['avatar'] = 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'
		admin_info['roles'] = [
			"超级管理员",
		]
		admin_info['buttons'] = [
			"cuser.detail",
			"cuser.user"
		]
		admin_info['routes'] = [
			"pagination",
			"edit",
			"home",
			"components",
			"menu-one",
			"moremenu",
			"menu-two",
			"menu-three",
			"menu-three-1",
			"menu-three-2",
			"userList",
			"canvas",
			"news",
			"newsList",
			"newsType",
			"echarts"
		]
		admin_info['userId'] = admin_info['id']
		return admin_info




@demo.route("/admin_save")
class AdminSaveController(MethodView):
	@admin_required
	@demo.arguments(AdminSaveQuery)
	@demo.response(200, SuccessResponseSchema)
	def post(self, args):
		"""
		新增管理员信息
		"""
		return AdminService().admin_save(args)
	
	@admin_required
	@demo.arguments(AdminSavePut)
	@demo.response(200, SuccessResponseSchema)
	def put(self, args):
		"""
		修改管理员信息
		"""
		if args['id'] == 0:
			raise gettext("参数错误")
		return AdminService().admin_save(args)


@demo.route("/admin_set_role")
class AdminSetRoleController(MethodView):
	@admin_required
	@demo.arguments(AdminSetRoleQuery)
	@demo.response(200, SuccessResponseSchema)
	def post(self, args):
		"""
		设置角色
		"""
		return AdminService().admin_set_role(args)


@demo.route("/admin_forbidden")
class AdminForbiddenController(MethodView):
	@admin_required
	@demo.arguments(AdminForbiddenQuery)
	@demo.response(200, AdminForbiddenResponse)
	def put(self, args):
		"""
		设置禁用状态
		"""
		return AdminService().admin_forbidden(args)


@demo.route("/admin_delete")
class AdminDelController(MethodView):
	@admin_required
	@demo.arguments(AdminDelQuery, location='query')
	@demo.response(200, SuccessResponseSchema)
	def delete(self, args):
		"""
		删除管理员
		"""
		return AdminService().admin_del(args)


@demo.route("/update_self_password")
class UpdateSelfPasswordController(MethodView):
	@admin_required
	@demo.arguments(UpdatePassword)
	@demo.response(200, SuccessResponseSchema)
	def put(self, args):
		"""
		修改自己登录密码
		"""
		return AdminService().update_self_password(args)


@demo.route("/admin_status")
class AdminStatusController(MethodView):
	@admin_required
	@demo.response(200, AdminStatusResponseSchema)
	def get(self):
		"""
		获取用户状态
		"""
		return AdminService().admin_status()


@demo.route("/reset_password")
class RestPasswordController(MethodView):
	@admin_required
	@demo.arguments(RestPassword)
	@demo.response(200, SuccessResponseSchema)
	def put(self, args):
		"""
		重置密码
		"""
		return AdminService().reset_password(args)
