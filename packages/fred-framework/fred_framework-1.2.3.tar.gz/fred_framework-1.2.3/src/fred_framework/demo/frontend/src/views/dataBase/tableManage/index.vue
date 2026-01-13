<template>
  <div class="table-box">
    <ProTable :key="locale" ref="proTable" :columns="columns" :request-api="getTableListApi" :data-callback="dataCallback">
      <template #tableHeader>
        <el-button type="primary" :icon="CirclePlus" @click="() => openDrawer('addTable')">{{
          t("dataBase.addTable")
        }}</el-button>
      </template>
      <template #status="scope">
        <div class="switch-wrapper">
          <div class="status-container">
            <el-switch
              :model-value="scope.row.deleted"
              :active-value="0"
              :inactive-value="1"
              active-color="#13ce66"
              inactive-color="#dcdfe6"
              @update:model-value="value => handleStatusChange(scope.row, Number(value))"
            />
          </div>
        </div>
      </template>
      <template #operation="scope">
        <el-button
          type="primary"
          link
          :icon="EditPen"
          :disabled="scope.row.deleted === 1"
          @click="() => openDrawer('edit', scope.row)"
        >
          {{ t("dataBase.edit") }}
        </el-button>
        <el-button
          type="primary"
          link
          :icon="Setting"
          :disabled="scope.row.deleted === 1"
          @click="() => openIndexDrawer(scope.row)"
        >
          {{ t("dataBase.indexManage") }}
        </el-button>
        <el-button type="primary" link :icon="View" :disabled="scope.row.deleted === 1" @click="() => openDataDrawer(scope.row)">
          {{ t("dataBase.viewData") }}
        </el-button>
      </template>
    </ProTable>

    <DataBaseDrawer ref="drawerRef" />
    <IndexDrawer
      v-if="indexDrawerVisible"
      :table-id="currentTableId"
      :table-name="currentTableName"
      :field-list="currentFieldList"
      v-model:visible="indexDrawerVisible"
    />
    <TableDataDrawer
      v-if="dataDrawerVisible"
      :table-id="currentTableId"
      :table-name="currentTableName"
      v-model:visible="dataDrawerVisible"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import ProTable from "@/components/ProTable/index.vue";
import { getTableList, addTable, editTable, deleteTable, restoreTable } from "@/api/modules/dataBase";
import { CirclePlus, EditPen, Setting, View } from "@element-plus/icons-vue";
import type { SearchType } from "@/components/ProTable/interface";
import DataBaseDrawer from "./components/DataBaseDrawer.vue";
import IndexDrawer from "./components/IndexDrawer.vue";
import TableDataDrawer from "./components/TableDataDrawer.vue";
import { ElMessage, ElMessageBox } from "element-plus";

const { t, locale } = useI18n();

interface TableItem {
  id: number;
  name: string;
  desc: string;
  deleted: number;
  field: any[];
}

const proTable = ref();
const drawerRef = ref<InstanceType<typeof DataBaseDrawer> | null>(null);
const indexDrawerVisible = ref(false);
const dataDrawerVisible = ref(false);
const currentTableId = ref<number | null>(null);
const currentTableName = ref<string>("");
const currentFieldList = ref<any[]>([]);

const columns = computed(() => {
  void locale.value;
  return [
    { prop: "id", label: "ID", width: 80 },
    {
      prop: "name",
      label: t("dataBase.tableName"),
      width: 180,
      align: "left",
      search: { el: "input" as SearchType, props: { placeholder: t("dataBase.inputTableName") } }
    },
    {
      prop: "desc",
      label: t("dataBase.remark"),
      search: { el: "input" as SearchType, props: { placeholder: t("dataBase.inputRemark") } }
    },
    { prop: "created", label: t("dataBase.created"), width: 200 },
    { prop: "modified", label: t("dataBase.modified"), width: 200 },
    { prop: "status", label: t("dataBase.deleteStatus"), width: 180, slot: true },
    { prop: "operation", label: t("dataBase.operation"), width: 200, fixed: "right" }
  ];
});

const dataCallback = (data: any) => {
  if (Array.isArray(data?.records)) {
    return { records: data.records, total: data.total };
  }
  if (Array.isArray(data?.list)) {
    return { records: data.list, total: data.total || data.totalCount };
  }
  if (Array.isArray(data)) {
    return { records: data, total: data.length };
  }
  return { records: [], total: 0 };
};

const getTableListApi = async (params: any) => {
  try {
    const result = await getTableList(params);
    return result;
  } catch (error) {
    throw error;
  }
};

const openDrawer = (title: string, row: Partial<TableItem> = {}) => {
  const params = {
    title,
    isView: false,
    row: { ...row },
    api: title === "addTable" ? addTable : editTable,
    getTableList: proTable.value?.getTableList
  };
  drawerRef.value?.acceptParams(params);
};

const openIndexDrawer = (row: TableItem) => {
  currentTableId.value = row.id;
  currentTableName.value = row.name;
  currentFieldList.value = Array.isArray(row.field) ? row.field : [];
  indexDrawerVisible.value = true;
};

const openDataDrawer = (row: TableItem) => {
  currentTableId.value = row.id;
  currentTableName.value = row.name;
  dataDrawerVisible.value = true;
};

const handleStatusChange = (row: TableItem, value: number) => {
  if (row.deleted !== undefined && row.deleted !== value) {
    // const originalStatus = row.deleted;
    const action = value === 1 ? "停用" : "启用";
    ElMessageBox.confirm(`确定要${action}该表吗？`, "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    })
      .then(() => {
        const params = {
          id: row.id,
          deleted: value
        };
        if (value === 1) {
          deleteTable(params)
            .then(() => {
              ElMessage.success(t("dataBase.statusChangeSuccess"));
              row.deleted = value; // 只有成功后才更新状态
              proTable.value?.getTableList();
            })
            .catch(() => {
              // 错误信息已在拦截器中处理
            });
        } else {
          restoreTable(params)
            .then(() => {
              ElMessage.success(t("dataBase.statusChangeSuccess"));
              row.deleted = value; // 只有成功后才更新状态
              proTable.value?.getTableList();
            })
            .catch(() => {
              // 错误信息已在拦截器中处理
            });
        }
      })
      .catch(() => {
        // ElMessage.info(t("dataBase.operationCancelled"));
      });
  }
};
</script>

<style scoped lang="scss">
.switch-wrapper {
  gap: 8px;
  align-items: center;
}
.status-container {
  gap: 8px;
  align-items: center;
}

// 避免在没有数据的情况下出现滚动条
:deep(.el-table) {
  .el-table__body-wrapper {
    // 当表格为空时，隐藏滚动条（通过 :has() 选择器）
    &:has(.el-table__empty-block) {
      overflow: hidden !important;
    }
  }

  .el-table__empty-block {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }
}
</style>
