<template>
  <div class="button-tree-list-container">
    <div class="layout-wrapper">
      <!-- 左侧菜单树形筛选器 -->
      <TreeFilter
        ref="treeFilterRef"
        label="name"
        id="id"
        :title="t('buttonManage.selectMenu')"
        :request-api="loadMenuTreeData"
        :default-value="currentMenuId"
        @change="handleMenuFilterChange"
      />

      <!-- 右侧按钮列表 -->
      <div class="descriptions-box card">
        <ProTable
          ref="proTable"
          :title="t('buttonManage.buttonList')"
          row-key="id"
          :columns="columns"
          :request-api="getTableList"
          :data-callback="dataCallback"
          :request-error="handleRequestError"
          :init-param="initParam"
          :pagination="true"
          :request-auto="false"
        >
          <!-- 表格 header 按钮 -->
          <template #tableHeader>
            <el-button type="primary" :icon="CirclePlus" @click="openDrawer('新增')">
              {{ t("buttonManage.addButton") }}
            </el-button>
          </template>

          <!-- API接口列自定义渲染 -->
          <template #api_list="scope">
            <div class="api-list">
              <div v-if="!scope.row.api_list || scope.row.api_list.length === 0" style="color: #999">
                {{ t("buttonManage.noApi") }}
              </div>
              <div v-else>
                <div v-for="(api, index) in scope.row.api_list" :key="index" class="api-item">
                  <el-tag :type="getMethodTagType(api.method) as any" size="small" style="margin-right: 4px">
                    {{ api.method }}
                  </el-tag>
                  <span class="api-url" :title="api.api_url">
                    {{ api.api_url }}
                  </span>
                </div>
              </div>
            </div>
          </template>

          <!-- 按钮操作 -->
          <template #operation="scope">
            <el-button type="primary" link :icon="EditPen" @click="openDrawer('编辑', scope.row)">
              {{ t("buttonManage.edit") }}
            </el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)"> {{ t("buttonManage.delete") }} </el-button>
          </template>
        </ProTable>
      </div>
    </div>

    <!-- 新增/编辑按钮抽屉 -->
    <ButtonDrawer ref="drawerRef" />
  </div>
</template>

<script setup lang="ts" name="buttonManage">
import { ref, onMounted, onUnmounted, nextTick, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { EditPen, CirclePlus } from "@element-plus/icons-vue";
import { useI18n } from "vue-i18n";
import { ColumnProps } from "@/components/ProTable/interface";
import ProTable from "@/components/ProTable/index.vue";
import TreeFilter from "@/components/TreeFilter/index.vue";
import {
  getButtonListApi,
  addButtonApi,
  updateButtonApi,
  deleteButtonApi,
  getMenuListApi,
  type ButtonInfo,
  type ButtonListParams
} from "../../../api/modules/buttonManage";
import ButtonDrawer from "./components/ButtonDrawer.vue";

// 国际化
const { t } = useI18n();

// 响应式数据
const currentMenuId = ref<number | string>("");
const drawerRef = ref();
const proTable = ref();
const treeFilterRef = ref();

// 搜索防抖定时器
const searchTimeout = ref<ReturnType<typeof setTimeout> | null>(null);

// resize事件处理函数
const handleResize = () => {
  // 触发表格重新布局
  if (proTable.value && proTable.value.element && proTable.value.element.value) {
    proTable.value.element.value.doLayout();
  }
};

// 搜索参数，用于联动菜单选择
const initParam = ref<ButtonListParams>({
  menu_id: undefined,
  button_name: ""
});

// 添加调试日志

// 表格列定义 - 使用 computed 确保语言切换时能够响应更新
const columns = computed<ColumnProps[]>(() => [
  { prop: "id", label: t("buttonManage.id"), width: 80 },
  {
    prop: "button_name",
    label: t("buttonManage.buttonName"),
    width: 150,
    search: { el: "input", props: { placeholder: t("buttonManage.inputButtonName") } }
  },
  { prop: "menu_name", label: t("buttonManage.menuName"), width: 150 },
  {
    prop: "api_list",
    label: t("buttonManage.apiUrl"),
    width: 300,
    showOverflowTooltip: true
  },
  {
    prop: "explain",
    label: t("buttonManage.explain"),
    search: { el: "input", props: { placeholder: t("buttonManage.inputExplain") } },
    showOverflowTooltip: true
  },
  { prop: "operation", label: t("buttonManage.operation"), width: 200, fixed: "right" }
]);

// 根据请求方式获取标签类型
const getMethodTagType = (method: string) => {
  const methodMap: { [key: string]: string } = {
    GET: "success",
    POST: "primary",
    PUT: "warning",
    DELETE: "danger",
    PATCH: "info",
    HEAD: "info",
    OPTIONS: "info"
  };
  return methodMap[method.toUpperCase()] || "info";
};

// 加载菜单树形数据（适配 TreeFilter 组件）
const loadMenuTreeData = async () => {
  try {
    const response = await getMenuListApi();
    return response;
  } catch (error) {
    ElMessage.error(t("buttonManage.loadMenuFailed"));
    console.error("加载菜单数据失败:", error);
    return { data: [] };
  }
};

// 处理 TreeFilter 组件的选择变化
const handleMenuFilterChange = (selectedId: string | number) => {
  currentMenuId.value = selectedId;

  // 如果选择了 "全部" 选项，清空菜单筛选条件
  if (!selectedId) {
    initParam.value.menu_id = undefined;
  } else {
    initParam.value.menu_id = Number(selectedId);
  }

  // 刷新表格数据
  if (proTable.value) {
    proTable.value.getTableList();
  }
};

// 表格数据回调处理
const dataCallback = (data: any) => {
  const result = {
    ...data,
    records: data.records.map((item: any) => {
      return {
        ...item,
        // 确保字段存在
        button_name: item.button_name || "",
        menu_name: item.menu_name || "未知菜单",
        api_url: item.api_url || "",
        explain: item.explain || ""
      };
    })
  };

  return result;
};

// 处理请求错误
const handleRequestError = (error: any) => {
  console.error("请求按钮列表失败:", error);
  ElMessage.error(t("buttonManage.loadButtonListFailed"));
};

// 获取表格数据
const getTableList = (params: ButtonListParams) => {
  // 添加防抖处理
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }

  return new Promise(resolve => {
    searchTimeout.value = setTimeout(async () => {
      try {
        const response = await getButtonListApi(params);
        resolve(response);
      } catch (error) {
        console.error("获取按钮列表失败:", error);
        ElMessage.error(t("buttonManage.loadButtonListFailed"));
        resolve({ data: { records: [], total: 0, pageNum: 1, pageSize: 10 } });
      }
    }, 300); // 300ms防抖
  });
};

