<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="700px" :title="drawerTitle">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps.isView"
      :model="drawerProps.row"
      :hide-required-asterisk="drawerProps.isView"
    >
      <el-form-item :label="t('dataBase.tableName')" prop="name">
        <el-input v-model="drawerProps.row!.name" :placeholder="t('dataBase.inputTableName')" clearable></el-input>
      </el-form-item>
      <el-form-item :label="t('dataBase.remark')" prop="desc">
        <el-input v-model="drawerProps.row!.desc" type="textarea" :placeholder="t('dataBase.inputRemark')" clearable></el-input>
      </el-form-item>
    </el-form>
    <!-- 字段列表 -->
    <div style="margin: 20px 0">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px">
        <span style="font-weight: bold">{{ t("dataBase.fieldList") }}</span>
        <el-button size="small" type="primary" @click="addField" :disabled="drawerProps.isView">{{
          t("dataBase.addField")
        }}</el-button>
      </div>
      <el-table :data="fields" border size="small" style="width: 100%">
        <el-table-column :label="t('dataBase.fieldName')" prop="field_name">
          <template #default="scope">
            <el-input v-model="scope.row.field_name" :placeholder="t('dataBase.fieldName')" :disabled="drawerProps.isView" />
          </template>
        </el-table-column>
        <el-table-column :label="t('dataBase.fieldDesc')" prop="field_desc">
          <template #default="scope">
            <el-input v-model="scope.row.field_desc" :placeholder="t('dataBase.fieldDesc')" :disabled="drawerProps.isView" />
          </template>
        </el-table-column>
        <el-table-column :label="t('dataBase.fieldType')" prop="field_type">
          <template #default="scope">
            <el-select
              v-model="scope.row.field_type"
              :placeholder="t('dataBase.fieldType')"
              :disabled="drawerProps.isView"
              style="width: 120px"
            >
              <el-option v-for="item in fieldTypeOptions" :key="item.id" :label="item.desc" :value="item.id" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column :label="t('dataBase.defaultValue')" prop="default_value">
          <template #default="scope">
            <el-input
              v-model="scope.row.default_value"
              :placeholder="t('dataBase.inputDefaultValue')"
              :disabled="drawerProps.isView"
            />
          </template>
        </el-table-column>
        <el-table-column :label="t('dataBase.isIndex')" prop="is_index" width="90">
          <template #default="scope">
            <el-icon class="index-icon-large" v-if="scope.row.is_index" color="#67C23A"><Check /></el-icon>
            <el-icon class="index-icon-large" v-else color="#F56C6C"><Close /></el-icon>
          </template>
        </el-table-column>
        <el-table-column :label="t('dataBase.action')" width="80">
          <template #default="scope">
            <el-button v-if="!drawerProps.isView" size="small" type="danger" @click="removeField(scope.$index)" link circle>
              <el-icon class="delete-icon-large"><DeleteFilled /></el-icon>
            </el-button>
          </template>
        </el-table-column>
        <template #empty>
          <div style="padding: 20px; color: #999999; text-align: center">{{ t("dataBase.noField") }}</div>
        </template>
      </el-table>
    </div>
    <template #footer>
      <el-button @click="drawerVisible = false">{{ t("dataBase.cancel") }}</el-button>
      <el-button v-show="!drawerProps.isView" type="primary" @click="handleSubmit">{{ t("dataBase.confirm") }}</el-button>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage, FormInstance } from "element-plus";
import { getFieldTypeList } from "@/api/modules/dataBase";
import { Check, Close, DeleteFilled } from "@element-plus/icons-vue";

const { t } = useI18n();

const rules = reactive({
  name: [{ required: true, message: t("dataBase.inputTableName") }],
  desc: [{ required: true, message: t("dataBase.inputRemark") }]
});

interface FieldItem {
  id?: number;
  field_name: string;
  field_desc: string;
  field_type: number | null;
  default_value?: string;
}

interface DrawerProps {
  title: string;
  isView: boolean;
  row: Partial<{ id: number; name: string; desc: string; field: FieldItem[] }>;
  api?: (params: any) => Promise<any>;
  getTableList?: () => void;
}

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: {}
});

