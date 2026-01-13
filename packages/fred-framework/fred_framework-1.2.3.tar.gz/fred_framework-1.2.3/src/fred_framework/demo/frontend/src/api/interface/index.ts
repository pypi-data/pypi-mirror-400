// 请求响应参数（不包含data）
export interface Result {
  code: number;
  message: string;
}

// 请求响应参数（包含data）
export interface ResultData<T = any> extends Result {
  data: T;
}

// 分页响应参数
export interface ResPage<T> {
  records: T[];
  pageNum: number;
  pageSize: number;
  total: number;
}

// 分页请求参数
export interface ReqPage {
  pageNum: number;
  pageSize: number;
}

// 文件上传模块
export namespace Upload {
  export interface ResFileUrl {
    fileUrl: string;
  }

  // 标注图片上传响应
  export interface ResAnnotationImage {
    fileUrl: string;
    file_name: string;
    file_path: string;
    height: number;
    id: number;
    width: number;
  }
}

// 登录模块
export namespace Login {
  export interface ReqLoginForm {
    username: string;
    password: string;
    captcha: string;
  }

  export interface ResLogin {
    id: number;
    username: string;
    access_token: string;
    refresh_token: string;
  }

  export interface ResAuthButtons {
    [key: string]: string[];
  }
}

// 用户管理模块
export namespace User {
  export interface ReqUserParams extends ReqPage {
    username: string;
    createTime: string[];
    status: number;
  }

  export interface ResUserList {
    id: number;
    username: string;
    phone: number;
    user: { detail: { age: number } };
    createTime: string;
    status: number;
    avatar: string;
    forbidden: boolean;
    roleName?: string;
    role_ids?: number[];
    children?: ResUserList[];
  }

  export interface ResStatus {
    userLabel: string;
    userValue: number;
  }

  export interface ResDepartment {
    id: string;
    name: string;
    children?: ResDepartment[];
  }

  export interface ResRole {
    id: string;
    path: string;
    name: string;
    children?: ResDepartment[];
  }
}

export namespace System {
  export interface Menu {
    id: string;
    path: string;
    name: string;
    component: string;
    meta: {
      icon: string;
      title: string;
    };
    assigned: boolean;
    children?: Menu[];
  }

  export interface ReqAccountParams extends ReqPage {
    username: string;
    gender: number;
    idCard: string;
    email: string;
    address: string;
    createTime: string[];
    status: number;
  }

  export interface AccountList {
    id: string;
    username: string;
    phone: string;
    lastLogin: string;
    status: number;
    avatar: string;
    forbidden: boolean;
    roleName: string;
    role_ids?: number[];
    created: string;
    children?: AccountList[];
  }

  export interface Role {
    id: number;
    name: string;
    created: string;
  }

  export interface RoleList {
    id: number;
    name: string;
    created: string;
  }

  export interface Button {
    id: number;
    menu_id: number;
    button_name: string;
    explain: string;
    assigned: boolean;
  }

  export interface MenuNode {
    id: string;
    name: string;
    path: string;
    component: string;
    meta: {
      title: string;
      icon?: string;
    };
    buttons?: Button[];
    hasButtons: boolean;
    assignedButtons: number;
    totalButtons: number;
    isButton?: boolean;
    buttonId?: number;
    children?: MenuNode[];
  }
}
