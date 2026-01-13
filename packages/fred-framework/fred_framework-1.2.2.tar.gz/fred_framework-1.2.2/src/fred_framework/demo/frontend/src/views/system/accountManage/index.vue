<template>
  <div class="table-box">
    <ProTable ref="proTable" :columns="columns" :request-api="getTableList" :init-param="initParam" :data-callback="dataCallback">
      <!-- 表格 header 按钮 -->
      <template #tableHeader="scope">
        <el-button v-auth="'add'" type="primary" :icon="CirclePlus" @click="openDrawer('新增')">{{
          t("user.addUser")
        }}</el-button>
        <el-button
          v-auth="'delete'"
          type="danger"
          :icon="Delete"
          plain
          :disabled="!scope.isSelected"
          @click="batchDelete(scope.selectedListIds)"
        >
          {{ t("user.batchDeleteUser") }}
        </el-button>
      </template>
      <!-- Expand -->
      <template #expand="scope">
        {{ scope.row }}
      </template>
      <!-- 表格操作 -->
      <template #operation="scope">
        <el-button type="primary" link :icon="View" @click="openDrawer('查看', scope.row)">{{ t("user.viewUser") }}</el-button>
        <el-button v-auth="'edit'" type="primary" link :icon="EditPen" @click="openDrawer('编辑', scope.row)">{{
          t("user.editUser")
        }}</el-button>
        <el-button v-auth="'resetPassword'" type="primary" link :icon="Refresh" @click="resetPass(scope.row)">{{
          t("user.resetPassword")
        }}</el-button>
        <el-button
          v-if="!(scope.row.role_ids && scope.row.role_ids.includes(1))"
          v-auth="'delete'"
          type="primary"
          link
          :icon="Delete"
          @click="deleteAccount(scope.row)"
        >
          {{ t("user.deleteUser") }}
        </el-button>
      </template>
    </ProTable>
    <UserDrawer ref="drawerRef" />
    <ImportExcel ref="dialogRef" />
  </div>
</template>

<script setup lang="tsx" name="useProTable">
import { reactive, ref, computed } from "vue";
import { User } from "@/api/interface";
import { useHandleData } from "@/hooks/useHandleData";
import { useAuthButtons } from "@/hooks/useAuthButtons";
import ProTable from "@/components/ProTable/index.vue";
import ImportExcel from "@/components/ImportExcel/index.vue";
import UserDrawer from "@/views/proTable/components/UserDrawer.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import { CirclePlus, Delete, EditPen, Refresh, View } from "@element-plus/icons-vue";
import { useI18n } from "vue-i18n";
import {
  addUser,
  changeUserStatus,
  deleteUser,
  editUser,
  getAccountList,
  getUserStatus,
  resetUserPassWord
} from "@/api/modules/admin";

// ProTable 实例
const proTable = ref<ProTableInstance>();

// 国际化
const { t } = useI18n();

// 如果表格需要初始化请求参数，直接定义传给 ProTable (之后每次请求都会自动带上该参数，此参数更改之后也会一直带上，改变此参数会自动刷新表格数据)
const initParam = reactive({ type: 1 });

// dataCallback 是对于返回的表格数据做处理，如果你后台返回的数据不是 list && total 这些字段，可以在这里进行处理成这些字段
// 或者直接去 hooks/useTable.ts 文件中把字段改为你后端对应的就行
const dataCallback = (data: any) => {
  return {
    records: data.records,
    total: data.total
  };
};

// 如果你想在请求之前对当前请求参数做一些操作，可以自定义如下函数：params 为当前所有的请求参数（包括分页），最后返回请求列表接口
// 默认不做操作就直接在 ProTable 组件上绑定	:requestApi="getUserList"
const getTableList = (params: any) => {
  let newParams = JSON.parse(JSON.stringify(params));
  if (newParams.createTime) {
    newParams.startTime = newParams.createTime[0];
    newParams.endTime = newParams.createTime[1];
  }
  delete newParams.createTime;
  return getAccountList(newParams);
};

// 页面按钮权限（按钮权限既可以使用 hooks，也可以直接使用 v-auth 指令，指令适合直接绑定在按钮上，hooks 适合根据按钮权限显示不同的内容）
const { BUTTONS } = useAuthButtons();

