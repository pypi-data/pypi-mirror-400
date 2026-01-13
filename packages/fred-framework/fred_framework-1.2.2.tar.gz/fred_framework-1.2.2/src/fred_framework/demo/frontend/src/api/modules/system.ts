import { ResPage } from "@/api/interface";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";
import type {
  MenuInfo,
  MenuNode,
  RoleInfo,
  SystemConfig,
  SystemConfigQuery,
  SystemConfigSaveParams,
  SystemConfigDeleteParams,
  SystemLog,
  SystemLogQuery,
  SystemLogDeleteParams,
  SystemStatus,
  SystemHealthCheck
} from "@/api/model/systemModel";

/**
 * 系统管理相关接口
 */

// 菜单管理
export const getMenu = (params?: any) => {
  return http.get<ResPage<MenuInfo>>(PORT1 + `/system/menu`, params || {});
};

export const addMenu = (params: MenuInfo) => {
  return http.post(PORT1 + `/system/menu`, params);
};

export const editMenu = (params: MenuInfo) => {
  return http.put(PORT1 + `/system/menu`, params);
};

export const deleteMenu = (params: { id: string }) => {
  return http.delete(PORT1 + `/system/menu`, params);
};

export const restoreMenu = (params: { id: string }) => {
  return http.patch(PORT1 + `/system/menu`, params);
};

// 角色管理模块
export const getRoleList = (params?: any) => {
  return http.get<ResPage<RoleInfo>>(PORT1 + `/system/role`, params || {});
};

export const addRole = (params: RoleInfo) => {
  return http.post(PORT1 + `/system/role`, params);
};

export const editRole = (params: RoleInfo) => {
  return http.put(PORT1 + `/system/role`, params);
};

export const deleteRole = (params: { id: number[] }) => {
  return http.delete(PORT1 + `/system/role`, params);
};

export const getRoleUserList = (params?: any) => {
  return http.get<RoleInfo[]>(PORT1 + `/system/role/users`, params || {});
};

export const removeRoleUser = (params: { userIds: number[]; roleId: number }) => {
  return http.delete(PORT1 + `/system/role/users`, params);
};

// 角色菜单权限管理
export const getRoleMenus = (params: { roleId: number }) => {
  return http.get<MenuInfo[]>(PORT1 + `/system/role/menu`, params);
};

export const setRoleMenuPermissions = (params: { roleId: number; menuIds: number[] }) => {
  return http.post(PORT1 + `/system/role/menu`, params);
};

// 角色按钮权限管理
export const getRoleButtons = (params: { roleId: number }) => {
  return http.get<MenuNode[]>(PORT1 + `/system/role/button`, params);
};

export const setRoleButtonPermissions = (params: { roleId: number; buttonIds: number[] }) => {
  return http.post(PORT1 + `/system/role/button`, params);
};

// 系统配置管理
export const getSystemConfig = (params?: SystemConfigQuery) => {
  return http.get<ResPage<SystemConfig>>(PORT1 + `/system/config`, params);
};

export const saveSystemConfig = (params: SystemConfigSaveParams) => {
  return http.post(PORT1 + `/system/config`, params);
};

export const updateSystemConfig = (params: SystemConfigSaveParams) => {
  return http.put(PORT1 + `/system/config`, params);
};

export const deleteSystemConfig = (params: SystemConfigDeleteParams) => {
  return http.delete(PORT1 + `/system/config`, params);
};

// 系统日志管理
export const getSystemLog = (params?: SystemLogQuery) => {
  return http.get<ResPage<SystemLog>>(PORT1 + `/system/log`, params);
};

export const getSystemLogDetail = (params: { id: number }) => {
  return http.get<SystemLog>(PORT1 + `/system/log/detail`, params);
};

export const deleteSystemLog = (params: SystemLogDeleteParams) => {
  return http.delete(PORT1 + `/system/log`, params);
};

// 系统状态监控
export const getSystemStatus = () => {
  return http.get<SystemStatus>(PORT1 + `/system/status`);
};

// 系统健康检查
export const getSystemHealthCheck = () => {
  return http.get<SystemHealthCheck>(PORT1 + `/system/health`);
};
