<template>
  <div class="table-box">
    <ProTable
      ref="proTable"
      :title="t('systemLog.title')"
      :columns="columns"
      :request-api="getTableList"
      :request-auto="true"
      :init-request="true"
      :data-callback="dataCallback"
      @reset="onReset"
      @search="onSearch"
    >
      <!-- 表格 header 按钮 -->
      <template #tableHeader="scope">
        <el-button type="danger" :icon="Delete" @click="onDelete(scope.selectedListIds)" :disabled="!scope.isSelected">
          {{ t("systemLog.batchDelete") }}
        </el-button>
      </template>

      <!-- 表格操作 -->
      <template #operation="scope">
        <el-button type="primary" link :icon="View" @click="onOpenView(scope.row)"> {{ t("systemLog.view") }} </el-button>
        <el-button type="danger" link :icon="Delete" @click="onDelete([scope.row.id])"> {{ t("systemLog.delete") }} </el-button>
      </template>
    </ProTable>

    <SystemLogDrawer ref="systemLogDrawerRef" />
  </div>
</template>

<script setup lang="ts" name="systemLog">
import { SystemLog } from "@/api/model/systemModel";
import { deleteSystemLog, getSystemLog } from "@/api/modules/system";
import ProTable from "@/components/ProTable/index.vue";
import { ColumnProps } from "@/components/ProTable/interface";
import { useHandleData } from "@/hooks/useHandleData";
import { Delete, View } from "@element-plus/icons-vue";
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import SystemLogDrawer from "./components/SystemLogDrawer.vue";

const { t, locale } = useI18n();

// ProTable 实例
const proTable = ref();

// Drawer 实例
const systemLogDrawerRef = ref();

// 如果表格需要使用 PageSchemaFactory 格式，请实现 dataCallback
const dataCallback = (data: any) => {
  return {
    records: data.records,
    total: data.total,
    page: data.page,
    limit: data.limit
  };
};

// 自定义请求处理函数，处理日期范围选择器的数据转换
const getTableList = (params: any) => {
  const newParams = { ...params };

  // 处理日期范围选择器：将数组转换为 start_date 和 end_date
  if (newParams.created && Array.isArray(newParams.created) && newParams.created.length === 2) {
    newParams.start_date = newParams.created[0];
    newParams.end_date = newParams.created[1];
    delete newParams.created;
  }

  return getSystemLog(newParams);
};

// 请求方法选项
const methodOptions = [
  { label: "GET", value: "GET" },
  { label: "POST", value: "POST" },
  { label: "PUT", value: "PUT" },
  { label: "DELETE", value: "DELETE" },
  { label: "PATCH", value: "PATCH" },
  { label: "HEAD", value: "HEAD" },
  { label: "OPTIONS", value: "OPTIONS" }
];

// 表格配置项
const columns = computed<ColumnProps<SystemLog>[]>(() => {
  void locale.value;
  return [
    { type: "selection", fixed: "left", width: 80 },
    { prop: "id", label: t("systemLog.id"), width: 100 },
    {
      prop: "username",
      label: t("systemLog.username"),
      width: 120,
      search: { el: "input", props: { placeholder: t("systemLog.inputUsername"), clearable: true } }
    },
    {
      prop: "api",
      label: t("systemLog.api"),
      width: 300,
      showOverflowTooltip: true,
      search: {
        el: "input",
        span: 2,
        props: { placeholder: t("systemLog.inputApi"), clearable: true }
      }
    },
    {
      prop: "method",
      label: t("systemLog.method"),
      width: 100,
      enum: methodOptions,
      search: {
        el: "select",
        props: {
          placeholder: t("systemLog.selectMethod"),
          clearable: true,
          filterable: true
        }
      },
      fieldNames: { label: "label", value: "value" }
    },
    {
      prop: "code",
      label: t("systemLog.code"),
      width: 100,
      search: {
        el: "input",
        props: {
          placeholder: t("systemLog.inputCode"),
          clearable: true,
          type: "number"
        }
      }
    },
    {
      prop: "created",
      label: t("systemLog.created"),
      width: 180,
      search: {
        el: "date-picker",
        span: 2,
        props: {
          type: "daterange",
          valueFormat: "YYYY-MM-DD",
          rangeSeparator: t("systemLog.to"),
          startPlaceholder: t("systemLog.startDate"),
          endPlaceholder: t("systemLog.endDate"),
          clearable: true
        }
      }
    },
    { prop: "api_summary", label: t("systemLog.apiSummary"), showOverflowTooltip: true },
    { prop: "operation", label: t("systemLog.operation"), fixed: "right", width: 160 }
  ];
});

// 重置
const onReset = () => {
  // 重置搜索条件
  proTable.value?.reset();
};

// 搜索
const onSearch = () => {
  // 执行搜索
  proTable.value?.search();
};

// 查看
const onOpenView = (row: SystemLog) => {
  systemLogDrawerRef.value.openDrawer(row);
};

// 删除
const onDelete = async (ids: (number | string)[]) => {
  // 转换ID类型
  const numberIds = ids.map(id => Number(id));
  // 确认删除
  await useHandleData(deleteSystemLog, { id: numberIds }, t("systemLog.deleteConfirm", { count: ids.length }), "warning", t);
  // 刷新表格
  proTable.value?.getTableList();
};

// 初始化
onMounted(() => {
  // 延迟1秒执行首次数据加载
  setTimeout(() => {
    proTable.value?.getTableList();
  }, 1000);
});
</script>

<style scoped lang="scss">
@import "@/styles/table-optimization.scss";

.table-box {
  @extend .table-box;
}

// 避免在没有数据的情况下出现滚动条
:deep(.el-table) {
  .el-table__body-wrapper {
    // 当表格为空时，隐藏滚动条
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
