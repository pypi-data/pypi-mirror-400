<template>
  <div class="table-box">
    <ProTable ref="proTable" :columns="columns" :request-api="getTableList" :init-param="initParam" :data-callback="dataCallback">
      <!-- 表格 header 按钮 -->
      <template #tableHeader="scope">
        <el-button type="primary" :icon="CirclePlus" @click="openDrawer('新增')">{{ t("config.addConfig") }}</el-button>
        <el-button type="danger" :icon="Delete" plain :disabled="!scope.isSelected" @click="batchDelete(scope.selectedListIds)">
          {{ t("config.batchDeleteConfig") }}
        </el-button>
      </template>
      <!-- 表格操作 -->
      <template #operation="scope">
        <el-button type="primary" link :icon="View" @click="openDrawer('查看', scope.row)">{{
          t("config.viewConfig")
        }}</el-button>
        <el-button type="primary" link :icon="EditPen" @click="openDrawer('编辑', scope.row)">{{
          t("config.editConfig")
        }}</el-button>
        <el-button type="primary" link :icon="Delete" @click="deleteConfig(scope.row)">
          {{ t("config.deleteConfig") }}
        </el-button>
      </template>
    </ProTable>
    <ConfigDrawer ref="drawerRef" />
  </div>
</template>

<script setup lang="tsx" name="configManage">
import { reactive, ref, computed } from "vue";
import { SystemConfig } from "@/api/model/systemModel";
import { useHandleData } from "@/hooks/useHandleData";
import ProTable from "@/components/ProTable/index.vue";
import ConfigDrawer from "./components/ConfigDrawer.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import { CirclePlus, Delete, EditPen, View } from "@element-plus/icons-vue";
import { useI18n } from "vue-i18n";
import { getSystemConfig, saveSystemConfig, updateSystemConfig, deleteSystemConfig } from "@/api/modules/system";

// ProTable 实例
const proTable = ref<ProTableInstance>();

// 国际化
const { t } = useI18n();

// 如果表格需要初始化请求参数，直接定义传给 ProTable
const initParam = reactive({});

// dataCallback 是对于返回的表格数据做处理
const dataCallback = (data: any) => {
  return {
    records: data.records,
    total: data.total
  };
};

// 请求列表接口
const getTableList = (params: any) => {
  return getSystemConfig(params);
};

// 表格配置项
const columns = computed<ColumnProps<SystemConfig>[]>(() => [
  {
    type: "selection",
    fixed: "left",
    width: 70
  },
  {
    prop: "id",
    label: t("config.id"),
    width: 80
  },
  {
    prop: "name",
    label: t("config.name"),
    width: 200,
    search: { el: "input", props: { placeholder: t("config.inputName") } }
  },
  {
    prop: "value",
    label: t("config.value"),
    width: 300
  },
  {
    prop: "desc",
    label: t("config.desc")
  },
  { prop: "operation", label: t("config.operation"), fixed: "right", width: 250 }
]);

// 删除配置
const deleteConfig = async (params: SystemConfig) => {
  await useHandleData(deleteSystemConfig, { id: [params.id] }, t("config.deleteConfirm", { name: params.name }), "warning", t);
  proTable.value?.getTableList();
};

// 批量删除配置
const batchDelete = async (id: number[]) => {
  await useHandleData(deleteSystemConfig, { id }, t("config.batchDeleteConfirm"), "warning", t);
  proTable.value?.clearSelection();
  proTable.value?.getTableList();
};

// 打开 drawer(新增、查看、编辑)
const drawerRef = ref<InstanceType<typeof ConfigDrawer> | null>(null);
const openDrawer = (title: string, row: Partial<SystemConfig> = {}) => {
  const params = {
    title,
    isView: title === "查看",
    row: { ...row },
    api: title === "新增" ? saveSystemConfig : title === "编辑" ? updateSystemConfig : undefined,
    getTableList: proTable.value?.getTableList
  };
  drawerRef.value?.acceptParams(params);
};
</script>
