import http from "@/api";
import { PORT1 } from "@/api/config/servicePort";

export const getTableList = (params?: any) => {
  return http.get(PORT1 + "/database/table", params);
};

export const addTable = (params: any) => {
  return http.post(PORT1 + "/database/table", params);
};

export const editTable = (params: any) => {
  return http.put(PORT1 + "/database/table", params);
};

export const deleteTable = (params: { id: number; deleted: number }) => {
  return http.delete(PORT1 + "/database/table", params);
};

// 修改 restoreTable 函数，将 params 作为第二个参数传递
export const restoreTable = (params: { id: number; deleted: number }) => {
  return http.patch(PORT1 + "/database/table", params);
};

export const getFieldTypeList = (params?: any) => {
  return http.get(PORT1 + "/database/field_type", params);
};

export const addFieldType = (params: any) => {
  return http.post(PORT1 + "/database/field_type", params);
};

export const editFieldType = (params: any) => {
  return http.put(PORT1 + "/database/field_type", params);
};

export const deleteFieldType = (params: { id: number }) => {
  return http.delete(PORT1 + "/database/field_type", params);
};

export const getIndexList = (params: any) => {
  return http.get(PORT1 + "/database/index", params);
};

export const addIndex = (params: any) => {
  return http.post(PORT1 + "/database/index", params);
};

export const editIndex = (params: any) => {
  return http.put(PORT1 + "/database/index", params);
};

export const deleteIndex = (id: number) => {
  return http.delete(PORT1 + "/database/index", { id });
};

// 查询表数据
export const getTableData = (params: { table_id: number; pageNum?: number; pageSize?: number }) => {
  return http.get(PORT1 + "/database/table/data", params);
};
