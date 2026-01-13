import { defHttp } from "@/api/index";
import { StoreListQuery, StoreListResponse, StoreSaveQuery, StoreInfoResponse } from "@/api/model/storeModel";

enum Api {
  STORE_LIST = "/demo/store/list",
  STORE_INFO = "/demo/store/info/",
  STORE_SAVE = "/demo/store/save",
  STORE_UPDATE = "/demo/store/update/",
  STORE_DELETE = "/demo/store/delete/"
}

/**
 * 获取门店列表
 * @param params 查询参数
 * @returns 门店列表
 */
export function getStoreList(params: StoreListQuery) {
  return defHttp.get<StoreListResponse>(Api.STORE_LIST as string, params);
}

/**
 * 获取门店信息
 * @param storeId 门店ID
 * @returns 门店信息
 */
export function getStoreInfo(storeId: number) {
  return defHttp.get<StoreInfoResponse>(`${Api.STORE_INFO}${storeId}` as string);
}

/**
 * 保存门店信息
 * @param params 门店信息
 * @returns 保存结果
 */
export function saveStore(params: StoreSaveQuery) {
  return defHttp.post(Api.STORE_SAVE as string, params);
}

/**
 * 更新门店信息
 * @param storeId 门店ID
 * @param params 门店信息
 * @returns 更新结果
 */
export function updateStore(storeId: number, params: StoreSaveQuery) {
  return defHttp.put(`${Api.STORE_UPDATE}${storeId}` as string, params);
}

/**
 * 删除门店信息
 * @param storeId 门店ID
 * @returns 删除结果
 */
export function deleteStore(storeId: number) {
  return defHttp.delete(`${Api.STORE_DELETE}${storeId}` as string);
}
