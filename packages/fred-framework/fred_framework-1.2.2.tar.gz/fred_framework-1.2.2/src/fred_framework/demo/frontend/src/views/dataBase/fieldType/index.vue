<template>
  <div class="table-box">
    <ProTable
      :key="locale"
      ref="fieldTypeTable"
      :columns="fieldTypeColumns"
      :request-api="getFieldTypeListApi"
      :data-callback="dataCallbackFieldType"
    >
      <template #tableHeader>
        <el-button type="primary" :icon="CirclePlus" @click="() => openFieldTypeDrawer('addFieldType')">{{
          t("dataBase.addFieldType")
        }}</el-button>
      </template>
      <template #operation="scope">
        <el-button type="primary" link :icon="EditPen" @click="() => openFieldTypeDrawer('edit', scope.row)">{{
          t("dataBase.edit")
        }}</el-button>
        <el-button type="primary" link :icon="Delete" @click="() => handleDeleteFieldType(scope.row)">{{
          t("dataBase.delete")
        }}</el-button>
      </template>
    </ProTable>
    <FieldTypeDrawer ref="fieldTypeDrawerRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import ProTable from "@/components/ProTable/index.vue";
import { getFieldTypeList, addFieldType, editFieldType, deleteFieldType } from "@/api/modules/dataBase";
import { CirclePlus, Delete, EditPen } from "@element-plus/icons-vue";
import type { SearchType } from "@/components/ProTable/interface";
import { useHandleData } from "@/hooks/useHandleData";
import FieldTypeDrawer from "./components/FieldTypeDrawer.vue";

const { t, locale } = useI18n();

interface FieldTypeItem {
  id: number;
  field_type: string;
  desc: string;
}

const fieldTypeTable = ref();
const fieldTypeDrawerRef = ref<InstanceType<typeof FieldTypeDrawer> | null>(null);

const fieldTypeColumns = computed(() => {
  void locale.value;
  return [
    { prop: "id", label: "ID", width: 80 },
    {
      prop: "field_type",
      label: t("dataBase.fieldType"),
      search: { el: "input" as SearchType, props: { placeholder: t("dataBase.inputType") } }
    },
    {
      prop: "desc",
      label: t("dataBase.fieldDesc"),
      search: { el: "input" as SearchType, props: { placeholder: t("dataBase.inputDesc") } }
    },
    { prop: "operation", label: t("dataBase.operation"), width: 180, fixed: "right" }
  ];
});

const dataCallbackFieldType = (data: any) => {
  if (Array.isArray(data?.records)) {
    return { records: data.records, total: data.total };
  }
  return { records: [], total: 0 };
};

const getFieldTypeListApi = async (params: any) => {
  return await getFieldTypeList(params);
};

const openFieldTypeDrawer = (title: string, row: Partial<FieldTypeItem> = {}) => {
  const params = {
    title,
    isView: false,
    row: { ...row },
    api: title === "addFieldType" ? addFieldType : editFieldType,
    getTableList: fieldTypeTable.value?.getTableList
  };
  fieldTypeDrawerRef.value?.acceptParams(params);
};

const handleDeleteFieldType = async (row: FieldTypeItem) => {
  await useHandleData(
    deleteFieldType,
    { id: row.id },
    t("dataBase.deleteFieldTypeConfirm", { name: row.field_type }),
    "warning",
    t
  );
  fieldTypeTable.value?.getTableList();
};
</script>
