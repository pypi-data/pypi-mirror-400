import { ResPage } from "@/api/interface/index";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";
import type {
  AdminAccount,
  AdminListQuery,
  AdminSaveParams,
  AdminStatus,
  UserDepartment,
  UserRole,
  UserInfo,
  UserQueryParams,
  PasswordUpdateParams,
  UserStatusUpdateParams,
  UserDeleteParams,
  PasswordResetParams
} from "@/api/model/adminModel";

/**
 * @name 用户管理模块
 */

// 获取管理员账户列表
export const getAccountList = (params: AdminListQuery) => {
  return http.get<ResPage<AdminAccount>>(PORT1 + `/admin_list`, params);
};

// 获取树形用户列表
export const getUserTreeList = (params: UserQueryParams) => {
  return http.post<ResPage<UserInfo>>(PORT1 + `/user/tree/list`, params);
};

// 新增用户
export const addUser = (params: AdminSaveParams) => {
  return http.post(PORT1 + `/admin_save`, params);
};

// 编辑用户
export const editUser = (params: AdminSaveParams) => {
  return http.put(PORT1 + `/admin_save`, params);
};

// 删除用户
export const deleteUser = (params: UserDeleteParams) => {
  return http.delete(PORT1 + `/admin_delete`, params);
};

// 切换用户状态
export const changeUserStatus = (params: UserStatusUpdateParams) => {
  return http.put(PORT1 + `/admin_forbidden`, params);
};

// 重置用户密码
export const resetUserPassWord = (params: PasswordResetParams) => {
  return http.put(PORT1 + `/reset_password`, params);
};

// 获取用户状态字典
export const getUserStatus = () => {
  return http.get<AdminStatus[]>(PORT1 + `/admin_status`);
};

// 获取用户部门列表
export const getUserDepartment = () => {
  return http.get<UserDepartment[]>(PORT1 + `/user/department`, {}, { cancel: false });
};

// 获取用户角色字典
export const getUserRole = () => {
  return http.get<UserRole[]>(PORT1 + `/user/role`);
};

// 更新密码
export const updatePassword = (params: PasswordUpdateParams) => {
  return http.put(PORT1 + `/update_self_password`, params);
};
