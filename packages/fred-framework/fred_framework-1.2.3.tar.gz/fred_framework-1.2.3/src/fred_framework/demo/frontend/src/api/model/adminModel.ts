/**
 * 管理员相关数据模型
 */

/**
 * 管理员账户信息
 */
export interface AdminAccount {
  id: string;
  username: string;
  phone: string;
  lastLogin: string;
  status: number;
  avatar: string;
  forbidden: boolean;
  roleName: string;
  role_ids?: number[];
  created: string;
  children?: AdminAccount[];
}

/**
 * 管理员列表查询参数
 */
export interface AdminListQuery {
  pageNum: number;
  pageSize: number;
  username?: string;
  gender?: number;
  idCard?: string;
  email?: string;
  address?: string;
  createTime?: string[];
  status?: number;
}

/**
 * 管理员保存参数
 */
export interface AdminSaveParams {
  id?: string;
  username: string;
  password?: string;
  phone?: string;
  email?: string;
  avatar?: string;
  role_ids?: number[];
  status?: number;
}

/**
 * 管理员状态字典
 */
export interface AdminStatus {
  userLabel: string;
  userValue: number;
}

/**
 * 用户部门信息
 */
export interface UserDepartment {
  id: string;
  name: string;
  children?: UserDepartment[];
}

/**
 * 用户角色信息
 */
export interface UserRole {
  id: string;
  path: string;
  name: string;
  children?: UserRole[];
}

/**
 * 用户信息
 */
export interface UserInfo {
  id: number;
  username: string;
  phone: number;
  user: { detail: { age: number } };
  createTime: string;
  status: number;
  avatar: string;
  forbidden: boolean;
  roleName?: string;
  role_ids?: number[];
  children?: UserInfo[];
}

/**
 * 用户查询参数
 */
export interface UserQueryParams {
  pageNum: number;
  pageSize: number;
  username: string;
  createTime: string[];
  status: number;
}

/**
 * 密码更新参数
 */
export interface PasswordUpdateParams {
  oldPassword: string;
  newPassword: string;
  repPassword: string;
}

/**
 * 用户状态更新参数
 */
export interface UserStatusUpdateParams {
  id: string;
  status: number;
}

/**
 * 用户删除参数
 */
export interface UserDeleteParams {
  id: string[];
}

/**
 * 密码重置参数
 */
export interface PasswordResetParams {
  id: string;
}