const drawerTitle = computed(() => {
  // 确保使用的翻译键存在
  const title = drawerProps.value.title;
  const titleKey = title === "view" ? "table" : title === "addTable" ? "addTable" : `${title}`;
  return t(`dataBase.${titleKey}`);
});

const fields = ref<FieldItem[]>([]);
const fieldTypeOptions = ref<any[]>([]);

// 拉取字段类型
const fetchFieldTypes = async () => {
  const res = await getFieldTypeList({ select_all: true });
  const data = res.data as any;
  fieldTypeOptions.value = Array.isArray(data) ? data : [];
};

onMounted(() => {
  fetchFieldTypes();
});

// 打开抽屉时同步字段
const acceptParams = (params: DrawerProps) => {
  drawerProps.value = params;
  // 兼容编辑和新增
  const rawFields = Array.isArray(params.row?.field) ? JSON.parse(JSON.stringify(params.row.field)) : [];

  // 直接使用default字段
  fields.value = rawFields.map(field => {
    return {
      ...field,
      default_value: field.default || ""
    };
  });

  drawerVisible.value = true;
};

defineExpose({
  acceptParams
});

// 添加字段
const addField = () => {
  fields.value.push({ field_name: "", field_desc: "", field_type: null, default_value: "" });
};
// 删除字段
const removeField = (idx: number) => {
  const field = fields.value[idx];
  if (field && (field as any).is_index) {
    ElMessage.warning(t("dataBase.deleteIndexFirst"));
    return;
  }
  fields.value.splice(idx, 1);
};

// 校验字段列表
const validateFields = () => {
  for (const [i, f] of fields.value.entries()) {
    if (!f.field_name) {
      ElMessage.error(t("dataBase.fieldNameRequired", { index: i + 1 }));
      return false;
    }
    if (!f.field_desc) {
      ElMessage.error(t("dataBase.fieldDescRequired", { index: i + 1 }));
      return false;
    }
    if (f.field_type === null || f.field_type === undefined) {
      ElMessage.error(t("dataBase.fieldTypeRequired", { index: i + 1 }));
      return false;
    }
  }
  return true;
};

// 提交数据（新增/编辑）
const ruleFormRef = ref<FormInstance>();
const handleSubmit = () => {
  ruleFormRef.value!.validate(async valid => {
    if (!valid) return;
    if (!validateFields()) return;
    try {
      // 合并字段到row
      // 删除row和fields中的created和modified字段
      const row = { ...drawerProps.value.row };
      if ("created" in row) delete (row as any).created;
      if ("modified" in row) delete (row as any).modified;
      if ("deleted" in row) delete (row as any).deleted; // 删除deleted字段，避免验证错误

      // 确保字段数据格式正确
      const processedFields = fields.value.map(field => {
        // 确保所有必需字段都存在且格式正确
        const processedField = {
          id: field.id || 0,
          field_name: String(field.field_name || ""),
          field_type: Number(field.field_type),
          field_desc: String(field.field_desc || ""),
          default: field.default_value !== undefined && field.default_value !== null ? String(field.default_value) : ""
        };

        // 验证字段数据
        if (!processedField.field_name) {
          throw new Error("字段名不能为空");
        }
        if (isNaN(processedField.field_type)) {
          throw new Error("字段类型必须为数字");
        }
        if (!processedField.field_desc) {
          throw new Error("字段描述不能为空");
        }

        return processedField;
      });

      row.field = processedFields; // 添加调试日志// 添加字段调试日志
      await drawerProps.value.api!(row);
      ElMessage.success({ message: t(`dataBase.${drawerProps.value.title}Success`) });
      drawerProps.value.getTableList!();
      drawerVisible.value = false;
    } catch {}
  });
};
</script>

<style scoped>
.delete-icon-large {
  font-size: 24px;
  font-weight: bold;
  color: #f56c6c;
}
.index-icon-large {
  font-size: 22px;
  font-weight: bold;
}
</style>
