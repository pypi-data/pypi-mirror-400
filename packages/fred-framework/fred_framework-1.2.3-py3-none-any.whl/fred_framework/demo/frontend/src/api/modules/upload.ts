import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";
import type {
  FileUploadParams,
  FileUploadResponse,
  ImageUploadParams,
  ImageUploadResponse,
  VideoUploadParams,
  VideoUploadResponse,
  ModelFileUploadParams,
  ModelFileUploadResponse,
  BatchUploadParams,
  BatchUploadResponse,
  FileDeleteParams,
  FileInfoQuery,
  FileInfoResponse
} from "@/api/model/uploadModel";

/**
 * 文件上传模块
 */

// 通用文件上传
export const uploadFile = (params: FileUploadParams) => {
  const formData = new FormData();
  formData.append("file", params.file);
  if (params.type) formData.append("type", params.type);
  if (params.category) formData.append("category", params.category);
  if (params.description) formData.append("description", params.description);

  return http.post<FileUploadResponse>(PORT1 + `/file/upload`, formData, {
    cancel: false,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
};

// 图片上传
export const uploadImg = (params: ImageUploadParams) => {
  const formData = new FormData();
  formData.append("file", params.file);
  if (params.category) formData.append("category", params.category);
  if (params.description) formData.append("description", params.description);
  if (params.resize) {
    formData.append("resize", JSON.stringify(params.resize));
  }

  return http.post<ImageUploadResponse>(PORT1 + `/file/upload/img`, formData, {
    cancel: false,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
};

// 视频上传
export const uploadVideo = (params: VideoUploadParams) => {
  const formData = new FormData();
  formData.append("file", params.file);
  if (params.category) formData.append("category", params.category);
  if (params.description) formData.append("description", params.description);
  if (params.thumbnail !== undefined) {
    formData.append("thumbnail", params.thumbnail.toString());
  }

  return http.post<VideoUploadResponse>(PORT1 + `/file/upload/video`, formData, {
    cancel: false,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
};

// 标注图片上传
export const uploadAnnotationImage = (params: ImageUploadParams) => {
  const formData = new FormData();
  formData.append("file", params.file);
  if (params.category) formData.append("category", params.category);
  if (params.description) formData.append("description", params.description);

  return http.post<ImageUploadResponse>(PORT1 + `/file/upload/annotation`, formData, {
    cancel: false,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
};

// 模型文件上传
export const uploadModelFile = (params: ModelFileUploadParams) => {
  const formData = new FormData();
  formData.append("file", params.file);
  formData.append("model_id", params.model_id.toString());
  if (params.version) formData.append("version", params.version);
  if (params.description) formData.append("description", params.description);

  return http.post<ModelFileUploadResponse>(PORT1 + `/file/upload/model`, formData, {
    cancel: false,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
};

// 批量上传
export const batchUpload = (params: BatchUploadParams) => {
  const formData = new FormData();
  params.files.forEach(file => {
    formData.append(`files`, file);
  });
  formData.append("type", params.type);
  if (params.category) formData.append("category", params.category);
  if (params.description) formData.append("description", params.description);

  return http.post<BatchUploadResponse>(PORT1 + `/file/upload/batch`, formData, {
    cancel: false,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
};

// 删除文件
export const deleteFile = (params: FileDeleteParams) => {
  return http.delete(PORT1 + `/file/delete`, params);
};

// 获取文件信息
export const getFileInfo = (params: FileInfoQuery) => {
  return http.get<FileInfoResponse>(PORT1 + `/file/info`, params);
};
