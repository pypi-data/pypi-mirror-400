/**
 * 角色相关数据模型
 */

/**
 * 角色信息
 */
export interface RoleInfo {
  id: number;
  name: string;
  description?: string;
  status: number;
  created: string;
  modified?: string;
  permissions?: string[];
}

/**
 * 角色列表查询参数
 */
export interface RoleListQuery {
  pageNum?: number;
  pageSize?: number;
  name?: string;
  status?: number;
}

/**
 * 角色保存参数
 */
export interface RoleSaveParams {
  id?: number;
  name: string;
  description?: string;
  status?: number;
  permissions?: string[];
}

/**
 * 角色删除参数
 */
export interface RoleDeleteParams {
  id: number[];
}

/**
 * 角色权限分配参数
 */
export interface RolePermissionParams {
  role_id: number;
  permission_ids: number[];
}

/**
 * 角色菜单分配参数
 */
export interface RoleMenuParams {
  role_id: number;
  menu_ids: number[];
}

/**
 * 角色用户分配参数
 */
export interface RoleUserParams {
  role_id: number;
  user_ids: number[];
}
