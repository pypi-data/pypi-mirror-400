"""
 * @Author：Auto
 * @Package：OrganizationSchema
 * @Project：admin
 * @name：OrganizationSchema
 * @Date：2025/1/11
 * @Filename：OrganizationSchema
"""
from marshmallow import fields, Schema

from fred_framework.common.PageSchema import PageSchema


# ==================== 公司相关Schema ====================
class CompanyListSchema(PageSchema):
    """公司列表查询参数"""
    name = fields.String(load_default=None, allow_none=True, metadata={'description': '公司名称，模糊查询'})


class CompanySaveSchema(Schema):
    """保存公司参数"""
    id = fields.Integer(load_default=None, metadata={'description': '公司ID，编辑时必传'})
    name = fields.String(required=True, validate=lambda x: len(x.strip()) > 0, metadata={'description': '公司名称'})


class CompanyDeleteSchema(Schema):
    """删除公司参数"""
    id = fields.Integer(required=True, metadata={'description': '公司ID'})


class CompanyRecord(Schema):
    """公司记录"""
    id = fields.Integer(metadata={'description': '公司ID'})
    name = fields.String(metadata={'description': '公司名称'})


# ==================== 部门相关Schema ====================
class DepartmentListSchema(PageSchema):
    """部门列表查询参数"""
    name = fields.String(load_default=None, allow_none=True, metadata={'description': '部门名称，模糊查询'})
    company_id = fields.Integer(load_default=None, allow_none=True, metadata={'description': '公司ID'})


class DepartmentSaveSchema(Schema):
    """保存部门参数"""
    id = fields.Integer(load_default=None, metadata={'description': '部门ID，编辑时必传'})
    name = fields.String(required=True, validate=lambda x: len(x.strip()) > 0, metadata={'description': '部门名称'})
    company_id = fields.Integer(required=True, metadata={'description': '所属公司ID'})


class DepartmentDeleteSchema(Schema):
    """删除部门参数"""
    id = fields.Integer(required=True, metadata={'description': '部门ID'})


class DepartmentRecord(Schema):
    """部门记录"""
    id = fields.Integer(metadata={'description': '部门ID'})
    name = fields.String(metadata={'description': '部门名称'})
    company_id = fields.Integer(metadata={'description': '所属公司ID'})
    company_name = fields.String(metadata={'description': '公司名称'})


# ==================== 团队相关Schema ====================
class TeamListSchema(PageSchema):
    """团队列表查询参数"""
    name = fields.String(load_default=None, allow_none=True, metadata={'description': '团队名称，模糊查询'})
    department_id = fields.Integer(load_default=None, allow_none=True, metadata={'description': '部门ID'})
    company_id = fields.Integer(load_default=None, allow_none=True, metadata={'description': '公司ID'})


class TeamSaveSchema(Schema):
    """保存团队参数"""
    id = fields.Integer(load_default=None, metadata={'description': '团队ID，编辑时必传'})
    name = fields.String(required=True, validate=lambda x: len(x.strip()) > 0, metadata={'description': '团队名称'})
    department_id = fields.Integer(required=True, metadata={'description': '所属部门ID'})


class TeamDeleteSchema(Schema):
    """删除团队参数"""
    id = fields.Integer(required=True, metadata={'description': '团队ID'})


class TeamRecord(Schema):
    """团队记录"""
    id = fields.Integer(metadata={'description': '团队ID'})
    name = fields.String(metadata={'description': '团队名称'})
    department_id = fields.Integer(metadata={'description': '所属部门ID'})
    department_name = fields.String(metadata={'description': '部门名称'})
    company_id = fields.Integer(metadata={'description': '所属公司ID'})
    company_name = fields.String(metadata={'description': '公司名称'})


# ==================== 团队人员相关Schema ====================
class TeamMemberListSchema(PageSchema):
    """团队人员列表查询参数"""
    team_id = fields.Integer(required=True, metadata={'description': '团队ID'})


class TeamMemberSaveSchema(Schema):
    """保存团队人员参数"""
    team_id = fields.Integer(required=True, metadata={'description': '团队ID'})
    admin_ids = fields.List(fields.Integer(), required=True, validate=lambda x: len(x) > 0, metadata={'description': '管理员ID列表'})


class TeamMemberDeleteSchema(Schema):
    """删除团队人员参数"""
    team_id = fields.Integer(required=True, metadata={'description': '团队ID'})
    admin_id = fields.Integer(required=True, metadata={'description': '管理员ID'})


class TeamMemberRecord(Schema):
    """团队人员记录"""
    id = fields.Integer(metadata={'description': '关联ID'})
    team_id = fields.Integer(metadata={'description': '团队ID'})
    admin_id = fields.Integer(metadata={'description': '管理员ID'})
    username = fields.String(metadata={'description': '用户名'})
    avatar = fields.String(metadata={'description': '头像'})
    is_manager = fields.Integer(metadata={'description': '是否管理员'})


class AvailableAdminRecord(Schema):
    """可用管理员记录（未加入团队的管理员）"""
    id = fields.Integer(metadata={'description': '管理员ID'})
    username = fields.String(metadata={'description': '用户名'})
    avatar = fields.String(metadata={'description': '头像'})


class TeamMemberManagerSchema(Schema):
    """设置团队管理员参数"""
    team_id = fields.Integer(required=True, metadata={'description': '团队ID'})
    admin_id = fields.Integer(required=True, metadata={'description': '管理员ID'})
    is_manager = fields.Integer(required=True, validate=lambda x: x in [0, 1, 2, 3], metadata={'description': '管理员类型：0-普通成员，1-公司管理员，2-部门管理，3-团队管理'})

