<template>
  <el-drawer v-model="visible" :title="drawerTitle" size="90%" :destroy-on-close="true">
    <div class="table-data-drawer">
      <ProTable
        ref="proTable"
        :columns="columns"
        :request-api="getTableDataApi"
        :data-callback="dataCallback"
        :init-param="initParam"
        :pagination="true"
      >
      </ProTable>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from "vue";
import { useI18n } from "vue-i18n";
import ProTable from "@/components/ProTable/index.vue";
import { getTableData } from "@/api/modules/dataBase";
import type { ColumnProps } from "@/components/ProTable/interface";

const props = defineProps<{ tableId: number | null; tableName: string; visible: boolean }>();
const emit = defineEmits(["update:visible"]);
const { t } = useI18n();

const visible = ref(props.visible);
watch(
  () => props.visible,
  v => (visible.value = v)
);
watch(visible, v => emit("update:visible", v));

const drawerTitle = computed(() => `${props.tableName} ${t("dataBase.viewData")}`);

const proTable = ref();
const columns = ref<ColumnProps[]>([]);
const initParam = ref<{ table_id: number }>({ table_id: props.tableId || 0 });

watch(
  () => props.tableId,
  newId => {
    if (newId) {
      initParam.value = { table_id: newId };
      // 重置表格
      nextTick(() => {
        proTable.value?.getTableList();
      });
    }
  },
  { immediate: true }
);

const dataCallback = (data: any) => {
  if (Array.isArray(data?.records)) {
    // 动态生成列（每次有数据时都重新生成，确保列是最新的）
    if (data.records.length > 0) {
      const firstRecord = data.records[0];
      const newColumns: ColumnProps[] = Object.keys(firstRecord).map(key => ({
        prop: key,
        label: key,
        minWidth: 120,
        align: "left"
      }));
      // 只有当列发生变化时才更新
      const currentKeys = columns.value
        .map(col => col.prop)
        .sort()
        .join(",");
      const newKeys = newColumns
        .map(col => col.prop)
        .sort()
        .join(",");
      if (currentKeys !== newKeys) {
        columns.value = newColumns;
      }
    }
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

const getTableDataApi = async (params: any) => {
  try {
    const result = await getTableData({
      table_id: props.tableId || 0,
      pageNum: params.pageNum || 1,
      pageSize: params.pageSize || 10
    });
    return result;
  } catch (error) {
    throw error;
  }
};

// 监听 visible 变化，打开时重置列并刷新数据
watch(visible, newVal => {
  if (newVal && props.tableId) {
    columns.value = [];
    nextTick(() => {
      proTable.value?.getTableList();
    });
  }
});
</script>

<style scoped lang="scss">
.table-data-drawer {
  padding: 0;
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
