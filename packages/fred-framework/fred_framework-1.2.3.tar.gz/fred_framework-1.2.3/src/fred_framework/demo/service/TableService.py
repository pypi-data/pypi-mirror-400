# python3.11
# -*- coding: utf-8 -*-
"""
 @author: Administrator
 @date: 2024/7/31 下午10:51
"""
from datetime import datetime
import threading
import time

from flask import abort, current_app
from flask_babelplus import gettext

from fred_framework.common.Sqlacodegen import Sqlacodegen
from fred_framework.common.Utils import Utils
from model.model import SysTable, db, SysTableField, SysFieldType, SysTableIndex
from sqlalchemy import Column, Integer, String, DateTime, MetaData, Table, text  # 新增：导入 text 函数


class TableService:
	"""
		 @desc:
	"""

	@staticmethod
	def _ensure_data_dir():
		"""
		确保 data 目录存在并返回目录路径
		"""
		import os
		# 当前文件: demo/service/TableService.py -> 工程根目录在上上上级
		service_dir = os.path.dirname(os.path.abspath(__file__))
		demo_dir = os.path.dirname(service_dir)
		project_root = os.path.dirname(demo_dir)
		data_dir = os.path.join(project_root, 'data')
		if not os.path.exists(data_dir):
			os.makedirs(data_dir, exist_ok=True)
		return data_dir

	@staticmethod
	def _escape_sql_string(value: str) -> str:
		"""
		转义 SQL 字符串中的单引号
		"""
		if value is None:
			return ''
		return str(value).replace("'", "''")

	@staticmethod
	def _log_sql(sql: str) -> None:
		"""
		将 SQL 语句写入 data/YYYYMMDD.sql，每天一个文件，新内容追加到文件末尾
		"""
		from datetime import datetime as _dt
		import os
		# 生成文件名：YYYYMMDD.sql（每天一个文件）
		now = _dt.now()
		date_part = now.strftime('%Y%m%d')
		filename = f"{date_part}.sql"
		data_dir = TableService._ensure_data_dir()
		path = os.path.join(data_dir, filename)
		# 统一以分号结尾，便于回放
		final_sql = sql.strip()
		if not final_sql.endswith(';'):
			final_sql += ';'
		# 在每条 SQL 前添加时间戳，方便查看执行时间
		timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
		# 使用追加模式打开文件
		with open(path, 'a', encoding='utf-8') as f:
			f.write(f"-- {timestamp}\n{final_sql}\n\n")

	@staticmethod
	def _log_orm_insert(table_name: str, data: dict) -> None:
		"""
		记录 INSERT 操作的 SQL
		"""
		if not data:
			return
		columns = []
		values = []
		for key, value in data.items():
			columns.append(f"`{key}`")
			if value is None:
				values.append("NULL")
			elif isinstance(value, (int, float)):
				values.append(str(value))
			elif isinstance(value, datetime):
				values.append(f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'")
			elif isinstance(value, str) and TableService._is_datetime_string(value):
				# 处理字符串格式的日期时间
				values.append(f"'{value}'")
			else:
				escaped = TableService._escape_sql_string(str(value))
				values.append(f"'{escaped}'")
		sql = f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ({', '.join(values)})"
		TableService._log_sql(sql)

	@staticmethod
	def _log_orm_update(table_name: str, data: dict, where_clause: str) -> None:
		"""
		记录 UPDATE 操作的 SQL
		"""
		if not data:
			return
		set_parts = []
		for key, value in data.items():
			if value is None:
				set_parts.append(f"`{key}` = NULL")
			elif isinstance(value, (int, float)):
				set_parts.append(f"`{key}` = {value}")
			elif isinstance(value, datetime):
				set_parts.append(f"`{key}` = '{value.strftime('%Y-%m-%d %H:%M:%S')}'")
			elif isinstance(value, str) and TableService._is_datetime_string(value):
				# 处理字符串格式的日期时间
				set_parts.append(f"`{key}` = '{value}'")
			else:
				escaped = TableService._escape_sql_string(str(value))
				set_parts.append(f"`{key}` = '{escaped}'")
		sql = f"UPDATE `{table_name}` SET {', '.join(set_parts)} WHERE {where_clause}"
		TableService._log_sql(sql)

	@staticmethod
	def _is_datetime_string(value: str) -> bool:
		"""
		判断字符串是否为日期时间格式 (YYYY-MM-DD HH:MM:SS)
		"""
		if not isinstance(value, str):
			return False
		try:
			datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
			return True
		except ValueError:
			return False

	@staticmethod
	def _log_orm_delete(table_name: str, where_clause: str) -> None:
		"""
		记录 DELETE 操作的 SQL
		"""
		sql = f"DELETE FROM `{table_name}` WHERE {where_clause}"
		TableService._log_sql(sql)

	def table_list(self, args):
		"""
		表格列表
		"""
		# 兼容前端传参，优先使用 pageNum/pageSize，其次兼容 page/limit
		page = args.get('pageNum', args.get('page', 1))
		per_page = args.get('pageSize', args.get('limit', 10))
		query = SysTable.query
		name = args.get('name', None)
		desc = args.get('desc', None)
		if name:
			query = query.filter(SysTable.name.like(f"%{name}%"))
		if desc:
			query = query.filter(SysTable.desc.like(f"%{desc}%"))
		data = query.order_by(SysTable.name).paginate(page=page, per_page=per_page)
		records = Utils.query_to_dict_list(data.items)
		for item in records:
			field_list = SysTableField.query.filter(SysTableField.table_id == item['id'], SysTableField.deleted == 0).all()
			# 获取该表所有索引涉及的字段名，统一 strip 和 lower
			index_fields = set()
			indexes = SysTableIndex.query.filter(SysTableIndex.table_id == item['id']).all()
			for idx in indexes:
				idx_fields = [x.strip().lower() for x in idx.index_fields.split(',') if x.strip()]
				index_fields.update(idx_fields)
			# 字段列表增加 is_index 字段，统一 strip 和 lower
			field_dicts = Utils.query_to_dict_list(field_list)
			for f in field_dicts:
				f_name = f['field_name'].strip().lower() if f['field_name'] else ''
				f['is_index'] = f_name in index_fields
			item["field"] = field_dicts
		return {
			"total": data.total,
			"records": records,
			"pageNum": data.page,
			"pageSize": data.per_page
		}

	@staticmethod
	def save_table(args):
		"""
		table表新增和修改数据
		"""
		id = args.get("id", 0)
		fields = args.get("field", [])
		now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		name = args.get("name", "")
		table_desc = args.get("desc", "")
		new_fields = None
		if not fields:
			abort(400, gettext("表字段不能为空"))
		if SysTable.query.filter(SysTable.name == name, SysTable.id != id, SysTable.deleted == 0).first():
			abort(400, gettext("表名不能重复"))
		field_names = [field.get("field_name") for field in fields]
		if len(field_names) != len(set(field_names)):
			abort(400, gettext("字段名称不能重复"))
		is_add = True
		args["modified"] = now_time
		args.pop("field", None)
		if id <= 0:
			args["created"] = now_time
			sys_table = SysTable(**args)
			db.session.add(sys_table)
			try:
				db.session.flush()
				# 尝试直接查询数据库
				query_result = db.session.query(SysTable).filter_by(name=name).first()
				id = query_result.id
				# 记录 INSERT SQL
				insert_data = args.copy()
				insert_data['id'] = id
				TableService._log_orm_insert('sys_table', insert_data)
			except Exception as e:
				db.session.rollback()
				abort(400, gettext("保存失败,刷新会话出错"))
		else:
			is_add = False
			old_table_info = SysTable.query.filter(SysTable.id == id, SysTable.deleted == 0).first()
			# 先判断数据库中的数据和提交的数据是否相同 不同才修改
			if old_table_info and (old_table_info.name != name or old_table_info.desc != table_desc):
				TableService.update_table_info(args, old_table_info)
				old_table_info.name = name
				old_table_info.desc = table_desc
				# 记录 UPDATE SQL
				update_data = {
					'name': name,
					'desc': table_desc,
					'modified': now_time
				}
				TableService._log_orm_update('sys_table', update_data, f"id = {id}")
		del_fields = None
		if not id:
			db.session.rollback()
			abort(400, gettext("保存失败,无法获取表ID"))
		if fields:
			new_fields, del_fields = TableService.save_fields(id, fields)
		# 保存成功后 在数据库中新建对应的表和字段,默认添加id字段并设置逐渐和自增属性
		if is_add and new_fields:
			TableService.created_table(name, table_desc, fields)
		if not is_add and new_fields:
			TableService.update_table_fields(name, new_fields)
			# 删除字段
			TableService.delete_table_fields(name, del_fields)
		db.session.commit()
		# 修改数据库以后 需要重新生成模型文件 - 使用异步处理避免开发环境重启导致前端请求断开
		TableService._async_create_models(current_app)
		return True

	@staticmethod
	def save_fields(table_id, fields):
		"""
		保存字段到数据库表中
		"""

		now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		new_fields = []
		old_fields = SysTableField.query.filter(SysTableField.table_id == table_id,
												SysTableField.deleted == 0).all()
		# 新的需要新增和修改的字段
		new_save_fields = []
		# 不需要修改的字段
		no_update_fields = []
		for field in fields:
			field_name = field.get("field_name")
			field_type = field.get("field_type")
			field_desc = field.get("field_desc")
			default_value = field.get("default", "")
			is_new = True
			for old_field in old_fields:
				if old_field.field_name == field_name:
					if old_field.field_desc == field_desc and old_field.field_type == field_type and getattr(old_field, 'default',
																											 '') == default_value:
						is_new = False
						no_update_fields.append(old_field.id)
						continue
					field["id"] = old_field.id
					continue
			if is_new:
				new_save_fields.append(field)
		# 获取 old_fields中的id
		ol_ids = [old_field.id for old_field in old_fields]
		# 获取new_save_fields中的id
		new_ids = [new_field.get("id") for new_field in new_save_fields]
		# 取old_ids中存在 new_ids不存在的id
		del_ids_1 = [old_id for old_id in ol_ids if old_id not in new_ids]
		# 取消 不处理的字段
		del_ids = [old_id for old_id in del_ids_1 if old_id not in no_update_fields]
		if del_ids:
			# 1. 获取要删除字段的 field_name
			del_fields_objs = SysTableField.query.filter(SysTableField.id.in_(del_ids)).all()
			del_field_names = [f.field_name for f in del_fields_objs]
			# 2. 检查索引是否引用这些字段
			indexes = SysTableIndex.query.filter(SysTableIndex.table_id == table_id, SysTableIndex.deleted == 0).all()
			for idx in indexes:
				idx_fields = [x.strip() for x in idx.index_fields.split(',')]
				for del_field in del_field_names:
					if del_field in idx_fields:
						abort(400, gettext(f"字段 {del_field} 被索引 {idx.index_name} 引用，请先修改索引再删除字段"))
			# 3. 没有引用才允许逻辑删除
			SysTableField.query.filter(SysTableField.id.in_(del_ids)).update({"deleted": 1, "modified": now_time})
			# 记录 UPDATE SQL（逻辑删除）
			for del_id in del_ids:
				TableService._log_orm_update('sys_table_fields', {"deleted": 1, "modified": now_time}, f"id = {del_id}")

		for field in new_save_fields:
			field["table_id"] = table_id
			id = field.get("id", 0)
			if id <= 0:
				field["created"] = now_time
				new_entry = SysTableField(**field)
				db.session.add(new_entry)
				db.session.flush()  # 获取新插入记录的 id
				insert_id = new_entry.id
				old_field_name = ""
				# 记录 INSERT SQL
				insert_data = field.copy()
				insert_data['id'] = insert_id
				TableService._log_orm_insert('sys_table_fields', insert_data)
			else:
				field["modified"] = now_time
				field['deleted'] = 0
				old_fields_info = SysTableField.query.get(id)
				old_field_name = old_fields_info.field_name
				if old_fields_info:
					# 使用字典的键来更新对象的属性
					for key, value in field.items():
						setattr(old_fields_info, key, value)
					# 记录 UPDATE SQL（排除 id 字段，因为 id 在 WHERE 条件中）
					update_data = {k: v for k, v in field.items() if k != 'id'}
					TableService._log_orm_update('sys_table_fields', update_data, f"id = {id}")
			one = field.copy()
			type_info = SysFieldType.query.filter(SysFieldType.id == field.get("field_type")).first()
			one["field_type"] = type_info.field_type
			one["old_field_name"] = old_field_name
			new_fields.append(one)
		return new_fields, del_ids

	@staticmethod
	def get_column_type(field_type):
		"""
		统一字段类型映射，返回 (SQLAlchemy类型, MySQL类型字符串)
		"""
		mapping = {
			'string': (String(255), 'VARCHAR(255)'),
			'integer': (Integer, 'INT'),
			'datetime': (DateTime, 'DATETIME'),
			'text': (db.Text, 'TEXT'),
			'decimal': (db.Numeric, 'DECIMAL(20,6)'),
			'date': (db.Date, 'DATE'),
			'smallint': (db.SmallInteger, 'SMALLINT'),
			'tinyint': (db.SmallInteger, 'TINYINT'),
			'float': (db.Float, 'FLOAT')
		}
		txt = gettext("不支持的字段类型")
		if field_type not in mapping:
			abort(400, f"{txt}: {field_type}")
		return mapping[field_type]

	@staticmethod
	def parse_default_value(field_desc):
		"""
		从字段描述中解析默认值
		格式: 原描述 [默认值: 值]
		"""
		import re
		if not field_desc:
			return None, field_desc

		# 匹配 [默认值: xxx] 格式
		match = re.search(r'\[默认值:\s*([^\]]+)\]', field_desc)
		if match:
			default_value = match.group(1).strip()
			# 移除默认值部分，保留原始描述
			clean_desc = re.sub(r'\s*\[默认值:\s*[^\]]+\]', '', field_desc).strip()
			return default_value, clean_desc

		return None, field_desc

	@staticmethod
	def get_default_value_for_column(field_type, default_value):
		"""
		根据字段类型和默认值生成SQLAlchemy列默认值
		返回 (server_default值, 是否设置默认值)
		"""
		if default_value is None or default_value == '':
			# 空值或空字符串的处理 - 对于所有类型都不设置默认值
			return None, False

		# 非空默认值的处理
		if field_type in ['integer', 'smallint', 'tinyint']:
			try:
				int_val = int(default_value)
				return str(int_val), True
			except ValueError:
				# 转换失败时，不设置默认值
				return None, False
		elif field_type in ['float', 'decimal']:
			try:
				float_val = float(default_value)
				return str(float_val), True
			except ValueError:
				# 转换失败时，不设置默认值
				return None, False
		elif field_type == 'datetime':
			if default_value.lower() in ['now', 'current_timestamp', 'current_timestamp()']:
				return 'CURRENT_TIMESTAMP', True
			else:
				try:
					from datetime import datetime
					datetime.strptime(default_value, '%Y-%m-%d %H:%M:%S')
					return f"'{default_value}'", True
				except ValueError:
					# 转换失败时，不设置默认值
					return None, False
		elif field_type == 'date':
			if default_value.lower() in ['now', 'current_date', 'current_date()']:
				return 'CURRENT_DATE', True
			else:
				try:
					from datetime import datetime
					datetime.strptime(default_value, '%Y-%m-%d')
					return f"'{default_value}'", True
				except ValueError:
					# 转换失败时，不设置默认值
					return None, False
		elif field_type == 'text':
			# text类型通常不设置默认值，除非明确提供
			if default_value.strip():
				return f"'{default_value}'", True
			return None, False
		else:  # string类型
			# string类型空字符串不设置默认值，避免无意义的空字符串默认值
			if default_value.strip():
				return f"'{default_value}'", True
			return None, False

	@staticmethod
	def get_default_value_clause(field_type, default_value):
		"""
		根据字段类型和默认值生成SQL默认值子句
		返回SQL默认值子句字符串
		"""
		if default_value is None or default_value == '':
			# 空值或空字符串的处理 - 对于所有类型都不设置默认值
			return ""

		# 非空默认值的处理
		if field_type in ['integer', 'smallint', 'tinyint']:
			try:
				return f" DEFAULT {int(default_value)}"
			except ValueError:
				# 转换失败时，不设置默认值
				return ""
		elif field_type in ['float', 'decimal']:
			try:
				return f" DEFAULT {float(default_value)}"
			except ValueError:
				# 转换失败时，不设置默认值
				return ""
		elif field_type == 'datetime':
			if default_value.lower() in ['now', 'current_timestamp', 'current_timestamp()']:
				return " DEFAULT CURRENT_TIMESTAMP"
			else:
				try:
					from datetime import datetime
					datetime.strptime(default_value, '%Y-%m-%d %H:%M:%S')
					return f" DEFAULT '{default_value}'"
				except ValueError:
					# 转换失败时，不设置默认值
					return ""
		elif field_type == 'date':
			if default_value.lower() in ['now', 'current_date', 'current_date()']:
				return " DEFAULT CURRENT_DATE"
			else:
				try:
					from datetime import datetime
					datetime.strptime(default_value, '%Y-%m-%d')
					return f" DEFAULT '{default_value}'"
				except ValueError:
					# 转换失败时，不设置默认值
					return ""
		elif field_type == 'text':
			# text类型通常不设置默认值，除非明确提供
			if default_value.strip():
				return f" DEFAULT '{default_value}'"
			return ""
		else:  # string类型
			# string类型空字符串不设置默认值，避免无意义的空字符串默认值
			if default_value.strip():
				return f" DEFAULT '{default_value}'"
			return ""

	@staticmethod
	def created_table(name: str, table_desc: str, fields: list) -> None:
		"""
		动态创建数据库表及其字段，默认添加一个名为 'id' 的字段作为主键和自增列。
		:param name: 表名
		:param table_desc: 表说明
		:param fields: 字段列表，每个字段为字典格式，包含字段名、类型等信息
		"""
		metadata = MetaData()
		columns = [
			Column('id', Integer, primary_key=True, autoincrement=True),
		]
		for field in fields:
			field_name = field.get('field_name')
			field_type_id = field.get('field_type')
			field_desc = field.get('field_desc', '')
			default_value = field.get('default', '')
			if not field_name or not field_type_id:
				abort(400, gettext("字段名和字段类型不能为空"))

			# 通过field_type_id查询实际的字段类型字符串
			type_info = SysFieldType.query.filter(SysFieldType.id == field_type_id).first()
			if not type_info:
				abort(400, gettext(f"字段类型ID: {field_type_id} 不存在"))
			field_type = type_info.field_type

			col_type, _ = TableService.get_column_type(field_type)

			# 构建列定义
			column_kwargs = {'comment': field_desc}

			# 使用统一的默认值处理函数
			server_default, should_set_default = TableService.get_default_value_for_column(field_type, default_value)
			if should_set_default:
				column_kwargs['server_default'] = server_default

			columns.append(Column(field_name, col_type, **column_kwargs))
		table = Table(name, metadata, *columns, comment=table_desc)
		# 记录等效的 CREATE TABLE SQL（便于审计/回放）
		col_sql_parts = ["`id` INT AUTO_INCREMENT PRIMARY KEY"]
		for field in fields:
			field_name = field.get('field_name')
			field_type_id = field.get('field_type')
			field_desc = field.get('field_desc', '')
			default_value = field.get('default', '')
			type_info = SysFieldType.query.filter(SysFieldType.id == field_type_id).first()
			if type_info:
				_, sql_type = TableService.get_column_type(type_info.field_type)
				default_clause = TableService.get_default_value_clause(type_info.field_type, default_value)
				escaped_comment = TableService._escape_sql_string(field_desc)
				col_sql_parts.append(f"`{field_name}` {sql_type}{default_clause} COMMENT '{escaped_comment}'")
		escaped_table_comment = TableService._escape_sql_string(table_desc)
		create_sql = f"CREATE TABLE IF NOT EXISTS `{name}` (\n  " + ",\n  ".join(col_sql_parts) + f"\n) COMMENT='{escaped_table_comment}'"
		TableService._log_sql(create_sql)
		table.create(bind=db.engine, checkfirst=True)

	@staticmethod
	def update_table_info(args, old_info):
		"""
	修改表名字和注释信息
		"""
		# 修改表名
		if old_info.name != args.get('name'):
			sql = f"ALTER TABLE `{old_info.name}` RENAME TO `{args.get('name')}`"
			TableService._log_sql(sql)
			db.session.execute(text(sql))

		# 添加表注释
		if old_info.desc != args.get('desc'):
			table_name = args.get('name')
			table_desc = args.get('desc')
			escaped = TableService._escape_sql_string(table_desc)
			sql = f"ALTER TABLE `{table_name}` COMMENT = '{escaped}'"
			TableService._log_sql(sql)
			db.session.execute(text(f"ALTER TABLE `{table_name}` COMMENT = :table_desc"), {"table_desc": table_desc})

	@staticmethod
	def update_table_fields(table_name, new_fields):
		"""
		修改表字段信息
		:param table_name: 表名
		:param new_fields: 字段列表，每个字段为字典格式，包含字段名、类型等信息
		"""
		for field in new_fields:
			field_name = field.get('field_name')
			field_type = field.get('field_type')  # 这里已经是字符串类型了，因为在save_fields中已经转换过
			field_desc = field.get('field_desc', '')
			default_value = field.get('default', '')
			id = field.get('id', 0)
			old_field_name = field.get('old_field_name', '')
			_, sql_type = TableService.get_column_type(field_type)

			# 使用统一的默认值处理函数生成SQL默认值子句
			default_clause = TableService.get_default_value_clause(field_type, default_value)

			if id > 0:
				if old_field_name and old_field_name != field_name:
					escaped_comment = TableService._escape_sql_string(field_desc)
					sql = f"ALTER TABLE `{table_name}` CHANGE `{old_field_name}` `{field_name}` {sql_type}{default_clause} COMMENT '{escaped_comment}'"
					TableService._log_sql(sql)
					db.session.execute(text(f"ALTER TABLE `{table_name}` CHANGE `{old_field_name}` `{field_name}` {sql_type}{default_clause} COMMENT :comment"), {"comment": field_desc})
				else:
					escaped_comment = TableService._escape_sql_string(field_desc)
					sql = f"ALTER TABLE `{table_name}` MODIFY COLUMN `{field_name}` {sql_type}{default_clause} COMMENT '{escaped_comment}'"
					TableService._log_sql(sql)
					db.session.execute(text(f"ALTER TABLE `{table_name}` MODIFY COLUMN `{field_name}` {sql_type}{default_clause} COMMENT :comment"), {"comment": field_desc})
			else:
				escaped_comment = TableService._escape_sql_string(field_desc)
				sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{field_name}` {sql_type}{default_clause} COMMENT '{escaped_comment}'"
				TableService._log_sql(sql)
				db.session.execute(text(f"ALTER TABLE `{table_name}` ADD COLUMN `{field_name}` {sql_type}{default_clause} COMMENT :comment"), {"comment": field_desc})

	@staticmethod
	def delete_table_fields(table_name, fields_ids):
		"""
		删除表字段
		"""
		if not fields_ids:
			return None
		name_list = SysTableField.query.filter(SysTableField.id.in_(fields_ids)).all()
		# 获取所有field_name
		field_name_list = [name.field_name for name in name_list]
		# 从mysql表中删除field_name_list列表中所有字段
		# 分别执行每个DROP COLUMN语句，但在同一个事务中
		for field_name in field_name_list:
			sql = f"ALTER TABLE `{table_name}` DROP COLUMN `{field_name}`"
			TableService._log_sql(sql)
			db.session.execute(text(sql))

	@staticmethod
	def field_type_list(args):
		"""
		sys_field_type 列表
		"""
		# 兼容前端传参，优先使用 pageNum/pageSize，其次兼容 page/limit
		page = args.get('pageNum', args.get('page', 1))
		per_page = args.get('pageSize', args.get('limit', 10))
		select_all = args.get('select_all', False)  # 获取 select_all 参数
		query = SysFieldType.query
		field_type = args.get('field_type', None)
		desc = args.get('desc', None)
		if field_type:
			query = query.filter(SysFieldType.field_type.like(f"%{field_type}%"))
		if desc:
			query = query.filter(SysFieldType.desc.like(f"%{desc}%"))

		# 如果 select_all 为 True，则查询所有数据并直接返回 records
		if select_all:
			data = query.all()
			return Utils.query_to_dict_list(data)

		# 否则按分页查询
		data = query.paginate(page=page, per_page=per_page)
		records = Utils.query_to_dict_list(data.items)
		return {
			"total": data.total,
			"records": records,
			"pageNum": data.page,
			"pageSize": data.per_page
		}

	@staticmethod
	def save_field_type(args):
		"""
		sys_field_type 新增和修改
		"""
		id = args.get("id", 0)
		if id <= 0:
			new_entry = SysFieldType(**args)
			db.session.add(new_entry)
		else:
			entry_to_update = SysFieldType.query.get(id)
			if entry_to_update:
				for key, value in args.items():
					setattr(entry_to_update, key, value)
		db.session.commit()
		return True

	@staticmethod
	def delete_field_type(args):
		"""
		sys_field_type 删除
		"""
		id = args.get("id")
		entry = SysFieldType.query.get(id)
		if entry:
			db.session.delete(entry)
			db.session.commit()
			return True
		return False

	@staticmethod
	def index_list(args):
		table_id = args.get('table_id')
		indexes = SysTableIndex.query.filter_by(table_id=table_id).all()
		result = []
		for i in indexes:
			d = i.__dict__.copy()
			d.pop('_sa_instance_state', None)
			d.pop('is_unique', None)  # 移除唯一性字段
			result.append(d)
		return result

	@staticmethod
	def save_index(args):
		id = args.get('id', 0)
		table_id = args['table_id']
		index_name = args['index_name']
		index_fields = args['index_fields']
		index_type = args.get('index_type', 'INDEX')
		now = datetime.now()
		table = SysTable.query.filter(SysTable.id == table_id, SysTable.deleted == 0).first()
		if not table:
			abort(400, '表不存在')
		field_list = index_fields.split(',')
		field_str = ','.join([f'`{f.strip()}`' for f in field_list])
		if id <= 0:
			# 新建
			sql = f"ALTER TABLE `{table.name}` ADD {index_type} `{index_name}` ({field_str})"
			TableService._log_sql(sql)
			db.session.execute(text(sql))
			new_index = SysTableIndex(
				table_id=table_id, index_name=index_name, index_fields=index_fields, index_type=index_type, created=now, modified=now
			)
			db.session.add(new_index)
			db.session.flush()  # 获取新插入记录的 id
			# 记录 INSERT SQL
			insert_data = {
				'id': new_index.id,
				'table_id': table_id,
				'index_name': index_name,
				'index_fields': index_fields,
				'index_type': index_type,
				'created': now,
				'modified': now
			}
			TableService._log_orm_insert('sys_table_index', insert_data)
		else:
			# 编辑（先删后加）
			old = SysTableIndex.query.get(id)
			if old:
				sql = f"ALTER TABLE `{table.name}` DROP INDEX `{old.index_name}`"
				TableService._log_sql(sql)
				db.session.execute(text(sql))
				# 记录 DELETE SQL
				TableService._log_orm_delete('sys_table_index', f"id = {id}")
				db.session.delete(old)
			sql = f"ALTER TABLE `{table.name}` ADD {index_type} `{index_name}` ({field_str})"
			TableService._log_sql(sql)
			db.session.execute(text(sql))
			new_index = SysTableIndex(
				id=id, table_id=table_id, index_name=index_name, index_fields=index_fields,
				index_type=index_type, created=now, modified=now
			)
			db.session.add(new_index)
			# 记录 INSERT SQL（编辑时重新插入）
			insert_data = {
				'id': id,
				'table_id': table_id,
				'index_name': index_name,
				'index_fields': index_fields,
				'index_type': index_type,
				'created': now,
				'modified': now
			}
			TableService._log_orm_insert('sys_table_index', insert_data)
		db.session.commit()
		return True

	@staticmethod
	def delete_index(args):
		id = args['id']
		index = SysTableIndex.query.get(id)
		if not index:
			abort(400, '索引不存在')
		table = SysTable.query.filter(SysTable.id == index.table_id, SysTable.deleted == 0).first()
		if not table:
			abort(400, '表不存在')
		sql = f"ALTER TABLE `{table.name}` DROP INDEX `{index.index_name}`"
		TableService._log_sql(sql)
		db.session.execute(text(sql))
		# 记录 DELETE SQL
		TableService._log_orm_delete('sys_table_index', f"id = {id}")
		db.session.delete(index)
		db.session.commit()
		return True

	@staticmethod
	def delete_table(args):
		"""
		删除表信息
		"""
		table_id = args.get('id')
		deleted = args.get('deleted', 1)

		# 获取表信息（包括已删除的表）
		table = SysTable.query.filter(SysTable.id == table_id).first()
		if not table:
			abort(400, gettext("表不存在"))

		# 检查是否已经被删除
		if table.deleted == 1:
			abort(400, gettext("表已被删除"))
		# 删除表的时候保留 现有表字段和索引状态 以便后期恢复的时候使用
		# # 标记删除表中的所有字段记录
		# SysTableField.query.filter(SysTableField.table_id == table_id).update({"deleted": 1, "modified": datetime.now()})

		# # 标记删除索引记录
		# SysTableIndex.query.filter(SysTableIndex.table_id == table_id).update({"deleted": 1, "modified": datetime.now()})

		# 更新表状态为删除
		now_time = datetime.now()
		table.deleted = deleted
		table.modified = now_time
		# 记录 UPDATE SQL
		TableService._log_orm_update('sys_table', {"deleted": deleted, "modified": now_time}, f"id = {table_id}")
		db.session.commit()

		return True

	@staticmethod
	def restore_table(args):
		"""
		恢复表信息
		"""
		table_id = args.get('id')

		# 获取已删除的表信息
		table = SysTable.query.filter(SysTable.id == table_id, SysTable.deleted == 1).first()
		if not table:
			abort(400, gettext("表不存在或未被删除"))

		# 更新表状态
		now_time = datetime.now()
		table.deleted = 0
		table.modified = now_time
		# 记录 UPDATE SQL
		TableService._log_orm_update('sys_table', {"deleted": 0, "modified": now_time}, f"id = {table_id}")
		db.session.commit()

		return True

	@staticmethod
	def _async_create_models(app):
		"""
		异步创建模型文件，避免开发环境重启导致前端请求断开
		"""
		def create_models_task():
			try:
				# 延迟2秒确保当前请求完成
				time.sleep(2)

				# 直接调用 Sqlacodegen，不依赖 Flask 应用上下文
				TableService._generate_models_directly()

			except Exception as e:
				# 记录错误但不影响主流程
				pass

		# 在后台线程中执行模型生成
		thread = threading.Thread(target=create_models_task, daemon=True)
		thread.start()

	@staticmethod
	def _generate_models_directly():
		"""
		直接生成模型文件，不依赖 Flask 应用上下文
		"""
		import os
		import subprocess
		from sqlalchemy import create_engine, inspect

		# 从配置文件中读取数据库连接信息
		try:
			import sys
			sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
			from config.Config import Config
			config = Config()
			database_uri = config.SQLALCHEMY_DATABASE_URI
		except:
			# 如果读取配置失败，使用默认值
			database_uri = 'mysql+pymysql://fic_label:DBL3FPHjhA5BXMX2@47.108.89.8:9806/fic_label'

		try:
			# 获取有主键的表
			engine = create_engine(database_uri)
			inspector = inspect(engine)
			tables = []
			for table_name in inspector.get_table_names():
				primary_keys = inspector.get_pk_constraint(table_name)['constrained_columns']
				if primary_keys:
					tables.append(table_name)

			if not tables:
				return

			# 确保模型目录存在
			model_dir = 'model'
			if not os.path.exists(model_dir):
				os.makedirs(model_dir)

			model_path = os.path.join(model_dir, 'model.py')

			# 构造 sqlacodegen 命令
			command = [
				"flask-sqlacodegen",
				database_uri,
				"--outfile", model_path,
				"--tables", ",".join(tables),
				"--flask"
			]

			# 执行命令
			subprocess.run(command)

		except Exception as e:
			raise

	@staticmethod
	def query_table_data(args):
		"""
		查询表的所有数据
		"""
		table_id = args.get('table_id')
		page = args.get('pageNum', args.get('page', 1))
		per_page = args.get('pageSize', args.get('limit', 10))

		# 获取表信息
		table = SysTable.query.filter(SysTable.id == table_id, SysTable.deleted == 0).first()
		if not table:
			abort(400, gettext("表不存在"))

		table_name = table.name

		# 获取表的所有字段信息
		field_list = SysTableField.query.filter(SysTableField.table_id == table_id, SysTableField.deleted == 0).all()
		if not field_list:
			return {
				"total": 0,
				"records": [],
				"pageNum": page,
				"pageSize": per_page
			}

		# 构建字段名列表（包含id字段）
		field_names = ['id'] + [field.field_name for field in field_list]

		# 构建 SELECT 语句
		columns_str = ', '.join([f'`{name}`' for name in field_names])
		sql = f"SELECT {columns_str} FROM `{table_name}`"

		# 获取总数
		count_sql = f"SELECT COUNT(*) as total FROM `{table_name}`"
		count_result = db.session.execute(text(count_sql)).fetchone()
		total = count_result[0] if count_result else 0

		# 分页查询
		offset = (page - 1) * per_page
		sql += f" LIMIT {per_page} OFFSET {offset}"

		# 执行查询
		result = db.session.execute(text(sql))
		rows = result.fetchall()

		# 转换为字典列表
		records = []
		for row in rows:
			record = {}
			for i, field_name in enumerate(field_names):
				value = row[i]
				# 处理日期时间类型
				if isinstance(value, datetime):
					record[field_name] = value.strftime('%Y-%m-%d %H:%M:%S')
				else:
					record[field_name] = value
			records.append(record)

		return {
			"total": total,
			"records": records,
			"pageNum": page,
			"pageSize": per_page
		}
