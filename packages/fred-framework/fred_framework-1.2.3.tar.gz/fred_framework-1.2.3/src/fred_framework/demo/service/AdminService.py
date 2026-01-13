# python3.11
# -*- coding: utf-8 -*-
"""
 @author: Administrator
 @date: 2024/9/27 下午10:08
"""
import json
import random
import time

from flask import session, jsonify, abort, current_app, request
from flask_babelplus import gettext
from flask_jwt_extended import unset_jwt_cookies, decode_token

from demo import demo
from demo.schema.AdminSchema import AdminLoginResponse
from demo.service.RoleService import RoleService
from fred_framework.common.AliyunSms import AliyunSms
from fred_framework.common.Email import Email
from fred_framework.common.ImageVerification import ImageVerification
from fred_framework.common.Utils import Utils
from model.model import Admin, db
from sqlalchemy import func

class AdminService:
	"""
		 @desc: 管理员 服务
	"""

	def login(self, args):
		"""
		帐号密码登录
		"""

		username = args.get("username", None)
		is_phone = Utils.validate_phone(username)
		password = args.get("password", None)
		captcha_code = args.get("captcha", None)
		if "captcha_code" not in session:
			abort(400, description=gettext("验证码无效！"))
		if captcha_code is None or captcha_code.lower() != session["captcha_code"].lower():
			abort(400, description=gettext("验证码有误!"))

		if username is None or password is None:
			abort(400, description=gettext("账号密码不能为空！"))
		session["captcha_code"] = ""
		admin_info = None
		if is_phone:
			phone_prefix = username[:3]
			phone_suffix = username[-4:]
			admin_list = Admin.query.filter_by(phone_prefix=phone_prefix, phone_suffix=phone_suffix, deleted=0, forbidden=0).all()
			if not admin_list:
				abort(400, description=gettext("账户密码错误"))
			for item in admin_list:
				pwd_dict = Utils.hash_encrypt(password, item.salt)
				user_phone = Utils.fernet_decrypt(item.phone_encrypt)
				if pwd_dict['hashed_text'] == item.password and user_phone == username:
					admin_info = item
					break
		else:
			admin_info = Admin.query.filter_by(username=username, deleted=0, forbidden=0).first()
			if not admin_info:
				abort(400, description=gettext("账户密码错误"))
			pwd_dict = Utils.hash_encrypt(password, admin_info.salt)
			if admin_info.password != pwd_dict['hashed_text']:
				abort(400, description=gettext("账户密码错误"))
		if not admin_info:
			current_app.logger.error(admin_info)
			abort(400, description=gettext("账户密码错误!"))
		identity = AdminLoginResponse().dump(admin_info)
		token = Utils.create_token(identity=json.dumps(identity), claims={"role": demo.name})
		admin_data = {**identity, **token}
		return admin_data

	def logout(self):
		response = jsonify({"logout": True})

		raw_token = request.headers.get('Authorization', '').replace('Bearer ', '')

		if raw_token:
			try:
				redis_client = current_app.extensions.get('redis')
				if redis_client:
					decoded_token = decode_token(raw_token)
					jti = decoded_token['jti']  # 唯一标识符
					exp = decoded_token['exp']  # 过期时间戳
					# 将 token 加入黑名单，设置和 token 相同的过期时间
					redis_client.setex(jti, int(exp - time.time()), 'revoked')
			except Exception as e:
				return jsonify({"msg": "无效的 token"}), 400
		unset_jwt_cookies(response)
		return ""

	def refresh(self):
		key = f'{demo.name}_user_info'
		new_access_token = Utils.create_token(identity=session[key], is_refresh=True)
		return new_access_token

	def img_captcha(self):
		image = ImageVerification()
		image.line_num = 4
		image.height = 50
		img, code = image.draw_verify_code()
		session['captcha_code'] = code
		return img

	def send_captcha(self, args):
		"""
			短信/邮箱验证码
		"""
		# 生成随机6个数字的字符串 作为验证码
		code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
		if Utils.validate_phone(args['acceptor']):
			AliyunSms.send_code(args['acceptor'], code)
			session['captcha'] = code
			return ""
		if Utils.validate_email(args['acceptor']):
			content = f"你的验证码为:{code},有效时间为5分钟!"
			Email().send_mail(args['acceptor'], "注册验证码", content)
			session['captcha'] = code
			return ""
		abort(400, description=gettext("手机号或邮箱格式不正确"))

	def admin_list(self, args):
		"""
		管理员 列表
		"""
		from model.model import AdminRoleRelation, AdminRole

		username = args.get('username', '')
		page = args.get('page', 1)
		per_page = args.get('limit', 10)
		phone = args.get('phone', 0)
		forbidden = args.get('forbidden', -1)
		where = [Admin.deleted == 0]
		last_login = args.get('lastLogin', [])
		if username:
			where.append(Admin.username.like(f'%{username}%'))
		if phone:
			where.append(Admin.phone_suffix == phone)
		if forbidden != -1:
			where.append(Admin.forbidden == forbidden)
		if last_login:
			where.append(Admin.last_login.between(
				Utils.datetime_to_timestamp(last_login[0]),
				Utils.datetime_to_timestamp(last_login[1])
			))

		# 先查询管理员列表
		with_entities = (
			Admin.id,
			Admin.username,
			Admin.phone_prefix,
			Admin.phone_suffix,
			Admin.created,
			Admin.forbidden,
			Admin.last_login.label('lastLogin'),
			Admin.avatar
		)

		query = Admin.query \
			.filter(*where) \
			.with_entities(*with_entities)

		data = query.paginate(page=page, per_page=per_page)
		records = Utils.query_to_dict_list(data.items)

		# 为每个用户查询角色信息
		user_ids = [item['id'] for item in records]
		role_relations = {}
		role_ids_map = {}
		if user_ids:
			role_data = AdminRole.query \
				.join(AdminRoleRelation, AdminRole.id == AdminRoleRelation.role) \
				.filter(AdminRoleRelation.admin_id.in_(user_ids)) \
				.with_entities(AdminRoleRelation.admin_id, AdminRole.name, AdminRoleRelation.role) \
				.all()

			for admin_id, role_name, role_id in role_data:
				if admin_id not in role_relations:
					role_relations[admin_id] = []
					role_ids_map[admin_id] = []
				role_relations[admin_id].append(role_name)
				role_ids_map[admin_id].append(role_id)

		for item in records:
			item['created'] = Utils.timestamp_to_utc(item['created'])
			item['lastLogin'] = Utils.timestamp_to_utc(item['lastLogin'])
			item['phone'] = f"{str(item['phone_prefix'])}****{str(item['phone_suffix'])}"
			# 设置角色名称和角色ID列表
			user_roles = role_relations.get(item['id'], [])
			item['roleName'] = ','.join(user_roles) if user_roles else ''
			item['role_ids'] = role_ids_map.get(item['id'], [])

		return_data = {
			'records': records,
			'total': data.total,
			'pageNum': data.page,
			'pageSize': data.per_page,
		}
		return return_data

	def admin_save(self, args):
		"""
		管理员 新增/编辑
		"""
		if args['id'] > 0:
			admin_info = Admin.query.filter_by(id=args['id'], deleted=0).first()
			if not admin_info:
				abort(400, description=gettext("管理员不存在或已删除"))
			admin_info.username = args['username']
			admin_info.avatar = args.get("avatar", "")

			# 处理角色关联
			role_ids = args.get('role_ids', [])
			from model.model import AdminRoleRelation
			from datetime import datetime

			# 删除该管理员的所有角色关系
			AdminRoleRelation.query.filter_by(admin_id=args['id']).delete()

			# 添加新的角色关系
			for role_id in role_ids:
				role_relation = AdminRoleRelation(
					admin_id=args['id'],
					role=role_id,
					created=datetime.now()
				)
				db.session.add(role_relation)
		else:
			phone = args.get('phone')
			if not phone:
				abort(400, description=gettext("手机号不能为空"))
			phone_prefix = phone[:3]
			phone_suffix = phone[-4:]
			admin_list = Admin.query.filter_by(phone_prefix=phone_prefix, phone_suffix=phone_suffix, deleted=0).filter(Admin.phone_encrypt.isnot(None), Admin.phone_encrypt != '').all()
			for item in admin_list:
				if not item.phone_encrypt:
					continue
				user_phone = Utils.fernet_decrypt(item.phone_encrypt)
				if user_phone == phone:
					abort(400, description=gettext("该手机号已存在"))
			username_count = Admin.query.filter_by(username=args['username'], deleted=0).count()
			if username_count:
				abort(400, description=gettext("用户名已存在"))
			admin_info = Admin()
			password = Utils.md5_encrypt(current_app.config.get('DEFAULT_PASSWORD'))
			hash_data = Utils.hash_encrypt(password)
			admin_info.password = hash_data['hashed_text']
			admin_info.salt = hash_data['salt']
			admin_info.phone_prefix = phone[:3]
			admin_info.phone_suffix = phone[-4:]
			admin_info.username = args['username']
			admin_info.phone_encrypt = Utils.fernet_encrypt(phone)
			admin_info.avatar = args.get("avatar", "")
			admin_info.deleted = 0  # 设置删除状态为0（未删除）
			admin_info.forbidden = 0  # 设置禁用状态为0（未禁用）
			admin_info.created = int(time.time())
			db.session.add(admin_info)
			db.session.flush()  # 获取新插入的ID

			# 处理角色关联
			role_ids = args.get('role_ids', [])
			from model.model import AdminRoleRelation
			from datetime import datetime

			# 添加新的角色关系
			for role_id in role_ids:
				role_relation = AdminRoleRelation(
					admin_id=admin_info.id,
					role=role_id,
					created=datetime.now()
				)
				db.session.add(role_relation)

		db.session.commit()

	def admin_set_role(self, args):
		"""
		管理员 设置角色
		"""
		from model.model import AdminRoleRelation
		from datetime import datetime

		admin_info = Admin.query.filter_by(id=args['user_id'], deleted=0).first()
		if not admin_info:
			abort(400, description=gettext("管理员不存在或已删除"))

		# 删除该管理员的所有角色关系
		AdminRoleRelation.query.filter_by(admin_id=args['user_id']).delete()

		# 添加新的角色关系
		for role_id in args['role_id_list']:
			role_relation = AdminRoleRelation(
				admin_id=args['user_id'],
				role=role_id,
				created=datetime.now()
			)
			db.session.add(role_relation)

		db.session.commit()
		return ""

	def admin_forbidden(self, args):
		"""
		管理员 设置状态
		"""
		from model.model import AdminRoleRelation

		admin_info = Admin.query.filter_by(id=args['id'], deleted=0).first()
		if not admin_info:
			abort(400, description=gettext("管理员不存在或已删除"))

		# 判断是否是系统管理员（role_id=1）
		sys_admin_relation = AdminRoleRelation.query.filter_by(admin_id=args['id'], role=1).first()
		if sys_admin_relation:
			abort(400, description=gettext("系统管理员无法禁用"))
		forbidden = 0 if admin_info.forbidden else 1
		admin_info.forbidden = forbidden
		db.session.commit()
		return forbidden

	def admin_del(self, args):
		"""
		管理员 删除
		"""
		from model.model import AdminRoleRelation

		# 查询要删除的用户中是否有系统管理员（role_id=1）
		sys_admin_ids = db.session.query(AdminRoleRelation.admin_id) \
			.filter(AdminRoleRelation.role == 1, AdminRoleRelation.admin_id.in_(args['id'])) \
			.distinct() \
			.all()

		if sys_admin_ids:
			abort(400, description=gettext("系统管理员无法删除"))

		Admin.query \
			.filter(Admin.id.in_(args['id']), Admin.deleted == 0) \
			.update({Admin.deleted: 1})
		db.session.commit()
		return ""

	def update_self_password(self, args):
		"""
		管理员 修改密码
		"""
		if args['newPassword'] != args['repPassword']:
			abort(400, description=gettext("两次密码不一致"))
		key = f'{demo.name}_user_info'
		user_info = session[key]
		admin_info = Admin.query.filter_by(id=user_info['id'], deleted=0).first()
		if not admin_info:
			abort(400, description=gettext("管理员不存在或已删除"))
		old_pwd = Utils.hash_encrypt(args['oldPassword'], admin_info.salt)['hashed_text']
		if old_pwd != admin_info.password:
			abort(400, description=gettext("旧密码错误"))
		hash_data = Utils.hash_encrypt(args['newPassword'])
		admin_info.password = hash_data['hashed_text']
		admin_info.salt = hash_data['salt']
		db.session.commit()
		return ""

	def admin_status(self):
		data = [{"label": "正常", "value": 0}, {"label": "禁用", "value": 1}]
		return data

	def reset_password(self, args):
		admin_id = args['id']
		admin_info = Admin.query.filter_by(id=admin_id, deleted=0).first()
		if not admin_info:
			abort(400, description=gettext("管理员不存在或已删除"))
		password = Utils.md5_encrypt(current_app.config.get('DEFAULT_PASSWORD'))
		hash_data = Utils.hash_encrypt(password)
		admin_info.password = hash_data['hashed_text']
		admin_info.salt = hash_data['salt']
		db.session.commit()
