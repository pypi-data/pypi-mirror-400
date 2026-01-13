import { ResultData } from "@/api/interface";
import { showFullScreenLoading, tryHideFullScreenLoading } from "@/components/Loading/fullScreen";
import { LOGIN_URL } from "@/config";
import { ResultEnum } from "@/enums/httpEnum";
import router from "@/routers";
import { useUserStore } from "@/stores/modules/user";
import { getBrowserLang } from "@/utils";
import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from "axios";
import { ElMessage } from "element-plus";
import { AxiosCanceler } from "./helper/axiosCancel";

export interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  loading?: boolean;
  cancel?: boolean;
  timeout?: number;
  retry?: number;
  retryDelay?: number;
}

// 确保 baseURL 是字符串类型，默认值为 "/api"
const baseURL = (import.meta.env.VITE_API_URL as string) || "/api";

const config = {
  // 默认地址请求地址，可在 .env.** 文件中修改
  baseURL: baseURL,
  // 设置超时时间
  timeout: ResultEnum.TIMEOUT as number,
  // 跨域时候允许携带凭证
  withCredentials: true
};

const axiosCanceler = new AxiosCanceler();

// 重试机制
const retryDelay = (delay: number) => new Promise(resolve => setTimeout(resolve, delay));

class RequestHttp {
  service: AxiosInstance;
  public constructor(config: AxiosRequestConfig) {
    // instantiation
    this.service = axios.create(config);

    /**
     * @description 请求拦截器
     */
    this.service.interceptors.request.use(
      (config: CustomAxiosRequestConfig) => {
        const userStore = useUserStore();
        config.cancel ??= true;
        if (config.cancel) {
          axiosCanceler.addPending(config);
        }
        config.loading ??= true;
        if (config.loading) {
          showFullScreenLoading();
        }

        if (config.headers && typeof config.headers.set === "function" && userStore.token) {
          config.headers.set("Authorization", "Bearer " + userStore.token);
        }

        let lang = "zh";
        try {
          lang = localStorage.getItem("locale") || getBrowserLang();
        } catch {}
        if (config.headers) {
          config.headers["accept-language"] = lang;
        }
        return config;
      },
      (error: AxiosError) => {
        return Promise.reject(error);
      }
    );

    /**
     * @description 响应拦截器
     */
    this.service.interceptors.response.use(
      (response: AxiosResponse & { config: CustomAxiosRequestConfig }) => {
        const { data, config } = response;
        const userStore = useUserStore();
        axiosCanceler.removePending(config);
        if (config.loading) {
          tryHideFullScreenLoading();
        }

        if (data.code == ResultEnum.OVERDUE) {
          userStore.setToken("");
          router.replace(LOGIN_URL);
          ElMessage.error(data.message);
          return Promise.reject(data);
        }

        if (data.code && data.code !== ResultEnum.SUCCESS) {
          ElMessage.error(data.message || "操作失败");
          return Promise.reject(data);
        }

        return data;
      },
      async (error: AxiosError<ResultData>) => {
        const { config, response } = error;

        if (config) {
          const retryConfig = config as CustomAxiosRequestConfig;
          const retryCount = retryConfig.retry || 0;
          const retryDelayTime = retryConfig.retryDelay || 1000;

          if (retryCount > 0) {
            retryConfig.retry = retryCount - 1;
            await retryDelay(retryDelayTime);
            return this.service.request(retryConfig);
          }
        }

        tryHideFullScreenLoading();

        if (error.code === "ECONNABORTED") {
          ElMessage.error("请求超时，请稍后重试");
        } else if (error.message?.includes("Network Error")) {
          ElMessage.error("网络错误，请检查网络连接");
        } else if (error.name === "CanceledError" || error.code === "ERR_CANCELED") {
          // 请求被取消，不显示错误提示
        } else if (response?.data?.message) {
          ElMessage.error(response.data.message);
        } else {
          ElMessage.error("请求失败，请稍后重试");
        }

        return Promise.reject(error);
      }
    );
  }

  get<T>(url: string, params?: object, _object = {}): Promise<ResultData<T>> {
    return this.service.get(url, { params, ..._object });
  }

  post<T>(url: string, params?: object | string, _object = {}): Promise<ResultData<T>> {
    return this.service.post(url, params, _object);
  }

  put<T>(url: string, params?: object, _object = {}): Promise<ResultData<T>> {
    return this.service.put(url, params, _object);
  }

  delete<T>(url: string, params?: any, _object = {}): Promise<ResultData<T>> {
    // 如果传入了data字段，则作为请求体发送，否则作为查询参数
    if (_object.data !== undefined) {
      return this.service.delete(url, { data: _object.data, ..._object });
    }
    return this.service.delete(url, { params, ..._object });
  }

  patch<T>(url: string, params?: object, _object = {}): Promise<ResultData<T>> {
    return this.service.patch(url, params, _object);
  }

  download(url: string, params?: object, _object = {}): Promise<BlobPart> {
    return this.service.post(url, params, { ..._object, responseType: "blob" });
  }
}

const defHttp = new RequestHttp(config);
export default defHttp;
export { defHttp };
