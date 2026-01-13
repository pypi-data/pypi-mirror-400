/**
 * 上传相关数据模型
 */

/**
 * 文件上传参数
 */
export interface FileUploadParams {
  file: File;
  type?: "image" | "video" | "document" | "model";
  category?: string;
  description?: string;
}

/**
 * 文件上传响应
 */
export interface FileUploadResponse {
  fileUrl: string;
  file_name: string;
  file_path: string;
  file_size: number;
  file_type: string;
  width?: number;
  height?: number;
  duration?: number;
}

/**
 * 图片上传参数
 */
export interface ImageUploadParams {
  file: File;
  category?: string;
  description?: string;
  resize?: {
    width?: number;
    height?: number;
    quality?: number;
  };
}

/**
 * 图片上传响应
 */
export interface ImageUploadResponse {
  fileUrl: string;
  file_name: string;
  file_path: string;
  width: number;
  height: number;
  file_size: number;
  id: number;
}

/**
 * 视频上传参数
 */
export interface VideoUploadParams {
  file: File;
  category?: string;
  description?: string;
  thumbnail?: boolean;
}

/**
 * 视频上传响应
 */
export interface VideoUploadResponse {
  fileUrl: string;
  file_name: string;
  file_path: string;
  file_size: number;
  duration: number;
  thumbnail_url?: string;
  width?: number;
  height?: number;
}

/**
 * 模型文件上传参数
 */
export interface ModelFileUploadParams {
  file: File;
  model_id: number;
  version?: string;
  description?: string;
}

/**
 * 模型文件上传响应
 */
export interface ModelFileUploadResponse {
  fileUrl: string;
  file_name: string;
  file_path: string;
  file_size: number;
  model_id: number;
  version: string;
}

/**
 * 批量上传参数
 */
export interface BatchUploadParams {
  files: File[];
  type: "image" | "video" | "document";
  category?: string;
  description?: string;
}

/**
 * 批量上传响应
 */
export interface BatchUploadResponse {
  success: FileUploadResponse[];
  failed: {
    file: string;
    error: string;
  }[];
  total: number;
  success_count: number;
  failed_count: number;
}

/**
 * 文件删除参数
 */
export interface FileDeleteParams {
  file_path: string;
}

/**
 * 文件信息查询参数
 */
export interface FileInfoQuery {
  file_path: string;
}

/**
 * 文件信息响应
 */
export interface FileInfoResponse {
  file_name: string;
  file_path: string;
  file_size: number;
  file_type: string;
  created: string;
  modified: string;
  width?: number;
  height?: number;
  duration?: number;
}
