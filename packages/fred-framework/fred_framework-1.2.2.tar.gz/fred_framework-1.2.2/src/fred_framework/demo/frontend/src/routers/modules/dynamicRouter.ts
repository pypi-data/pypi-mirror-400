import { LOGIN_URL } from "@/config";
import router from "@/routers/index";
import { useAuthStore } from "@/stores/modules/auth";
import { useUserStore } from "@/stores/modules/user";
import { ElNotification } from "element-plus";
import { RouteRecordRaw } from "vue-router";

// 引入 views 文件夹下所有 vue 文件
const modules = import.meta.glob("@/views/**/*.vue");

/**
 * @description 初始化动态路由
 */
export const initDynamicRouter = async () => {
  const userStore = useUserStore();
  const authStore = useAuthStore();

  try {
    // 1.获取菜单列表 && 按钮权限列表
    await authStore.getAuthMenuList();
    await authStore.getAuthButtonList();

    // 2.判断当前用户有没有菜单权限
    if (!authStore.authMenuListGet.length) {
      ElNotification({
        title: "无权限访问",
        message: "当前账号无任何菜单权限，请联系系统管理员！",
        type: "warning",
        duration: 3000
      });
      userStore.setToken("");
      router.replace(LOGIN_URL);
      return Promise.reject("No permission");
    }

    // 3.添加动态路由
    authStore.flatMenuListGet.forEach(item => {
      if (item.children) {
        delete item.children;
      }
      if (item.component && typeof item.component == "string") {
        item.component = modules["/src/views" + item.component + ".vue"];
      }
      if (item.meta.isFull) {
        router.addRoute(item as unknown as RouteRecordRaw);
      } else {
        router.addRoute("layout", item as unknown as RouteRecordRaw);
      }
    });

    // 4.手动添加模型日志页面路由（如果不存在）
    // 检查是否已存在modelManage/log的路由
    const hasModelLogRoute = router.hasRoute("modelManage/log");
    if (!hasModelLogRoute) {
      const modelLogRoute: RouteRecordRaw = {
        path: "/modelManage/log",
        name: "modelManage/log",
        component: modules["/src/views/modelManage/log.vue"],
        meta: {
          title: "模型日志",
          icon: "el-icon-document",
          isLink: "",
          isHide: false,
          isFull: false,
          isAffix: false,
          isKeepAlive: true
        }
      };
      router.addRoute("layout", modelLogRoute);
    }

    // 5.手动添加素材图片预览页面路由（如果不存在）
    // 检查是否已存在materialImages的路由
    const hasMaterialImagesRoute = router.hasRoute("materialImages");
    if (!hasMaterialImagesRoute) {
      const materialImagesRoute: RouteRecordRaw = {
        path: "/annotation/material-images",
        name: "materialImages",
        component: modules["/src/views/annotation/materialImages.vue"],
        meta: {
          title: "查看素材",
          icon: "el-icon-picture",
          isLink: "",
          isHide: true,
          isFull: false,
          isAffix: false,
          isKeepAlive: true,
          activeMenu: "/annotation"
        }
      };
      router.addRoute("layout", materialImagesRoute);
    }
  } catch (error) {
    // 当按钮 || 菜单请求出错时，重定向到登陆页
    userStore.setToken("");
    router.replace(LOGIN_URL);
    return Promise.reject(error);
  }
};