// 表格配置项 - 使用 computed 确保语言切换时能够响应更新
const columns = computed<ColumnProps<User.ResUserList>[]>(() => [
  {
    type: "selection",
    fixed: "left",
    width: 70,
    selectable: (row: User.ResUserList) => !(row.role_ids && row.role_ids.includes(1))
  },
  {
    prop: "id",
    label: t("user.id"),
    width: 80
  },
  {
    prop: "username",
    label: t("user.username"),
    width: 120,
    search: { el: "input", props: { placeholder: t("user.inputUsername") } }
  },
  {
    prop: "phone",
    label: t("user.phone"),
    width: 180,
    search: { el: "input", props: { placeholder: t("user.phoneLast4Digits") } }
  },
  {
    prop: "roleName",
    label: t("user.role"),
    width: 200,
    render: scope => {
      if (!scope.row.roleName) {
        return <span class="text-gray-400">{t("user.noRole")}</span>;
      }
      const roles = scope.row.roleName.split(",");
      return (
        <div class="flex flex-wrap gap-1">
          {roles.map(role => (
            <el-tag key={role} size="small" type="primary">
              {role}
            </el-tag>
          ))}
        </div>
      );
    }
  },
  {
    prop: "forbidden",
    label: t("user.status"),
    enum: getUserStatus,
    search: { el: "select", props: { filterable: true, placeholder: t("user.selectStatus") } },
    fieldNames: { label: "label", value: "value" },
    render: scope => {
      const isSysAdmin = scope.row.role_ids && scope.row.role_ids.includes(1);
      return (
        <>
          {BUTTONS.value.forbidden && !isSysAdmin ? (
            <el-switch
              style="--el-switch-on-color:#ff4949;--el-switch-off-color:#67c23a"
              model-value={scope.row.forbidden}
              active-text={scope.row.forbidden ? t("user.disabled") : t("user.normal")}
              active-value={true}
              inactive-value={false}
              onClick={() => changeStatus(scope.row)}
            />
          ) : (
            <el-tag type={scope.row.forbidden ? "danger" : "success"}>
              {scope.row.forbidden ? t("user.disabled") : t("user.normal")}
            </el-tag>
          )}
        </>
      );
    }
  },
  {
    prop: "lastLogin",
    label: t("user.lastLogin"),
    width: 180,
    search: {
      el: "date-picker",
      span: 2,
      props: {
        type: "datetimerange",
        valueFormat: "YYYY-MM-DD HH:mm:ss",
        "start-placeholder": t("user.startTime"),
        "end-placeholder": t("user.endTime")
      },
      defaultValue: []
    }
  },
  {
    prop: "created",
    label: t("user.created"),
    width: 180
  },
  { prop: "operation", label: t("user.operation"), fixed: "right", width: 330 }
]);

// 删除用户信息
const deleteAccount = async (params: User.ResUserList) => {
  await useHandleData(deleteUser, { id: [params.id] }, t("user.deleteConfirm", { name: params.username }), "warning", t);
  proTable.value?.getTableList();
};

// 批量删除用户信息
const batchDelete = async (id: string[]) => {
  await useHandleData(deleteUser, { id }, t("user.batchDeleteConfirm"), "warning", t);
  proTable.value?.clearSelection();
  proTable.value?.getTableList();
};

// 重置用户密码
const resetPass = async (params: User.ResUserList) => {
  await useHandleData(
    resetUserPassWord,
    { id: params.id },
    t("user.resetPasswordConfirm", { name: params.username }),
    "warning",
    t
  );
  proTable.value?.getTableList();
};

// 切换用户状态
const changeStatus = async (row: User.ResUserList) => {
  await useHandleData(changeUserStatus, { id: row.id }, t("user.statusChangeConfirm", { name: row.username }), "warning", t);
  proTable.value?.getTableList();
};

// 打开 drawer(新增、查看、编辑)
const drawerRef = ref<InstanceType<typeof UserDrawer> | null>(null);
const openDrawer = (title: string, row: Partial<User.ResUserList> = {}) => {
  const params = {
    title,
    isView: title === "查看",
    row: { ...row },
    api: title === "新增" ? addUser : title === "编辑" ? editUser : undefined,
    getTableList: proTable.value?.getTableList
  };
  drawerRef.value?.acceptParams(params);
};
</script>
