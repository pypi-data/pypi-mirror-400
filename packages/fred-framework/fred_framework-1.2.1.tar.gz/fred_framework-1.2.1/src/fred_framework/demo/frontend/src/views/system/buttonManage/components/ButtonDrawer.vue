<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="500px" :title="`${drawerProps.title}按钮`">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps.isView"
      :model="drawerProps.row"
      :hide-required-asterisk="drawerProps.isView"
    >
      <el-form-item label="按钮名称" prop="button_name">
        <el-input v-model="drawerProps.row!.button_name" placeholder="请输入按钮名称" clearable></el-input>
      </el-form-item>
      <el-form-item label="所属菜单" prop="menu_id">
        <el-select
          v-model="drawerProps.row!.menu_id"
          placeholder="请选择所属菜单（支持搜索）"
          filterable
          remote
          :remote-method="searchMenus"
          :loading="menuLoading"
          clearable
          style="width: 100%"
          @change="handleMenuChange"
        >
          <el-option v-for="menu in filteredMenus" :key="menu.id" :label="menu.name" :value="menu.id">
            <div style="display: flex; align-items: center; padding: 4px 0">
              <span style="flex: 1">{{ menu.name }}</span>
              <el-tag v-if="menu.level" size="small" type="info" style="margin-left: 8px">
                {{ menu.level === 1 ? "一级" : menu.level === 2 ? "二级" : "三级" }}
              </el-tag>
            </div>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="API接口" prop="api_list">
        <div class="api-list-container">
          <div v-for="(api, index) in apiList" :key="index" class="api-item">
            <div class="api-item-content">
              <el-form-item
                :prop="`api_list.${index}.api_key`"
                :rules="[{ required: true, message: '请选择API接口', trigger: 'change' }]"
              >
                <el-select
                  v-model="api.api_key"
                  placeholder="请选择API接口（支持搜索）"
                  clearable
                  filterable
                  :filter-method="filterApiUrls"
                  :loading="apiUrlLoading"
                  @change="value => handleApiChange(value, index)"
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in filteredApiUrls"
                    :key="`${item.method}-${item.url}`"
                    :label="`${item.method} ${item.url} - ${item.summary || item.description || item.tags?.[0] || ''}`"
                    :value="`${item.method}-${item.url}`"
                  >
                    <div style="display: flex; align-items: center; padding: 6px 0; line-height: 1.4">
                      <!-- HTTP方法标签 -->
                      <el-tag
                        :type="getMethodTagType(item.method) as any"
                        size="small"
                        style="margin-right: 12px; min-width: 50px; text-align: center; font-weight: bold"
                      >
                        {{ item.method }}
                      </el-tag>

                      <!-- 接口地址 -->
                      <span
                        style="
                          font-family: &quot;Monaco&quot;, &quot;Menlo&quot;, &quot;Ubuntu Mono&quot;, monospace;
                          color: #333;
                          margin-right: 16px;
                          min-width: 200px;
                          font-size: 13px;
                        "
                      >
                        {{ item.url }}
                      </span>

                      <!-- 接口说明 -->
                      <span v-if="item.summary" style="color: #409eff; font-size: 13px; flex: 1; font-weight: 500">
                        {{ item.summary }}
                      </span>
                      <span v-else-if="item.description" style="color: #409eff; font-size: 13px; flex: 1; font-weight: 500">
                        {{ item.description.length > 50 ? item.description.substring(0, 50) + "..." : item.description }}
                      </span>
                      <span
                        v-else-if="item.tags && item.tags.length > 0"
                        style="color: #909399; font-size: 12px; flex: 1; font-style: italic"
                      >
                        {{ item.tags[0] }}
                      </span>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>
            </div>
            <el-button
              type="danger"
              :icon="Delete"
              circle
              size="small"
              @click="removeApi(index)"
              style="margin-left: 8px; flex-shrink: 0"
            />
          </div>
          <el-button type="primary" :icon="Plus" @click="addApi" style="width: 100%; margin-top: 8px"> 添加API接口 </el-button>
        </div>
      </el-form-item>

      <el-form-item label="按钮说明" prop="explain" style="margin-top: 24px">
        <el-input
          v-model="drawerProps.row!.explain"
          type="textarea"
          :rows="3"
          placeholder="请输入按钮说明"
          clearable
          maxlength="255"
          show-word-limit
        ></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="drawerVisible = false"> 取消 </el-button>
      <el-button type="primary" v-show="!drawerProps.isView" @click="handleSubmit"> 确定 </el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts" name="ButtonDrawer">
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, FormInstance, FormRules } from "element-plus";
import { Plus, Delete } from "@element-plus/icons-vue";
import { ButtonInfo, MenuInfo, getApiUrlsApi, ApiUrlInfo } from "../../../../api/modules/buttonManage";

