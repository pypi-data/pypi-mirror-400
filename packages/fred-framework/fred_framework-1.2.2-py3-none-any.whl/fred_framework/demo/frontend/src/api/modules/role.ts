import { ResPage } from "@/api/interface/index";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";
import type {
  RoleInfo,
  RoleListQuery,
  RoleSaveParams,
  RoleDeleteParams,
  RolePermissionParams,
  RoleMenuParams,
  RoleUserParams
} from "@/api/model/roleModel";

/**
 * @name 角色管理模块
 */

// 获取角色列表
export const getRoleList = (params?: RoleListQuery) => {
  return http.get<ResPage<RoleInfo>>(PORT1 + `/system/role`, params);
};

// 获取所有角色列表（用于下拉选择）
export const getAllRoleList = () => {
  return http.get<RoleInfo[]>(PORT1 + `/system/role/all`);
};

// 获取用户角色列表
export const getUserRoles = (params: { userId: number }) => {
  return http.get<RoleInfo[]>(PORT1 + `/system/role/user`, params);
};

// 设置用户角色
export const setUserRoles = (params: RoleUserParams) => {
  return http.post(PORT1 + `/admin_set_role`, params);
};

// 创建角色
export const createRole = (params: RoleSaveParams) => {
  return http.post(PORT1 + `/system/role`, params);
};

// 更新角色
export const updateRole = (params: RoleSaveParams) => {
  return http.put(PORT1 + `/system/role`, params);
};

// 删除角色
export const deleteRole = (params: RoleDeleteParams) => {
  return http.delete(PORT1 + `/system/role`, params);
};

// 分配角色权限
export const assignRolePermissions = (params: RolePermissionParams) => {
  return http.post(PORT1 + `/system/role/permissions`, params);
};

// 分配角色菜单
export const assignRoleMenus = (params: RoleMenuParams) => {
  return http.post(PORT1 + `/system/role/menus`, params);
};