// 打开抽屉
const openDrawer = (title: string, row: any = {}) => {
  // 先加载最新的菜单数据，确保传递给抽屉的是最新数据
  loadMenuTreeData().then(menuData => {
    const params = {
      title,
      row: { ...row },
      api: title === "新增" ? addButtonApi : (params: any) => updateButtonApi(params),
      getTableList: () => {
        // 刷新表格数据
        if (proTable.value) {
          proTable.value.getTableList();
        }
      },
      // 将菜单数据传递给抽屉组件
      menuTreeData: menuData?.data || [],
      // 如果是新增按钮且左侧有选中的菜单，则自动设置菜单ID
      defaultMenuId: title === "新增" && currentMenuId.value ? Number(currentMenuId.value) : undefined
    };

    drawerRef.value.acceptParams(params);
  });
};

// 删除按钮
const handleDelete = (row: ButtonInfo) => {
  ElMessageBox.confirm(t("buttonManage.deleteConfirm"), t("common.tip"), {
    type: "warning"
  })
    .then(async () => {
      try {
        await deleteButtonApi({ id: row.id });
        ElMessage.success(t("buttonManage.deleteSuccess"));

        // 刷新表格数据
        if (proTable.value) {
          proTable.value.getTableList();
        }
      } catch (error) {
        ElMessage.error(t("buttonManage.deleteFailed"));
        console.error("删除按钮失败:", error);
      }
    })
    .catch(() => {
      // 用户取消删除
    });
};

// 组件挂载时初始化
onMounted(() => {
  // 初始加载表格数据
  if (proTable.value) {
    proTable.value.getTableList();
  }

  // 添加resize事件监听器
  window.addEventListener("resize", handleResize);

  // 确保在DOM更新后重新计算表格高度
  nextTick(() => {
    // 延迟执行以确保DOM完全渲染
    setTimeout(() => {
      handleResize();
    }, 100);
  });

  // 默认折叠全部树形节点
  setTimeout(() => {
    if (treeFilterRef.value?.treeRef?.value) {
      const nodes = treeFilterRef.value.treeRef.value.store.nodesMap;
      if (nodes) {
        for (const node in nodes) {
          if (nodes.hasOwnProperty(node)) {
            nodes[node].expanded = false;
          }
        }
      }
    }
  }, 100);
});

// 组件卸载时清理
onUnmounted(() => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }
  // 移除resize事件监听器
  window.removeEventListener("resize", handleResize);
});
</script>

<style scoped lang="scss">
.button-tree-list-container {
  padding: 20px;
  min-height: 100vh;
  box-sizing: border-box;
}

.layout-wrapper {
  display: flex;
  height: 100%;
  gap: 20px;
}

.descriptions-box.card {
  flex: 1;
  height: 100%;
  overflow: visible;
}

.tree-filter-wrapper {
  width: 300px;
  flex-shrink: 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 右侧表格区域样式通过 .descriptions-box.card 实现 */

/* TreeFilter组件内部样式调整 */
:deep(.card.filter) {
  margin-bottom: 0;
  border: none;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

:deep(.tree-filter-content) {
  flex: 1;
  overflow-y: auto;
}

:deep(.el-table) {
  height: calc(100vh - 150px);
}

:deep(.table-main) {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: visible;
}

:deep(.el-table__inner-wrapper) {
  flex: 1;
  overflow: visible;
}

/* API列表样式 */
:deep(.api-list) {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

:deep(.api-item) {
  display: flex;
  align-items: center;
  padding: 2px 0;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.api-item:last-child) {
  border-bottom: none;
}

:deep(.api-url) {
  flex: 1;
  font-size: 12px;
  color: #666;
  word-break: break-all;
  line-height: 1.4;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .layout-wrapper {
    flex-direction: column;
  }

  .button-tree-list-container {
    padding: 10px;
  }

  :deep(.el-table) {
    height: calc(100vh - 450px);
  }
}
</style>
