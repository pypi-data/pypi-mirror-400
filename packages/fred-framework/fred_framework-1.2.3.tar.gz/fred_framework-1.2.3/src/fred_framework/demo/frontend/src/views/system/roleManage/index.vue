<template>
  <div class="table-box">
    <ProTable ref="proTable" :columns="columns" :request-api="getTableList" :init-param="initParam" :data-callback="dataCallback">
      <!-- 表格 header 按钮 -->
      <template #tableHeader="scope">
        <el-button type="primary" :icon="CirclePlus" @click="openDrawer('新增')">{{ t("role.addRole") }}</el-button>
        <el-button type="danger" :icon="Delete" plain :disabled="!scope.isSelected" @click="batchDelete(scope.selectedListIds)">
          {{ t("role.batchDeleteRole") }}
        </el-button>
      </template>
      <!-- 表格操作 -->
      <template #operation="scope">
        <el-button type="primary" link :icon="User" @click="openUserDrawer(scope.row)">{{ t("role.userManage") }}</el-button>
        <el-button type="success" link :icon="Menu" @click="openMenuDrawer(scope.row)">{{ t("role.menuPermission") }}</el-button>
        <el-button type="warning" link :icon="Operation" @click="openButtonDrawer(scope.row)">{{
          t("role.buttonPermission")
        }}</el-button>
        <el-button type="primary" link :icon="EditPen" @click="openDrawer('编辑', scope.row)">{{ t("role.editRole") }}</el-button>
        <el-button v-if="scope.row.id !== 1" type="primary" link :icon="Delete" @click="deleteRoleFunc(scope.row)">
          {{ t("role.deleteRole") }}
        </el-button>
        <el-tooltip v-else :content="t('role.cannotDeleteSuperAdmin')" placement="top">
          <el-button type="info" link :icon="Delete" disabled>
            {{ t("role.deleteRole") }}
          </el-button>
        </el-tooltip>
      </template>
    </ProTable>
    <RoleDrawer ref="drawerRef" />
    <RoleUserDrawer ref="userDrawerRef" />
    <RoleMenuDrawer ref="menuDrawerRef" />
    <RoleButtonDrawer ref="buttonDrawerRef" />
  </div>
</template>

<script setup lang="tsx" name="roleManage">
import { reactive, ref, computed } from "vue";
import { System } from "@/api/interface";
import { useHandleData } from "@/hooks/useHandleData";
import ProTable from "@/components/ProTable/index.vue";
import RoleDrawer from "./components/RoleDrawer.vue";
import RoleUserDrawer from "./components/RoleUserDrawer.vue";
import RoleMenuDrawer from "./components/RoleMenuDrawer.vue";
import RoleButtonDrawer from "./components/RoleButtonDrawer.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import { CirclePlus, Delete, EditPen, User, Menu, Operation } from "@element-plus/icons-vue";
import { addRole, deleteRole, editRole, getRoleList } from "@/api/modules/system";
import { useI18n } from "vue-i18n";
import { ElMessage } from "element-plus";

// 国际化
const { t } = useI18n();

// ProTable 实例
const proTable = ref<ProTableInstance>();
const initParam = reactive({});

const dataCallback = (data: any) => {
  return {
    records: data.records,
    total: data.total
  };
};

const getTableList = (params: any) => {
  return getRoleList(params);
};

// 表格配置项 - 使用 computed 确保语言切换时能够响应更新
const columns = computed<ColumnProps<System.Role>[]>(() => [
  { type: "selection", fixed: "left", width: 70 },
  { prop: "id", label: t("role.id"), width: 80 },
  {
    prop: "name",
    label: t("role.name"),
    search: { el: "input", props: { placeholder: t("role.inputRoleName") } }
  },
  {
    prop: "created",
    label: t("role.created"),
    width: 180
  },
  { prop: "operation", label: t("role.operation"), fixed: "right", width: 450 }
]);

// 删除角色信息
const deleteRoleFunc = async (params: System.Role) => {
  await useHandleData(deleteRole, { id: [params.id] }, t("role.deleteConfirm", { name: params.name }), "warning", t);
  proTable.value?.getTableList();
};

// 批量删除角色信息
const batchDelete = async (id: string[]) => {
  const roleIds = id.map(Number);

  // 检查是否包含超级管理员角色（ID为1）
  if (roleIds.includes(1)) {
    ElMessage.warning(t("role.cannotDeleteSuperAdmin"));
    return;
  }

  await useHandleData(deleteRole, { id: roleIds }, t("role.batchDeleteConfirm"), "warning", t);
  proTable.value?.clearSelection();
  proTable.value?.getTableList();
};

// 打开 drawer(新增、查看、编辑)
const drawerRef = ref<InstanceType<typeof RoleDrawer> | null>(null);
const openDrawer = (title: string, row: Partial<System.Role> = {}) => {
  const params = {
    title,
    isView: title === "查看",
    row: { ...row },
    api: title === "新增" ? addRole : title === "编辑" ? editRole : undefined,
    getTableList: proTable.value?.getTableList
  };
  drawerRef.value?.acceptParams(params);
};

const userDrawerRef = ref<InstanceType<typeof RoleUserDrawer> | null>(null);
const openUserDrawer = (row: Partial<System.Role> = {}) => {
  const params = {
    row: { ...row }
  };
  userDrawerRef.value?.acceptParams(params);
};

const menuDrawerRef = ref<InstanceType<typeof RoleMenuDrawer> | null>(null);
const openMenuDrawer = (row: Partial<System.Role> = {}) => {
  const params = {
    row: { ...row }
  };
  menuDrawerRef.value?.acceptParams(params);
};

const buttonDrawerRef = ref<InstanceType<typeof RoleButtonDrawer> | null>(null);
const openButtonDrawer = (row: Partial<System.Role> = {}) => {
  const params = {
    row: { ...row }
  };
  buttonDrawerRef.value?.acceptParams(params);
};
</script>
