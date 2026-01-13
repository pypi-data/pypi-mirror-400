import { ResPage } from "@/api/interface";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";

/**
 * 组织结构管理相关接口
 */

// ==================== 公司相关接口 ====================
export interface CompanyInfo {
  id?: number;
  name: string;
}

export const getCompanyList = (params?: any) => {
  return http.get<ResPage<CompanyInfo>>(PORT1 + `/organization/company`, params || {});
};

export const addCompany = (params: CompanyInfo) => {
  return http.post(PORT1 + `/organization/company`, params);
};

export const editCompany = (params: CompanyInfo) => {
  return http.put(PORT1 + `/organization/company`, params);
};

export const deleteCompany = (params: { id: number }) => {
  return http.delete(PORT1 + `/organization/company`, params);
};

export const getAllCompanies = () => {
  return http.get<CompanyInfo[]>(PORT1 + `/organization/company/all`);
};

// ==================== 部门相关接口 ====================
export interface DepartmentInfo {
  id?: number;
  name: string;
  company_id?: number;
  company_name?: string;
}

export const getDepartmentList = (params?: any) => {
  return http.get<ResPage<DepartmentInfo>>(PORT1 + `/organization/department`, params || {});
};

export const addDepartment = (params: DepartmentInfo) => {
  return http.post(PORT1 + `/organization/department`, params);
};

export const editDepartment = (params: DepartmentInfo) => {
  return http.put(PORT1 + `/organization/department`, params);
};

export const deleteDepartment = (params: { id: number }) => {
  return http.delete(PORT1 + `/organization/department`, params);
};

export const getDepartmentsByCompany = (params: { company_id: number }) => {
  return http.get<DepartmentInfo[]>(PORT1 + `/organization/department/by-company`, params);
};

// ==================== 团队相关接口 ====================
export interface TeamInfo {
  id?: number;
  name: string;
  department_id?: number;
  department_name?: string;
  company_id?: number;
  company_name?: string;
}

export const getTeamList = (params?: any) => {
  return http.get<ResPage<TeamInfo>>(PORT1 + `/organization/team`, params || {});
};

export const addTeam = (params: TeamInfo) => {
  return http.post(PORT1 + `/organization/team`, params);
};

export const editTeam = (params: TeamInfo) => {
  return http.put(PORT1 + `/organization/team`, params);
};

export const deleteTeam = (params: { id: number }) => {
  return http.delete(PORT1 + `/organization/team`, params);
};

// ==================== 团队人员相关接口 ====================
export interface TeamMemberInfo {
  id?: number;
  team_id: number;
  admin_id: number;
  username?: string;
  avatar?: string;
  is_manager?: number;
}

export interface AvailableAdminInfo {
  id: number;
  username: string;
  avatar?: string;
}

export const getTeamMemberList = (params: { team_id: number; pageNum?: number; pageSize?: number }) => {
  return http.get<ResPage<TeamMemberInfo>>(PORT1 + `/organization/team/member`, params);
};

export const addTeamMembers = (params: { team_id: number; admin_ids: number[] }) => {
  return http.post(PORT1 + `/organization/team/member`, params);
};

export const deleteTeamMember = (params: { team_id: number; admin_id: number }) => {
  return http.delete(PORT1 + `/organization/team/member`, params);
};

export const getAvailableAdmins = (params: { team_id: number }) => {
  return http.get<AvailableAdminInfo[]>(PORT1 + `/organization/team/available-admins`, params);
};

export const updateTeamMemberManager = (params: { team_id: number; admin_id: number; is_manager: number }) => {
  return http.put(PORT1 + `/organization/team/member/manager`, params);
};
