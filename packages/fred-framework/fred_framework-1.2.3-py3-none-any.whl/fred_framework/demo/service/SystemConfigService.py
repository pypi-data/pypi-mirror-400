# python3.11
# -*- coding: utf-8 -*-
"""
 @author: Administrator
 @date: 2024/10/12 20:27
"""

from flask import abort
from flask_babelplus import gettext

from fred_framework.common.Utils import Utils
from model.model import SysConfig, db


class SysConfigService:
	"""
	系统配置服务
	"""

	def config_list(self, args):
		"""
		系统配置列表
		"""
		page = args.get('page', 1)
		per_page = args.get('limit', 10)
		name = args.get('name', '')

		query = SysConfig.query
		if name:
			query = query.filter(SysConfig.name.like(f'%{name}%'))

		data = query.paginate(page=page, per_page=per_page)
		records = Utils.query_to_dict_list(data.items)

		return {
			"total": data.total,
			"records": records,
			"pageNum": data.page,
			"pageSize": data.per_page
		}

	def config_save(self, args):
		"""
		新增/修改系统配置
		"""
		config_id = args.get('id', 0)

		if config_id == 0:
			# 新增
			# 检查配置项名称是否已存在
			existing_config = SysConfig.query.filter_by(name=args['name']).first()
			if existing_config:
				abort(500, description=gettext("配置项名称已存在"))

			config = SysConfig(
				name=args['name'],
				value=args['value'],
				desc=args.get('desc', '')
			)
			db.session.add(config)
		else:
			# 修改
			config = SysConfig.query.filter_by(id=config_id).first()
			if not config:
				abort(500, description=gettext("配置不存在"))

			# 如果修改了名称，检查新名称是否已存在
			if args['name'] != config.name:
				existing_config = SysConfig.query.filter_by(name=args['name']).first()
				if existing_config:
					abort(500, description=gettext("配置项名称已存在"))

			config.name = args['name']
			config.value = args['value']
			config.desc = args.get('desc', '')

		db.session.commit()
		return ""

	def config_delete(self, args):
		"""
		删除系统配置
		"""
		config_ids = args['id']

		SysConfig.query.filter(SysConfig.id.in_(config_ids)).delete(synchronize_session=False)
		db.session.commit()
		return ""

