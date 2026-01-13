import { ResPage } from "@/api/interface";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";

/**
 * 门店管理模块
 */

// 门店信息接口
export interface StoreInfo {
  id: number;
  name: string;
  address: string;
  // 移除了经度和纬度字段
  // scene_num: number;
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

// 门店列表查询参数
export interface StoreListParams {
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

// 保存门店参数
export interface StoreSaveParams {
  name: string;
  address: string;
  // 移除了经度和纬度字段
  // scene_num?: number;
  // 新增省市区字段
  country_id?: number;
  province_id?: number;
  city_id?: number;
  district_id?: number;
}

// 省市区树形数据接口
export interface RegionTreeItem {
  id: string;
  label: string;
  count?: number;
  device_count?: number;
  country_id?: number;
  children?: RegionTreeItem[];
  stores?: {
    id: string;
    name: string;
  }[];
}

// 获取门店列表
export const getStoreList = (params: StoreListParams) => {
  return http.get<ResPage<StoreInfo>>(PORT1 + `/store`, params);
};

// 获取门店信息
export const getStoreInfo = (storeId: number) => {
  return http.get<StoreInfo>(PORT1 + `/store/detail/${storeId}`);
};

// 保存门店
export const saveStore = (params: StoreSaveParams) => {
  return http.post(PORT1 + `/store`, params);
};

// 更新门店
export const updateStore = (storeId: number, params: StoreSaveParams) => {
  return http.put(PORT1 + `/store/detail/${storeId}`, params);
};

// 删除门店
export const deleteStore = (storeId: number) => {
  return http.delete(PORT1 + `/store/detail/${storeId}`);
};

// 获取省市区树形数据
export const getRegionTree = (includeCount: boolean = true, countType: string = "store") => {
  return http.get<RegionTreeItem[]>(PORT1 + `/store/region_tree?include_count=${includeCount}&count_type=${countType}`);
};

// 根据省市区获取门店列表
export const getStoresByRegion = (params: { province?: string; city?: string; district?: string }) => {
  return http.get<ResPage<StoreInfo>>(PORT1 + `/store/list`, params);
};

// 根据地址获取经纬度
export const getCoordinatesByAddress = (address: string) => {
  return http.post<{ latitude: number; longitude: number; formatted_address: string }>(PORT1 + `/store/geocode`, { address });
};

// 门店场景管理相关接口

// 门店场景信息接口
export interface StoreSceneInfo {
  id: number;
  name: string;
  description: string;
  cover_image: string;
  status: number;
  sort_order: number;
  created: string;
  modified: string;
  hz: number;
  is_bound: boolean;
}

// 门店场景列表查询参数
export interface StoreSceneListParams {
  page?: number;
  limit?: number;
  store_id: number;
  name?: string;
}

// 门店场景绑定参数
export interface StoreSceneBindParams {
  store_id: number;
  scene_id: number;
  model_camera_mappings: ModelCameraMapping[];
}

// 模型摄像头通道映射
export interface ModelCameraMapping {
  model_id: number;
  camera_channel_ids: number[];
}

// 门店场景解绑参数
export interface StoreSceneUnbindParams {
  store_id: number;
  scene_id: number;
}

// 获取门店场景列表（包含绑定状态）
export const getStoreSceneList = (params: StoreSceneListParams) => {
  return http.get<ResPage<StoreSceneInfo>>(PORT1 + `/store/scene`, params);
};

// 绑定门店场景
export const bindStoreScene = (params: StoreSceneBindParams) => {
  return http.post(PORT1 + `/store/scene`, params);
};

// 解绑门店场景
export const unbindStoreScene = (params: StoreSceneUnbindParams) => {
  return http.delete(PORT1 + `/store/scene`, params);
};

// 替换模型摄像头通道关系
export const replaceModelCameraChannel = (params: {
  store_id: number;
  scene_id: number;
  model_id: number;
  old_channel_id: number;
  new_channel_id: number;
}) => {
  return http.put(PORT1 + `/store/model-camera-channel`, params);
};

// 删除模型摄像头通道关系
export const removeModelCameraChannel = (params: {
  store_id: number;
  scene_id: number;
  model_id: number;
  channel_id: number;
}) => {
  return http.delete(PORT1 + `/store/model-camera-channel`, {}, { data: params });
};

// 新增模型摄像头通道关系
export const addModelCameraChannel = (params: { store_id: number; scene_id: number; model_id: number; channel_id: number }) => {
  return http.post(PORT1 + `/store/model-camera-channel`, params);
};

// 获取门店已绑定的场景列表
export const getStoreBoundScenes = (storeId: number) => {
  return http.get<StoreSceneInfo[]>(PORT1 + `/store/scenes/${storeId}`);
};

// 获取门店摄像头通道列表
export const getStoreCameraChannels = (storeId: number) => {
  return http.get<{ code: number; data: CameraChannelInfo[]; message: string }>(PORT1 + `/store/camera-channels/${storeId}`);
};

// 获取门店场景详情（包含模型和摄像头通道关系）
export const getStoreSceneDetails = (storeId: number) => {
  return http.get<StoreSceneDetail[]>(PORT1 + `/store/scene-details/${storeId}`);
};

// 摄像头通道信息接口
export interface CameraChannelInfo {
  id: number;
  channel_id: string;
  image: string;
  status: number;
  camera_type_id: number;
  ip: string;
  user: string;
  type: string;
  brand_name: string;
  brand_id: number;
}

// 获取所有场景（用于绑定选择）
export const getAllScenes = () => {
  return http.get<{ code: number; data: SceneInfo[]; message: string }>(PORT1 + `/scene/all`);
};

// 获取门店未绑定的场景列表
export const getStoreUnboundScenes = (storeId: number) => {
  return http.get<SceneInfo[]>(PORT1 + `/store/unbound-scenes/${storeId}`);
};

// 获取场景的模型列表（用于绑定选择）
export const getSceneModels = (sceneId: number) => {
  return http.get<{ code: number; data: ModelInfo[]; message: string }>(PORT1 + `/scene/models/${sceneId}`);
};

// 场景信息接口（简化版，用于绑定选择）
export interface SceneInfo {
  id: number;
  name: string;
  description: string;
  cover_image: string;
  status: number;
  sort_order: number;
  created: string;
  modified: string;
  hz: number;
  models?: ModelInfo[];
}

// 模型信息接口（用于绑定选择）
export interface ModelInfo {
  id: number;
  name: string;
  desc: string;
  file_path: string;
  created: string;
  modified: string;
}

// 门店场景详情接口
export interface StoreSceneDetail {
  id: number;
  name: string;
  description: string;
  cover_image: string;
  status: number;
  sort_order: number;
  hz: number;
  created: string;
  modified: string;
  models: StoreModelDetail[];
}

// 门店模型详情接口
export interface StoreModelDetail {
  id: number;
  name: string;
  desc: string;
  file_path: string;
  created: string;
  modified: string;
  camera_channels: StoreCameraChannelDetail[];
}

// 门店摄像头通道详情接口
export interface StoreCameraChannelDetail {
  id: number;
  channel_id: string;
  image: string;
  status: number;
  ip: string;
  user: string;
  type: string;
  brand_name: string;
  brand_id: number;
  relation_id: number;
  created: string;
}
