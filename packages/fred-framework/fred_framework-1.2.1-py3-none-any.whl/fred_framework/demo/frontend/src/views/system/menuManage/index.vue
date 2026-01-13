<template>
  <div class="table-box">
    <ProTable
      ref="proTable"
      :title="t('menuManage.menuList')"
      row-key="path"
      :indent="20"
      :columns="columns"
      :request-api="getTableList"
      :data-callback="dataCallback"
      :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      :expand-row-keys="expandedRows"
      :pagination="true"
    >
      <!-- 表格 header 按钮 -->
      <template #tableHeader>
        <el-button type="primary" :icon="CirclePlus" @click="openDrawer('新增')">{{ t("menuManage.addMenu") }} </el-button>
      </template>
      <!-- 菜单图标 -->
      <template #icon="scope">
        <el-icon :size="18">
          <component :is="scope.row.meta.icon"></component>
        </el-icon>
      </template>
      <!-- 菜单名称 -->
      <template #title="scope">
        <span
          :class="['menu-title', { 'has-children': scope.row.children && scope.row.children.length }]"
          @click="toggleMenuExpand(scope.row)"
        >
          {{ scope.row.meta.title }}
        </span>
      </template>
      <!-- 停用状态 -->
      <template #deleted="scope">
        <div class="status-container">
          <el-switch
            :model-value="scope.row.deleted"
            :active-value="0"
            :inactive-value="1"
            active-color="#13ce66"
            inactive-color="#dcdfe6"
            @click="handleStatusClick(scope.row)"
          />
        </div>
      </template>

      <!-- 菜单操作 -->
      <template #operation="scope">
        <el-button type="primary" link :icon="EditPen" @click="openDrawer('编辑', scope.row)">
          {{ t("menuManage.edit") }}
        </el-button>
        <el-button type="primary" link :icon="Plus" @click="openDrawer('新增子菜单', scope.row)">
          {{ t("menuManage.addSubMenu") }}
        </el-button>
      </template>
    </ProTable>
    <MenuDrawer ref="drawerRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, computed } from "vue";
import { ColumnProps } from "@/components/ProTable/interface";
import { EditPen, CirclePlus, Plus } from "@element-plus/icons-vue";
import ProTable from "@/components/ProTable/index.vue";
import { getMenu, addMenu, editMenu, deleteMenu, restoreMenu } from "@/api/modules/system";
import MenuDrawer from "./components/MenuDrawer.vue";
import { ElMessageBox, ElMessage } from "element-plus";
import { getFlatMenuList } from "@/utils";
import { useAuthStore } from "@/stores/modules/auth";
import { useI18n } from "vue-i18n";

const proTable = ref();
const drawerRef = ref();

// 国际化
const { t } = useI18n();

// 控制展开的行
const expandedRows = ref<string[]>([]);

const authStore = useAuthStore();

const openDrawer = (title: string, row: any = {}) => {
  const isAdd = title === "新增" || title === "新增子菜单";

  // 如果是新增操作，记录时间戳
  if (isAdd) {
    lastAddTime.value = Date.now();
  }

  let parentMenu: any = null;
  if (!isAdd && row.parent_id) {
    // 编辑时查找父菜单
    const flatMenu = getFlatMenuList(authStore.authMenuList);
    parentMenu = flatMenu.find((item: any) => item.id === row.parent_id) || null;
  }

  // 确保编辑时parent_id有值
  if (!isAdd && row.parent_id === undefined) {
    row.parent_id = 0;
  }
  const params = {
    title,
    isView: title === "查看",
    row: isAdd
      ? {
          meta: {},
          parent_id: title === "新增子菜单" ? row.id : undefined,
          isNew: true
        }
      : JSON.parse(JSON.stringify(row)),
    api: isAdd ? addMenu : editMenu,
    getTableList: proTable.value?.getTableList,
    parentMenu: isAdd ? (title === "新增子菜单" ? row : null) : parentMenu,
    allMenus: authStore.authMenuList // 传递完整的菜单数据
  };
  drawerRef.value?.acceptParams(params);
};

// 点击菜单名称切换展开/收起
const toggleMenuExpand = async (row: any) => {
  if (row.children && row.children.length) {
    const isExpanded = expandedRows.value.includes(row.path);
    if (isExpanded) {
      // 收起
      const index = expandedRows.value.indexOf(row.path);
      if (index > -1) {
        expandedRows.value.splice(index, 1);
      }
    } else {
      // 展开
      expandedRows.value.push(row.path);
    }
    // 使用 nextTick 确保状态更新后表格能正确响应
    await nextTick();
    // 直接操作表格实例
    const tableElement = proTable.value?.element;
    if (tableElement) {
      if (isExpanded) {
        tableElement.toggleRowExpansion(row, false);
      } else {
        tableElement.toggleRowExpansion(row, true);
      }
    }
  }
};

