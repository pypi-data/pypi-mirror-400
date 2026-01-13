import { ResPage } from "@/api/interface/index";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";

/**
 * @name 按钮管理模块
 */

// 菜单信息接口
export interface MenuInfo {
  id: number;
  name: string;
  children?: MenuInfo[];
  level?: number; // 菜单层级
}

// API信息接口
export interface ApiInfo {
  id?: number;
  api_url: string;
  method: string;
  api_key?: string; // 用于前端选择的唯一标识
}

// 按钮信息接口
export interface ButtonInfo {
  id: number;
  button_name: string;
  menu_id: number;
  menu_name: string;
  explain?: string;
  api_list?: ApiInfo[];
  // 保持向后兼容
  api_url?: string;
  created?: string;
  modified?: string;
}

// 按钮列表查询参数
export interface ButtonListParams {
  pageNum?: number;
  pageSize?: number;
  menu_id?: number;
  button_name?: string;
}

// 保存按钮参数
export interface ButtonSaveParams {
  button_name: string;
  menu_id: number;
  explain?: string;
  api_list?: ApiInfo[];
  // 保持向后兼容
  api_url?: string;
}

/**
 * @description 获取菜单列表
 * @param {Object} params 查询参数
 * @returns {Promise}
 */
export const getMenuListApi = (params?: any) => {
  return http.get<MenuInfo[]>(PORT1 + "/button/manage/menu", params);
};

/**
 * @description 获取按钮列表
 * @param {Object} params 查询参数
 * @returns {Promise}
 */
export const getButtonListApi = (params?: ButtonListParams) => {
  return http.get<ResPage<ButtonInfo>>(PORT1 + "/button/manage", params);
};

/**
 * @description 新增按钮
 * @param {Object} data 按钮数据
 * @returns {Promise}
 */
export const addButtonApi = (data: ButtonSaveParams) => {
  return http.post(PORT1 + "/button/manage", data);
};

/**
 * @description 更新按钮
 * @param {Object} data 按钮数据
 * @returns {Promise}
 */
export const updateButtonApi = (data: ButtonInfo) => {
  return http.put(PORT1 + "/button/manage", data);
};

/**
 * @description 删除按钮
 * @param {Object} params 删除参数
 * @returns {Promise}
 */
export const deleteButtonApi = (params: { id: number }) => {
  return http.delete(PORT1 + "/button/manage", params);
};

// API URL信息接口
export interface ApiUrlInfo {
  url: string;
  method: string;
  summary?: string;
  description?: string;
  operation_id?: string;
  tags?: string[];
  label: string;
}

/**
 * @description 获取所有接口URL列表
 * @returns {Promise}
 */
export const getApiUrlsApi = () => {
  return http.get<{ data: ApiUrlInfo[] }>(PORT1 + "/button/manage/api-urls");
};
