# coding: utf-8
"""
 * @Author：Qoder
 * @Package：SystemLogService
 * @Project：admin
 * @name：SystemLogService
 * @Date：2025/12/1
 * @Filename：SystemLogService
"""
from flask import abort
from flask_babelplus import gettext

from fred_framework.common.Utils import Utils
from model.model import db, SysLog, SysLogBody


class SystemLogService:
    """系统日志服务类"""

    def get_system_logs(self, args):
        """
        获取系统日志列表
        :param args: 查询参数
        :return: 日志列表
        """
        try:
            # 获取分页参数
            page = args.get('pageNum', 1)
            per_page = args.get('pageSize', 10)

            # 获取查询参数
            username = args.get('username', '').strip()
            api = args.get('api', '').strip()
            method = args.get('method', '').strip()
            code = args.get('code')
            start_date = args.get('start_date', '').strip()
            end_date = args.get('end_date', '').strip()

            # 构建查询
            query = SysLog.query

            # 添加筛选条件
            if username:
                query = query.filter(SysLog.username.like(f"%{username}%"))

            if api:
                query = query.filter(SysLog.api.like(f"%{api}%"))

            if method:
                query = query.filter(SysLog.method == method)

            if code is not None:
                query = query.filter(SysLog.code == code)

            if start_date:
                query = query.filter(SysLog.created >= start_date)

            if end_date:
                # 结束日期加一天，确保包含当天的数据
                from datetime import datetime, timedelta
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                query = query.filter(SysLog.created < end_datetime)

            # 分页查询
            pagination = query.order_by(SysLog.id.desc()).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            # 格式化返回数据
            records = Utils.query_to_dict_list(pagination.items)

            # 确保records是列表
            if not isinstance(records, list):
                records = []

            # 获取所有接口说明信息（只获取一次，提高性能）
            api_list = Utils.get_api_urls_from_files()

            # 为每条日志添加接口说明
            for record in records:
                api_url = record.get('api', '')
                api_method = record.get('method', '')
                if api_url and api_method:
                    api_summary = Utils.get_api_summary_by_url_and_method(api_url, api_method, api_list)
                    record['api_summary'] = api_summary if api_summary else ''
                else:
                    record['api_summary'] = ''

            result = {
                'records': records,
                'total': pagination.total,
                'page': page,
                'limit': per_page
            }

            return result

        except Exception as e:
            abort(500, gettext(f"获取系统日志失败: {str(e)}"))

    def delete_system_logs(self, ids):
        """
        删除系统日志
        :param ids: 日志ID列表
        :return: 删除结果
        """
        try:
            # 删除指定ID的日志
            SysLog.query.filter(SysLog.id.in_(ids)).delete(synchronize_session=False)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            abort(500, gettext(f"删除系统日志失败: {str(e)}"))

    def get_system_log_detail(self, log_id):
        """
        获取系统日志详情
        :param log_id: 日志ID
        :return: 日志详情
        """

        # 获取日志基本信息
        log = SysLog.query.filter_by(id=log_id).first()
        if not log:
            abort(404, gettext("日志不存在"))

        # 转换为字典
        record = Utils.query_to_dict(log)

        # 获取对应的sys_log_body数据
        log_body = SysLogBody.query.filter_by(sys_log_id=log_id).first()
        if log_body:
            record['request'] = log_body.request
            record['response'] = log_body.response
        else:
            record['request'] = None
            record['response'] = None

        return record
