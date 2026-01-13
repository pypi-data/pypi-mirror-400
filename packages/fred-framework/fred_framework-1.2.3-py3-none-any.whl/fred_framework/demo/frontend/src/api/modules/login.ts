import { PORT1 } from "@/api/config/servicePort";
import authButtonList from "@/assets/json/authButtonList.json";
import http from "@/api";
import type {
  LoginFormParams,
  LoginResponse,
  AuthButtons,
  MenuOption,
  ImageCaptchaResponse,
  UserInfo,
  RefreshTokenParams,
  RefreshTokenResponse
} from "@/api/model/loginModel";

/**
 * @name 登录模块
 */

// 用户登录
export const loginApi = (params: LoginFormParams) => {
  return http.post<LoginResponse>(PORT1 + `/login`, params, { loading: false });
};

// 获取菜单列表
export const getAuthMenuListApi = () => {
  return http.get<MenuOption[]>(PORT1 + `/admin_auth/menu`, {}, { loading: false });
};

// 获取按钮权限
export const getAuthButtonListApi = () => {
  return http.get<AuthButtons>(PORT1 + `/admin_auth/buttons`, {}, { loading: false });
  // 如果想让按钮权限变为本地数据，注释上一行代码，并引入本地 authButtonList.json 数据
  return authButtonList;
};

// 获取图片验证码
export const getImageCaptcha = () => {
  return http.get<ImageCaptchaResponse>(PORT1 + `/img_captcha`, {}, { loading: false, responseType: "blob" });
};

// 用户退出登录
export const logoutApi = () => {
  return http.post(PORT1 + `/logout`);
};

// 获取用户信息
export const getUserInfo = () => {
  return http.get<UserInfo>(PORT1 + `/user/info`);
};

// 刷新令牌
export const refreshToken = (params: RefreshTokenParams) => {
  return http.post<RefreshTokenResponse>(PORT1 + `/refresh_token`, params);
};
