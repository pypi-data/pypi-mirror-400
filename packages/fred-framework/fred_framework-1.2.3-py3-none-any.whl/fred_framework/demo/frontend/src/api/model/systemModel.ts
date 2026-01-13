/**
 * 系统相关数据模型
 */

/**
 * 菜单信息
 */
export interface MenuInfo {
  id: string;
  path: string;
  name: string;
  component: string;
  meta: {
    icon: string;
    title: string;
  };
  assigned: boolean;
  children?: MenuInfo[];
}

/**
 * 菜单节点
 */
export interface MenuNode {
  id: string;
  name: string;
  path: string;
  component: string;
  meta: {
    title: string;
    icon?: string;
  };
  buttons?: ButtonInfo[];
  hasButtons: boolean;
  assignedButtons: number;
  totalButtons: number;
  isButton?: boolean;
  buttonId?: number;
  children?: MenuNode[];
}

/**
 * 按钮信息
 */
export interface ButtonInfo {
  id: number;
  menu_id: number;
  button_name: string;
  explain: string;
  assigned: boolean;
}

/**
 * 角色信息
 */
export interface RoleInfo {
  id: number;
  name: string;
  created: string;
}

/**
 * 系统配置信息
 */
export interface SystemConfig {
  id: number;
  name: string;
  value: string;
  desc?: string;
}

/**
 * 系统配置查询参数
 */
export interface SystemConfigQuery {
  pageNum?: number;
  pageSize?: number;
  name?: string;
}

/**
 * 系统配置保存参数
 */
export interface SystemConfigSaveParams {
  id?: number;
  name: string;
  value: string;
  desc?: string;
}

/**
 * 系统配置删除参数
 */
export interface SystemConfigDeleteParams {
  id: number[];
}

/**
 * 系统日志删除参数
 */
export interface SystemLogDeleteParams {
  id: number[];
}

/**
 * 系统日志信息
 */
export interface SystemLog {
  id: number;
  user_id: number;
  username: string;
  api: string;
  method: string;
  code: number;
  created: string;
  api_summary?: string;
  request?: string | null;
  response?: string | null;
}

/**
 * 系统日志查询参数
 */
export interface SystemLogQuery {
  pageNum?: number;
  pageSize?: number;
  username?: string;
  api?: string;
  method?: string;
  code?: number;
  start_date?: string;
  end_date?: string;
}

/**
 * 系统状态信息
 */
export interface SystemStatus {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_usage: number;
  uptime: number;
  total_users: number;
  active_users: number;
  total_requests: number;
  error_rate: number;
}

/**
 * 系统健康检查响应
 */
export interface SystemHealthCheck {
  status: "healthy" | "warning" | "error";
  services: {
    name: string;
    status: "up" | "down";
    response_time?: number;
    error?: string;
  }[];
  timestamp: string;
}