// 表单类型
interface DrawerProps {
  title: string;
  isView: boolean;
  row: Partial<ButtonInfo>;
  api?: (params: any) => Promise<any>;
  getTableList?: () => void;
  defaultMenuId?: number;
}

// 抽屉组件参数
const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: {}
});

// 菜单树形数据
const menuTreeData = ref<MenuInfo[]>([]);
// 菜单搜索相关
const filteredMenus = ref<MenuInfo[]>([]);
const menuLoading = ref(false);

// API URL选项
const apiUrlOptions = ref<ApiUrlInfo[]>([]);
const filteredApiUrls = ref<ApiUrlInfo[]>([]);
const apiUrlLoading = ref(false);

// 表单引用
const ruleFormRef = ref<FormInstance>();

// API列表
const apiList = computed({
  get: () => drawerProps.value.row!.api_list || [],
  set: value => {
    drawerProps.value.row!.api_list = value;
  }
});

// 表单验证规则
const rules = reactive<FormRules>({
  button_name: [{ required: true, message: "请输入按钮名称", trigger: "blur" }],
  menu_id: [{ required: true, message: "请选择所属菜单", trigger: "change" }],
  explain: [{ max: 255, message: "按钮说明不能超过255个字符", trigger: "blur" }]
});

// 接收父组件传递过来的参数
const acceptParams = (params: DrawerProps & { menuTreeData?: MenuInfo[] }) => {
  drawerProps.value = params;
  if (params.menuTreeData) {
    menuTreeData.value = params.menuTreeData;
    // 初始化菜单选项（扁平化树形结构）
    filteredMenus.value = flattenMenuTree(params.menuTreeData);
  }

  // 如果是新增按钮且有默认菜单ID，则设置到表单中
  if (params.title === "新增" && params.defaultMenuId && !params.row.menu_id) {
    params.row.menu_id = params.defaultMenuId;
  }

  // 初始化API列表，如果没有则创建一个空项
  if (!params.row.api_list || params.row.api_list.length === 0) {
    // 向后兼容：如果有旧的api_url字段，则转换为api_list
    if (params.row.api_url) {
      params.row.api_list = [
        {
          api_url: params.row.api_url,
          method: "GET", // 默认使用GET方法
          api_key: `GET-${params.row.api_url}`
        }
      ];
    } else {
      params.row.api_list = [
        {
          api_url: "",
          method: "GET",
          api_key: ""
        }
      ];
    }
  } else {
    // 为现有的API列表添加api_key字段
    params.row.api_list = params.row.api_list.map(api => ({
      ...api,
      api_key: api.api_url && api.method ? `${api.method}-${api.api_url}` : ""
    }));
  }

  drawerVisible.value = true;
};

// 提交数据（新增/编辑）
const handleSubmit = () => {
  ruleFormRef.value!.validate(async valid => {
    if (!valid) return;
    try {
      // 过滤掉空的API项，并只保留后端需要的字段
      const validApiList = (drawerProps.value.row!.api_list || [])
        .filter(api => api.api_url && api.api_url.trim() !== "")
        .map(api => ({
          api_url: api.api_url,
          method: api.method
        }));

      // 构建提交数据，只包含后端需要的字段
      const submitData = {
        button_name: drawerProps.value.row!.button_name,
        menu_id: drawerProps.value.row!.menu_id,
        explain: drawerProps.value.row!.explain || "",
        api_list: validApiList
      };

      // 添加调试信息

      // 检查每个API项的数据格式
      validApiList.forEach(() => {
        // API项已处理
      });

      // 如果是编辑模式，需要添加id字段
      if (drawerProps.value.title === "编辑" && drawerProps.value.row!.id) {
        (submitData as any).id = drawerProps.value.row!.id;
      }

      await drawerProps.value.api!(submitData);
      ElMessage.success({ message: `${drawerProps.value.title}按钮成功！` });
      drawerProps.value.getTableList!();
      drawerVisible.value = false;
    } catch (error) {
      console.error("提交失败:", error);
    }
  });
};

// 加载API URL列表
const loadApiUrls = async () => {
  try {
    apiUrlLoading.value = true;
    const response = await getApiUrlsApi();
    // 处理后端返回的数据格式 {code: 200, data: [...]}
    const data = response?.data || response || [];
    apiUrlOptions.value = Array.isArray(data) ? data : [];
    filteredApiUrls.value = apiUrlOptions.value;
  } catch (error) {
    console.error("加载API URL列表失败:", error);
    ElMessage.error("加载API URL列表失败");
  } finally {
    apiUrlLoading.value = false;
  }
};

