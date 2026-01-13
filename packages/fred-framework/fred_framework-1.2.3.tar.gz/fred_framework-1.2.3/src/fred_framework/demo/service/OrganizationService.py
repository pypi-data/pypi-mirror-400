"""
 * @Author：Auto
 * @Package：OrganizationService
 * @Project：admin
 * @name：OrganizationService
 * @Date：2025/1/11
 * @Filename：OrganizationService
"""
from flask import abort
from flask_babelplus import gettext

from fred_framework.common.Utils import Utils
from model.model import Company, Department, Team, TeamAdminRelation, Admin, db


class OrganizationService:
    """组织结构管理服务类"""

    # ==================== 公司相关方法 ====================
    def company_list(self, args):
        """获取公司列表"""
        page = args.get('pageNum', 1)
        per_page = args.get('pageSize', 10)
        name = args.get('name')

        query = Company.query

        if name:
            query = query.filter(Company.name.like(f"%{name}%"))

        data = query.order_by(Company.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        records = Utils.query_to_dict_list(data.items)

        result = {
            "total": data.total,
            "records": records,
            "pageNum": data.page,
            "pageSize": data.per_page
        }

        return result

    def save_company(self, args):
        """保存公司（新增/编辑）"""
        company_id = args.get('id')
        name = args.get('name', '').strip()

        if not name:
            abort(500, gettext('公司名称不能为空'))

        if company_id:
            # 编辑
            company = Company.query.filter_by(id=company_id).first()
            if not company:
                abort(500, gettext('公司不存在'))

            # 检查名称是否重复（排除自己）
            existing = Company.query.filter(Company.name == name, Company.id != company_id).first()
            if existing:
                abort(500, gettext('公司名称已存在'))

            company.name = name
            db.session.commit()
            return company_id
        else:
            # 新增
            existing = Company.query.filter_by(name=name).first()
            if existing:
                abort(500, gettext('公司名称已存在'))

            company = Company(name=name)
            db.session.add(company)
            db.session.commit()
            return company.id

    def delete_company(self, args):
        """删除公司"""
        company_id = args.get('id')
        company = Company.query.filter_by(id=company_id).first()

        if not company:
            abort(500, gettext('公司不存在'))

        # 检查是否有部门关联
        departments = Department.query.filter_by(company_id=company_id).first()
        if departments:
            abort(500, gettext('该公司下存在部门，无法删除'))

        db.session.delete(company)
        db.session.commit()
        return True

    # ==================== 部门相关方法 ====================
    def department_list(self, args):
        """获取部门列表"""
        page = args.get('pageNum', 1)
        per_page = args.get('pageSize', 10)
        name = args.get('name')
        company_id = args.get('company_id')

        query = Department.query

        if name:
            query = query.filter(Department.name.like(f"%{name}%"))

        if company_id:
            query = query.filter(Department.company_id == company_id)

        data = query.order_by(Department.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        records = Utils.query_to_dict_list(data.items)

        # 关联查询公司名称
        for record in records:
            company_id = record.get('company_id')
            if company_id is not None and company_id != 0:
                company = Company.query.filter_by(id=company_id).first()
                record['company_name'] = company.name if company else ''
            else:
                record['company_name'] = ''

        result = {
            "total": data.total,
            "records": records,
            "pageNum": data.page,
            "pageSize": data.per_page
        }

        return result

    def save_department(self, args):
        """保存部门（新增/编辑）"""
        department_id = args.get('id')
        name = args.get('name', '').strip()
        company_id = args.get('company_id')

        if not name:
            abort(500, gettext('部门名称不能为空'))

        if not company_id:
            abort(500, gettext('请选择所属公司'))

        # 验证公司是否存在
        company = Company.query.filter_by(id=company_id).first()
        if not company:
            abort(500, gettext('所选公司不存在'))

        if department_id:
            # 编辑
            department = Department.query.filter_by(id=department_id).first()
            if not department:
                abort(500, gettext('部门不存在'))

            # 检查名称是否重复（同一公司下，排除自己）
            existing = Department.query.filter(
                Department.name == name,
                Department.company_id == company_id,
                Department.id != department_id
            ).first()
            if existing:
                abort(500, gettext('该部门名称已存在'))

            department.name = name
            department.company_id = company_id
            db.session.commit()
            return department_id
        else:
            # 新增
            existing = Department.query.filter_by(name=name, company_id=company_id).first()
            if existing:
                abort(500, gettext('该部门名称已存在'))

            department = Department(name=name, company_id=company_id)
            db.session.add(department)
            db.session.commit()
            return department.id

    def delete_department(self, args):
        """删除部门"""
        department_id = args.get('id')
        department = Department.query.filter_by(id=department_id).first()

        if not department:
            abort(500, gettext('部门不存在'))

        # 检查是否有团队关联
        teams = Team.query.filter_by(department_id=department_id).first()
        if teams:
            abort(500, gettext('该部门下存在团队，无法删除'))

        db.session.delete(department)
        db.session.commit()
        return True

    # ==================== 团队相关方法 ====================
    def team_list(self, args):
        """获取团队列表"""
        page = args.get('pageNum', 1)
        per_page = args.get('pageSize', 10)
        name = args.get('name')
        department_id = args.get('department_id')
        company_id = args.get('company_id')

        query = Team.query

        if name:
            query = query.filter(Team.name.like(f"%{name}%"))

        if department_id:
            query = query.filter(Team.department_id == department_id)

        if company_id:
            # 通过部门关联查询公司
            department_ids = db.session.query(Department.id).filter(
                Department.company_id == company_id
            ).all()
            dept_id_list = [d[0] for d in department_ids]
            if dept_id_list:
                query = query.filter(Team.department_id.in_(dept_id_list))
            else:
                # 如果没有部门，返回空结果
                return {
                    "total": 0,
                    "records": [],
                    "pageNum": page,
                    "pageSize": per_page
                }

        data = query.order_by(Team.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        records = Utils.query_to_dict_list(data.items)

        # 关联查询部门名称和公司名称
        for record in records:
            department_id = record.get('department_id')
            if department_id is not None and department_id != 0:
                department = Department.query.filter_by(id=department_id).first()
                if department:
                    record['department_name'] = department.name
                    company_id = department.company_id
                    if company_id is not None and company_id != 0:
                        company = Company.query.filter_by(id=company_id).first()
                        if company:
                            record['company_id'] = company.id
                            record['company_name'] = company.name
                        else:
                            record['company_id'] = None
                            record['company_name'] = ''
                    else:
                        record['company_id'] = None
                        record['company_name'] = ''
                else:
                    record['department_name'] = ''
                    record['company_id'] = None
                    record['company_name'] = ''
            else:
                record['department_name'] = ''
                record['company_id'] = None
                record['company_name'] = ''

        result = {
            "total": data.total,
            "records": records,
            "pageNum": data.page,
            "pageSize": data.per_page
        }

        return result

    def save_team(self, args):
        """保存团队（新增/编辑）"""
        team_id = args.get('id')
        name = args.get('name', '').strip()
        department_id = args.get('department_id')

        if not name:
            abort(500, gettext('团队名称不能为空'))

        if not department_id:
            abort(500, gettext('请选择所属部门'))

        # 验证部门是否存在
        department = Department.query.filter_by(id=department_id).first()
        if not department:
            abort(500, gettext('所选部门不存在'))

        if team_id:
            # 编辑
            team = Team.query.filter_by(id=team_id).first()
            if not team:
                abort(500, gettext('团队不存在'))

            # 检查名称是否重复（同一部门下，排除自己）
            existing = Team.query.filter(
                Team.name == name,
                Team.department_id == department_id,
                Team.id != team_id
            ).first()
            if existing:
                abort(500, gettext('该团队名称已存在'))

            team.name = name
            team.department_id = department_id
            db.session.commit()
            return team_id
        else:
            # 新增
            existing = Team.query.filter_by(name=name, department_id=department_id).first()
            if existing:
                abort(500, gettext('该团队名称已存在'))

            team = Team(name=name, department_id=department_id)
            db.session.add(team)
            db.session.commit()
            return team.id

    def delete_team(self, args):
        """删除团队"""
        team_id = args.get('id')
        team = Team.query.filter_by(id=team_id).first()

        if not team:
            abort(500, gettext('团队不存在'))

        db.session.delete(team)
        db.session.commit()
        return True

    # ==================== 辅助方法 ====================
    def get_all_companies(self):
        """获取所有公司（用于下拉选择）"""
        companies = Company.query.order_by(Company.id.asc()).all()
        return Utils.query_to_dict_list(companies)

    def get_departments_by_company(self, company_id):
        """根据公司ID获取部门列表（用于下拉选择）"""
        departments = Department.query.filter_by(company_id=company_id).order_by(Department.id.asc()).all()
        return Utils.query_to_dict_list(departments)

    # ==================== 团队人员相关方法 ====================
    def team_member_list(self, args):
        """获取团队人员列表"""
        team_id = args.get('team_id')
        page = args.get('pageNum', 1)
        per_page = args.get('pageSize', 10)

        query = TeamAdminRelation.query.filter_by(team_id=team_id)

        data = query.order_by(TeamAdminRelation.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        records = Utils.query_to_dict_list(data.items)

        # 关联查询管理员信息
        for record in records:
            admin = Admin.query.filter_by(id=record['admin_id']).first()
            if admin:
                record['username'] = admin.username
                record['avatar'] = admin.avatar if hasattr(admin, 'avatar') else ''
            else:
                record['username'] = ''
                record['avatar'] = ''

        result = {
            "total": data.total,
            "records": records,
            "pageNum": data.page,
            "pageSize": data.per_page
        }

        return result

    def save_team_members(self, args):
        """保存团队人员（批量添加）"""
        team_id = args.get('team_id')
        admin_ids = args.get('admin_ids', [])

        if not team_id:
            abort(500, gettext('团队ID不能为空'))

        if not admin_ids:
            abort(500, gettext('请选择要添加的管理员'))

        # 验证团队是否存在
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            abort(500, gettext('团队不存在'))

        # 验证管理员是否存在
        admins = Admin.query.filter(Admin.id.in_(admin_ids), Admin.deleted == 0).all()
        if len(admins) != len(admin_ids):
            abort(500, gettext('部分管理员不存在或已被删除'))

        # 检查是否已经存在关系
        existing_relations = TeamAdminRelation.query.filter(
            TeamAdminRelation.team_id == team_id,
            TeamAdminRelation.admin_id.in_(admin_ids)
        ).all()
        existing_admin_ids = [rel.admin_id for rel in existing_relations]

        # 只添加不存在的关联
        new_admin_ids = [aid for aid in admin_ids if aid not in existing_admin_ids]

        if not new_admin_ids:
            abort(500, gettext('所选管理员已在该团队中'))

        # 批量添加关联
        for admin_id in new_admin_ids:
            relation = TeamAdminRelation(team_id=team_id, admin_id=admin_id, is_manager=0)
            db.session.add(relation)

        db.session.commit()
        return True

    def delete_team_member(self, args):
        """删除团队人员"""
        team_id = args.get('team_id')
        admin_id = args.get('admin_id')

        relation = TeamAdminRelation.query.filter_by(team_id=team_id, admin_id=admin_id).first()

        if not relation:
            abort(500, gettext('关联关系不存在'))

        db.session.delete(relation)
        db.session.commit()
        return True

    def get_available_admins(self, team_id):
        """获取可用的管理员列表（未加入该团队的管理员）"""
        # 获取已加入团队的管理员ID
        existing_relations = TeamAdminRelation.query.filter_by(team_id=team_id).all()
        existing_admin_ids = [rel.admin_id for rel in existing_relations]

        # 查询未加入团队的管理员
        query = Admin.query.filter(Admin.deleted == 0)
        if existing_admin_ids:
            query = query.filter(~Admin.id.in_(existing_admin_ids))

        admins = query.order_by(Admin.id.asc()).all()
        return Utils.query_to_dict_list(admins)

    def update_team_member_manager(self, args):
        """更新团队人员的管理员状态"""
        team_id = args.get('team_id')
        admin_id = args.get('admin_id')
        is_manager = args.get('is_manager')

        relation = TeamAdminRelation.query.filter_by(team_id=team_id, admin_id=admin_id).first()

        if not relation:
            abort(500, gettext('关联关系不存在'))

        relation.is_manager = is_manager
        db.session.commit()
        return True

