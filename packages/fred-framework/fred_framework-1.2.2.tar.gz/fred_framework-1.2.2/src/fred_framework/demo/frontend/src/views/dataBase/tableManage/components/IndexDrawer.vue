<template>
  <el-drawer v-model="visible" :title="drawerTitle" size="900px">
    <div class="index-drawer-layout">
      <!-- 索引列表 -->
      <el-card class="index-card">
        <template #header>
          <div class="card-header">
            <el-icon><Setting /></el-icon>
            <span>{{ t("dataBase.existingIndex") }}</span>
          </div>
        </template>
        <el-table :data="indexList" style="width: 100%" size="small" border>
          <el-table-column prop="index_name" :label="t('dataBase.indexName')" />
          <el-table-column prop="index_fields" :label="t('dataBase.field')" />
          <el-table-column prop="index_type" :label="t('dataBase.type')" />
          <el-table-column :label="t('dataBase.action')" width="160">
            <template #default="scope">
              <el-button type="primary" size="large" link circle @click="openEditDialog(scope.row)">
                <el-icon class="index-action-icon"><Edit /></el-icon>
              </el-button>
              <el-button size="large" type="danger" link circle @click="removeIndex(scope.row)">
                <el-icon class="index-action-icon"><DeleteFilled /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      <!-- 字段列表 -->
      <el-card class="index-card">
        <template #header>
          <div class="card-header">
            <el-icon><CirclePlus /></el-icon>
            <span>{{ t("dataBase.newIndex") }}</span>
          </div>
        </template>
        <div class="field-select-area">
          <div class="field-select-label">{{ t("dataBase.selectableField") }}</div>
          <el-checkbox-group v-model="selectedFields">
            <el-checkbox v-for="field in fieldList" :key="field.field_name" :label="field.field_name">
              {{ field.field_name }}
            </el-checkbox>
          </el-checkbox-group>
        </div>
        <el-divider />
        <el-input v-model="newIndexName" :placeholder="t('dataBase.indexName')" style="margin: 12px 0" clearable />
        <el-select v-model="indexType" :placeholder="t('dataBase.indexType')" style="width: 160px; margin-bottom: 12px">
          <el-option :label="t('dataBase.normalIndex')" value="INDEX" />
          <el-option :label="t('dataBase.uniqueIndex')" value="UNIQUE" />
          <el-option :label="t('dataBase.fulltextIndex')" value="FULLTEXT" />
        </el-select>
        <div class="index-btn-area">
          <el-button type="primary" @click="createIndex" :disabled="!canCreateIndex">{{ t("dataBase.createIndex") }}</el-button>
        </div>
        <div class="index-tip">{{ t("dataBase.multiSelect") }}</div>
      </el-card>
    </div>
    <div style="margin-top: 16px; text-align: right">
      <el-button @click="close">{{ t("dataBase.close") }}</el-button>
    </div>
  </el-drawer>

  <el-dialog v-model="editDialogVisible" :title="t('dataBase.editIndex')" width="400px">
    <el-form :model="editForm" label-width="80px">
      <el-form-item :label="t('dataBase.indexName')">
        <el-input v-model="editForm.index_name" />
      </el-form-item>
      <el-form-item :label="t('dataBase.field')">
        <el-checkbox-group v-model="editForm.index_fields">
          <el-checkbox v-for="field in fieldList" :key="field.field_name" :label="field.field_name">
            {{ field.field_name }}
          </el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item :label="t('dataBase.type')">
        <el-select v-model="editForm.index_type" style="width: 160px">
          <el-option :label="t('dataBase.normalIndex')" value="INDEX" />
          <el-option :label="t('dataBase.uniqueIndex')" value="UNIQUE" />
          <el-option :label="t('dataBase.fulltextIndex')" value="FULLTEXT" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="editDialogVisible = false">{{ t("dataBase.cancel") }}</el-button>
      <el-button type="primary" @click="submitEdit">{{ t("dataBase.save") }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { useI18n } from "vue-i18n";
import { getIndexList, addIndex, editIndex, deleteIndex } from "@/api/modules/dataBase";
import { Setting, CirclePlus, Edit, DeleteFilled } from "@element-plus/icons-vue";
import { useHandleData } from "@/hooks/useHandleData";

const props = defineProps<{ tableId: number | null; tableName: string; fieldList: any[]; visible: boolean }>();
const emit = defineEmits(["update:visible"]);
const { t } = useI18n();

const visible = ref(props.visible);
watch(
  () => props.visible,
  v => (visible.value = v)
);
watch(visible, v => emit("update:visible", v));

const drawerTitle = computed(() => `${props.tableName} ${t("dataBase.indexManage")}`);

const indexList = ref<any[]>([]);
const selectedFields = ref<string[]>([]);
const newIndexName = ref("");
const indexType = ref("INDEX");

const canCreateIndex = computed(() => {
  return newIndexName.value && selectedFields.value.length > 0 && indexType.value;
});

const editDialogVisible = ref(false);
const editForm = ref({ id: 0, index_name: "", index_fields: [], index_type: "INDEX" });

const fetchIndexes = async () => {
  if (!props.tableId) return;
  const res = await getIndexList({ table_id: props.tableId });
  indexList.value = Array.isArray(res.data) ? res.data : [];
};

watch(
  () => props.tableId,
  () => {
    fetchIndexes();
    selectedFields.value = [];
    newIndexName.value = "";
    indexType.value = "INDEX";
  },
  { immediate: true }
);

const createIndex = async () => {
  if (!props.tableId) return;
  await addIndex({
    table_id: props.tableId,
    index_name: newIndexName.value,
    index_fields: selectedFields.value.join(","),
    index_type: indexType.value
  });
  fetchIndexes();
  selectedFields.value = [];
  newIndexName.value = "";
  indexType.value = "INDEX";
};

const openEditDialog = (row: any) => {
  editForm.value = {
    id: row.id,
    index_name: row.index_name,
    index_fields: row.index_fields ? row.index_fields.split(",") : [],
    index_type: row.index_type || "INDEX"
  };
  editDialogVisible.value = true;
};

const submitEdit = async () => {
  await editIndex({
    id: editForm.value.id,
    table_id: props.tableId,
    index_name: editForm.value.index_name,
    index_fields: editForm.value.index_fields.join(","),
    index_type: editForm.value.index_type
  });
  editDialogVisible.value = false;
  fetchIndexes();
};

const removeIndex = async (row: any) => {
  await useHandleData(deleteIndex, row.id, t("dataBase.deleteIndexConfirm", { name: row.index_name }), "warning", t);
  fetchIndexes();
};

const close = () => {
  visible.value = false;
};
</script>

<style scoped>
.index-drawer-layout {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  justify-content: space-between;
}
.index-card {
  flex: 1 1 380px;
  min-width: 340px;
  margin-bottom: 0;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgb(0 0 0 / 6%);
}
.card-header {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
}
.field-select-area {
  margin-bottom: 8px;
}
.field-select-label {
  margin-bottom: 4px;
  font-weight: bold;
}
.index-btn-area {
  margin: 18px 0 8px;
  text-align: center;
}
.index-tip {
  margin-top: 8px;
  font-size: 13px;
  color: #888888;
  text-align: center;
}
.index-action-icon {
  font-size: 22px;
  font-weight: bold;
}
</style>