// 过滤API URL列表
const filterApiUrls = (query: string) => {
  if (!query) {
    filteredApiUrls.value = apiUrlOptions.value;
    return;
  }

  const lowerQuery = query.toLowerCase();
  filteredApiUrls.value = apiUrlOptions.value.filter(
    item =>
      item.url.toLowerCase().includes(lowerQuery) ||
      item.method.toLowerCase().includes(lowerQuery) ||
      (item.summary && item.summary.toLowerCase().includes(lowerQuery)) ||
      (item.description && item.description.toLowerCase().includes(lowerQuery)) ||
      (item.tags && item.tags.some(tag => tag.toLowerCase().includes(lowerQuery)))
  );
};

// 扁平化菜单树结构
const flattenMenuTree = (menus: MenuInfo[], level: number = 1): MenuInfo[] => {
  const result: MenuInfo[] = [];
  menus.forEach(menu => {
    result.push({ ...menu, level });
    if (menu.children && menu.children.length > 0) {
      result.push(...flattenMenuTree(menu.children, level + 1));
    }
  });
  return result;
};

// 搜索菜单
const searchMenus = (query: string) => {
  if (!query) {
    filteredMenus.value = flattenMenuTree(menuTreeData.value);
    return;
  }

  menuLoading.value = true;
  try {
    const allMenus = flattenMenuTree(menuTreeData.value);
    filteredMenus.value = allMenus.filter(menu => menu.name.toLowerCase().includes(query.toLowerCase()));
  } catch (error) {
    console.error("搜索菜单失败:", error);
    ElMessage.error("搜索菜单失败");
  } finally {
    menuLoading.value = false;
  }
};

// 处理菜单选择变化
const handleMenuChange = (menuId: number) => {
  const selectedMenu = filteredMenus.value.find(menu => menu.id === menuId);
  if (selectedMenu) {
  }
};

// 添加API项
const addApi = () => {
  const currentList = apiList.value || [];
  apiList.value = [...currentList, { api_url: "", method: "GET", api_key: "" }];
};

// 删除API项
const removeApi = (index: number) => {
  const currentList = apiList.value || [];
  if (currentList.length > 1) {
    currentList.splice(index, 1);
    apiList.value = [...currentList];
  } else {
    ElMessage.warning("至少需要保留一个API接口");
  }
};

// 处理API选择变化
const handleApiChange = (selectedKey: string, index: number) => {
  if (!selectedKey) {
    // 如果清空了选择，清空所有字段
    if (apiList.value[index]) {
      apiList.value[index].api_url = "";
      apiList.value[index].method = "";
      apiList.value[index].api_key = "";
    }
    return;
  }

  // 解析选择的API key，格式为 "method-url"
  // 找到第一个连字符的位置，分割方法和URL
  const firstDashIndex = selectedKey.indexOf("-");
  if (firstDashIndex === -1) {
    console.error("无效的API key格式:", selectedKey);
    return;
  }

  const method = selectedKey.substring(0, firstDashIndex);
  const url = selectedKey.substring(firstDashIndex + 1);

  if (apiList.value[index]) {
    apiList.value[index].method = method;
    apiList.value[index].api_url = url;
    apiList.value[index].api_key = selectedKey;
  }
};

// 获取HTTP方法标签类型
const getMethodTagType = (method: string) => {
  const methodTypes: { [key: string]: string } = {
    GET: "success", // 绿色 - 获取数据
    POST: "primary", // 蓝色 - 创建数据
    PUT: "warning", // 橙色 - 更新数据
    DELETE: "danger", // 红色 - 删除数据
    PATCH: "info", // 青色 - 部分更新
    HEAD: "", // 默认色
    OPTIONS: "" // 默认色
  };
  return methodTypes[method] || "";
};

// 组件挂载时加载API URL列表
onMounted(() => {
  loadApiUrls();
});

// 暴露给父组件的方法
defineExpose({
  acceptParams
});
</script>

<style scoped lang="scss">
:deep(.el-tree-select) {
  width: 100%;
}

.api-list-container {
  width: 100%;
}

.api-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background-color: #fafafa;
}

.api-item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

:deep(.el-form-item) {
  margin-bottom: 0;
}

:deep(.el-form-item__label) {
  font-size: 12px;
  color: #666;
  padding-bottom: 4px;
}

:deep(.el-form-item__error) {
  font-size: 11px;
  padding-top: 2px;
}
</style>
