<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="30%" :title="`${drawerProps.row?.name} - 用户列表`">
    <ProTable
      ref="proTable"
      :columns="columns"
      :request-api="getTableList"
      :init-param="initParam"
      :data-callback="dataCallback"
      row-key="id"
      @selection-change="handleSelectionChange"
      :tool-button="false"
      :pagination="false"
    >
      <template #tableHeader>
        <el-button type="danger" :disabled="!selectedUsers.length" @click="removeSelectedUsers">
          {{ t("role.batchRemoveUser") }}
        </el-button>
      </template>
      <!-- 表格操作 -->
      <template #operation="scope">
        <el-button type="primary" link :icon="Delete" @click="removeUser(scope.row)">
          {{ t("role.removeUser") }}
        </el-button>
      </template>
    </ProTable>
  </el-drawer>
</template>

<script setup lang="tsx" name="RoleUserDrawer">
import { reactive, ref } from "vue";
import { System } from "@/api/interface";
import { useHandleData } from "@/hooks/useHandleData";
import ProTable from "@/components/ProTable/index.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import { Delete } from "@element-plus/icons-vue";
import { getRoleUserList, removeRoleUser } from "@/api/modules/system";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

interface DrawerProps {
  row: Partial<System.Role>;
}

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  row: {}
});

const proTable = ref<ProTableInstance>();
const initParam = reactive({ roleId: "" });
const selectedUsers = ref<System.AccountList[]>([]);

const dataCallback = (data: any) => {
  // 由于pagination为false，直接返回数组数据
  if (Array.isArray(data)) {
    return data;
  }
  return [];
};

const getTableList = (params: any) => {
  const newParams = { ...params };
  delete newParams.pageNum;
  delete newParams.pageSize;
  return getRoleUserList(newParams);
};

// 接收父组件传过来的参数
const acceptParams = (params: DrawerProps) => {
  drawerProps.value = params;
  initParam.roleId = params.row.id!.toString();
  drawerVisible.value = true;
};

const handleSelectionChange = (selection: System.AccountList[]) => {
  selectedUsers.value = selection;
};

const removeSelectedUsers = async () => {
  if (!selectedUsers.value.length) return;
  await useHandleData(
    removeRoleUser,
    {
      userIds: selectedUsers.value.map(u => Number(u.id)),
      roleId: drawerProps.value.row.id
    },
    t("role.batchRemoveUserConfirm"),
    "warning",
    t
  );
  proTable.value?.getTableList();
};

// 表格配置项
const columns: ColumnProps<System.AccountList>[] = [
  { type: "selection", width: 50 },
  { prop: "id", label: "ID", width: 80 },
  {
    prop: "username",
    label: t("user.username")
  },
  {
    prop: "phone",
    label: t("user.phone")
  },
  { prop: "operation", label: t("role.operation"), fixed: "right", width: 120 }
];

// 移除用户
const removeUser = async (params: System.AccountList) => {
  await useHandleData(
    removeRoleUser,
    { userIds: [Number(params.id)], roleId: drawerProps.value.row.id },
    t("role.removeUserConfirm", { name: params.username }),
    "warning",
    t
  );
  proTable.value?.getTableList();
};

defineExpose({
  acceptParams
});
</script>
