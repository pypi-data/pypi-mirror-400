/**
 * 登录相关数据模型
 */

/**
 * 登录表单参数
 */
export interface LoginFormParams {
  username: string;
  password: string;
  captcha: string;
}

/**
 * 登录响应信息
 */
export interface LoginResponse {
  id: number;
  username: string;
  access_token: string;
  refresh_token: string;
}

/**
 * 权限按钮信息
 */
export interface AuthButtons {
  [key: string]: string[];
}

/**
 * 菜单选项
 */
export interface MenuOption {
  id: string;
  path: string;
  name: string;
  component: string;
  meta: {
    icon: string;
    title: string;
  };
  assigned: boolean;
  children?: MenuOption[];
}

/**
 * 图片验证码响应
 */
export interface ImageCaptchaResponse {
  captcha: string;
  image: string;
}

/**
 * 用户信息
 */
export interface UserInfo {
  id: number;
  username: string;
  avatar?: string;
  roles?: string[];
  permissions?: string[];
}

/**
 * 刷新令牌参数
 */
export interface RefreshTokenParams {
  refresh_token: string;
}

/**
 * 刷新令牌响应
 */
export interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
}