const dataCallback = (data: any) => {
  // 菜单数据通常直接返回树形数组，不需要records包装
  if (Array.isArray(data)) {
    return data;
  }

  // 如果数据在data字段中
  if (data && data.data) {
    if (Array.isArray(data.data)) {
      return data.data;
    }
    return data.data;
  }

  // 如果有records字段（分页格式）
  if (data && data.records) {
    return {
      records: data.records,
      total: data.total,
      pageNum: data.pageNum,
      pageSize: data.pageSize
    };
  }

  // 默认返回空数组
  return [];
};

const columns = computed<ColumnProps[]>(() => [
  {
    prop: "meta.title",
    label: t("menuManage.menuName"),
    width: 200,
    align: "left",
    search: { el: "input", props: { placeholder: t("menuManage.inputMenuName") } }
  },
  { prop: "meta.icon", label: t("menuManage.menuIcon"), width: 100 },
  { prop: "sort", label: t("menuManage.sort"), width: 100 },
  { prop: "path", label: t("menuManage.menuPath") },
  { prop: "component", label: t("menuManage.componentPath") },
  {
    prop: "deleted",
    label: t("menuManage.status"),
    width: 150,
    // 停用状态搜索，默认启用
    enum: [
      { label: t("menuManage.enabled"), value: 0 },
      { label: t("menuManage.disabled"), value: 1 },
      { label: t("menuManage.all"), value: -1 }
    ],
    search: {
      el: "select",
      defaultValue: 0,
      props: { filterable: true, clearable: false, placeholder: t("menuManage.selectStatus") }
    }
  },
  { prop: "operation", label: t("menuManage.operation"), width: 200, fixed: "right" }
]);

// 添加一个标志，用于忽略初始加载时的状态变更
const isDataLoaded = ref(false);
// 记录最近新增的菜单ID，用于避免新增后立即触发状态变更
const recentlyAddedMenus = ref<Set<any>>(new Set());
// 最后一次新增操作的时间戳
const lastAddTime = ref<number>(0);

// 处理状态开关点击事件
const handleStatusClick = async (row: any) => {
  // 添加调试日志

  // 如果是新增操作，直接返回不做任何处理
  if (row.isNew) {
    return;
  }

  // 检查是否在新增操作后的短时间内（5秒内）
  const currentTime = Date.now();
  if (currentTime - lastAddTime.value < 5000) {
    return;
  }

  // 检查是否是最近新增的菜单（通过路径或ID检查）
  if (recentlyAddedMenus.value.has(row.path) || recentlyAddedMenus.value.has(row.id)) {
    // 从记录中移除
    recentlyAddedMenus.value.delete(row.path);
    recentlyAddedMenus.value.delete(row.id);
    return;
  }

  // 如果数据尚未加载完成，忽略此变更
  if (!isDataLoaded.value) {
    return;
  }

  // 计算新状态（切换）
  const newValue = row.deleted === 0 ? 1 : 0;

  try {
    const action = newValue === 1 ? "停用" : "启用";
    await ElMessageBox.confirm(t("menuManage.statusChangeConfirm", { action }), t("common.tip"), {
      confirmButtonText: t("common.confirm"),
      cancelButtonText: t("common.cancel"),
      type: "warning"
    });
    // 只有用户确认后才更新状态
    row.deleted = newValue;
    if (newValue === 0) {
      await restoreMenu({ id: row.id });
    } else {
      await deleteMenu({ id: row.id });
    }
    ElMessage.success(t("menuManage.statusChangeSuccess", { action }));
    proTable.value?.getTableList();
  } catch {}
};
// 添加页面加载完成后的调试
onMounted(() => {
  // 延迟一点时间，确保数据已经加载
  setTimeout(() => {
    // 标记数据已加载完成
    isDataLoaded.value = true;
  }, 1000);
});

const getTableList = (params: any) => {
  return getMenu(params);
};
</script>

<style scoped lang="scss">
.menu-title {
  color: var(--el-color-primary);
  cursor: pointer;
  &.has-children {
    font-weight: bold;
    &:hover {
      text-decoration: underline;
    }
  }
}
.status-container {
  gap: 8px;
  align-items: center;
}
.status-label {
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 4px;
}
.active {
  color: #67c23a;
  background-color: #f0f9eb;
  border: 1px solid #e1f3d8;
}
.deleted {
  color: #f56c6c;
  background-color: #fef0f0;
  border: 1px solid #fde2e2;
}
</style>
