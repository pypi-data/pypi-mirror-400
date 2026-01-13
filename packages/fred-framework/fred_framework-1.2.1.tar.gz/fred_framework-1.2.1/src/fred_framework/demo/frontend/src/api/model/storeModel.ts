/**
 * 门店列表查询参数
 */
export interface StoreListQuery {
  page?: number;
  limit?: number;
  name?: string;
  address?: string;
  // 支持按名称搜索
  province?: string;
  city?: string;
  district?: string;
  // 支持按ID搜索
  country_id?: number;
  province_id?: number;
  city_id?: number;
  district_id?: number;
}

/**
 * 门店信息
 */
export interface StoreInfo {
  id: number;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  scene_num: number;
  created: string;
  modified: string;
  // 新增省市区字段
  country_id?: number;
  country_name?: string;
  province_id?: number;
  province_name?: string;
  city_id?: number;
  city_name?: string;
  district_id?: number;
  district_name?: string;
}

/**
 * 门店列表响应
 */
export interface StoreListResponse {
  total: number;
  records: StoreInfo[];
  pageNum: number;
  pageSize: number;
}

/**
 * 保存门店请求参数
 */
export interface StoreSaveQuery {
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  scene_num?: number;
  // 新增省市区字段
  country_id?: number;
  province_id?: number;
  city_id?: number;
  district_id?: number;
}

/**
 * 门店信息响应
 */
export type StoreInfoResponse = StoreInfo;

/**
 * 门店操作结果
 */
export interface StoreOperationResult {
  message: string;
  id?: number;
}
