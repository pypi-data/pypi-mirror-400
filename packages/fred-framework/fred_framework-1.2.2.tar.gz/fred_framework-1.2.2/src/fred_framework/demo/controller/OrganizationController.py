"""
 * @Author：Auto
 * @Package：OrganizationController
 * @Project：admin
 * @name：OrganizationController
 * @Date：2025/1/11
 * @Filename：OrganizationController
"""
from flask.views import MethodView
from flask_babelplus import gettext

from demo import demo
from demo.controller import admin_required
from demo.schema.OrganizationSchema import (
    CompanyListSchema, CompanySaveSchema, CompanyDeleteSchema, CompanyRecord,
    DepartmentListSchema, DepartmentSaveSchema, DepartmentDeleteSchema, DepartmentRecord,
    TeamListSchema, TeamSaveSchema, TeamDeleteSchema, TeamRecord,
    TeamMemberListSchema, TeamMemberSaveSchema, TeamMemberDeleteSchema, TeamMemberRecord, AvailableAdminRecord,
    TeamMemberManagerSchema
)
from demo.service.OrganizationService import OrganizationService
from fred_framework.common.PageSchema import PageSchemaFactory


# ==================== 公司相关接口 ====================
@demo.route("/organization/company")
class CompanyController(MethodView):
    """公司管理"""

    @admin_required
    @demo.arguments(CompanyListSchema, location='query')
    @demo.response(200, PageSchemaFactory(CompanyRecord))
    def get(self, args):
        """获取公司列表"""
        return OrganizationService().company_list(args)

    @admin_required
    @demo.arguments(CompanySaveSchema)
    @demo.response(200)
    def post(self, args):
        """新增公司"""
        OrganizationService().save_company(args)
        return gettext("保存成功")

    @admin_required
    @demo.arguments(CompanySaveSchema)
    @demo.response(200)
    def put(self, args):
        """编辑公司"""
        OrganizationService().save_company(args)
        return gettext("保存成功")

    @admin_required
    @demo.arguments(CompanyDeleteSchema, location='query')
    @demo.response(200)
    def delete(self, args):
        """删除公司"""
        OrganizationService().delete_company(args)
        return gettext("删除成功")


# ==================== 部门相关接口 ====================
@demo.route("/organization/department")
class DepartmentController(MethodView):
    """部门管理"""

    @admin_required
    @demo.arguments(DepartmentListSchema, location='query')
    @demo.response(200, PageSchemaFactory(DepartmentRecord))
    def get(self, args):
        """获取部门列表"""
        return OrganizationService().department_list(args)

    @admin_required
    @demo.arguments(DepartmentSaveSchema)
    @demo.response(200)
    def post(self, args):
        """新增部门"""
        OrganizationService().save_department(args)
        return gettext("保存成功")

    @admin_required
    @demo.arguments(DepartmentSaveSchema)
    @demo.response(200)
    def put(self, args):
        """编辑部门"""
        OrganizationService().save_department(args)
        return gettext("保存成功")

    @admin_required
    @demo.arguments(DepartmentDeleteSchema, location='query')
    @demo.response(200)
    def delete(self, args):
        """删除部门"""
        OrganizationService().delete_department(args)
        return gettext("删除成功")


# ==================== 团队相关接口 ====================
@demo.route("/organization/team")
class TeamController(MethodView):
    """团队管理"""

    @admin_required
    @demo.arguments(TeamListSchema, location='query')
    @demo.response(200, PageSchemaFactory(TeamRecord))
    def get(self, args):
        """获取团队列表"""
        return OrganizationService().team_list(args)

    @admin_required
    @demo.arguments(TeamSaveSchema)
    @demo.response(200)
    def post(self, args):
        """新增团队"""
        OrganizationService().save_team(args)
        return gettext("保存成功")

    @admin_required
    @demo.arguments(TeamSaveSchema)
    @demo.response(200)
    def put(self, args):
        """编辑团队"""
        OrganizationService().save_team(args)
        return gettext("保存成功")

    @admin_required
    @demo.arguments(TeamDeleteSchema, location='query')
    @demo.response(200)
    def delete(self, args):
        """删除团队"""
        OrganizationService().delete_team(args)
        return gettext("删除成功")


# ==================== 辅助接口 ====================
@demo.route("/organization/company/all")
class CompanyAllController(MethodView):
    """获取所有公司（用于下拉选择）"""

    @admin_required
    @demo.response(200, CompanyRecord(many=True))
    def get(self):
        """获取所有公司列表"""
        return OrganizationService().get_all_companies()


@demo.route("/organization/department/by-company")
class DepartmentByCompanyController(MethodView):
    """根据公司获取部门列表（用于下拉选择）"""

    @admin_required
    @demo.response(200, DepartmentRecord(many=True))
    def get(self):
        """根据公司ID获取部门列表"""
        from flask import request
        company_id = request.args.get('company_id')
        if not company_id:
            return []
        return OrganizationService().get_departments_by_company(int(company_id))


# ==================== 团队人员相关接口 ====================
@demo.route("/organization/team/member")
class TeamMemberController(MethodView):
    """团队人员管理"""

    @admin_required
    @demo.arguments(TeamMemberListSchema, location='query')
    @demo.response(200, PageSchemaFactory(TeamMemberRecord))
    def get(self, args):
        """获取团队人员列表"""
        return OrganizationService().team_member_list(args)

    @admin_required
    @demo.arguments(TeamMemberSaveSchema)
    @demo.response(200)
    def post(self, args):
        """添加团队人员"""
        OrganizationService().save_team_members(args)
        return gettext("添加成功")

    @admin_required
    @demo.arguments(TeamMemberDeleteSchema, location='query')
    @demo.response(200)
    def delete(self, args):
        """删除团队人员"""
        OrganizationService().delete_team_member(args)
        return gettext("删除成功")


@demo.route("/organization/team/available-admins")
class TeamAvailableAdminsController(MethodView):
    """获取可用的管理员列表（未加入团队的管理员）"""

    @admin_required
    @demo.response(200, AvailableAdminRecord(many=True))
    def get(self):
        """获取可用的管理员列表"""
        from flask import request
        team_id = request.args.get('team_id')
        if not team_id:
            return []
        return OrganizationService().get_available_admins(int(team_id))


@demo.route("/organization/team/member/manager")
class TeamMemberManagerController(MethodView):
    """设置团队管理员"""

    @admin_required
    @demo.arguments(TeamMemberManagerSchema)
    @demo.response(200)
    def put(self, args):
        """设置/取消团队管理员"""
        OrganizationService().update_team_member_manager(args)
        return gettext("操作成功")

