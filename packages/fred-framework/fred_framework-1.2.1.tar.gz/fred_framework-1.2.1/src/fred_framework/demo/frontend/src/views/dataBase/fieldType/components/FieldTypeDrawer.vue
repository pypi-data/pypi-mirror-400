<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="500px" :title="drawerTitle">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps.isView"
      :model="drawerProps.row"
      :hide-required-asterisk="drawerProps.isView"
    >
      <el-form-item :label="t('dataBase.fieldType', '字段类型')" prop="field_type">
        <el-input
          v-model="drawerProps.row!.field_type"
          :placeholder="t('dataBase.inputType', '请输入字段类型')"
          clearable
        ></el-input>
      </el-form-item>
      <el-form-item :label="t('dataBase.remark', '备注')" prop="desc">
        <el-input
          v-model="drawerProps.row!.desc"
          type="textarea"
          :placeholder="t('dataBase.inputDesc', '请输入备注')"
          clearable
        ></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="drawerVisible = false">{{ t("dataBase.cancel", "取消") }}</el-button>
      <el-button v-show="!drawerProps.isView" type="primary" @click="handleSubmit">{{ t("dataBase.confirm", "确定") }}</el-button>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, reactive, computed } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage, FormInstance } from "element-plus";

const { t, locale } = useI18n();

const rules = reactive({
  field_type: [{ required: true, message: t("dataBase.inputType", "请输入字段类型") }],
  desc: [{ required: true, message: t("dataBase.inputDesc", "请输入备注") }]
});

interface DrawerProps {
  title: string;
  isView: boolean;
  row: Partial<{ id: number; field_type: string; desc: string }>;
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
  void locale.value;
  return t(`dataBase.${drawerProps.value.title}`, drawerProps.value.title) + t("dataBase.fieldType", "字段类型");
});

// 接收父组件传过来的参数
const acceptParams = (params: DrawerProps) => {
  drawerProps.value = params;
  drawerVisible.value = true;
};

// 提交数据（新增/编辑）
const ruleFormRef = ref<FormInstance>();
const handleSubmit = () => {
  ruleFormRef.value!.validate(async valid => {
    if (!valid) return;
    try {
      await drawerProps.value.api!(drawerProps.value.row);
      ElMessage.success({ message: t(`dataBase.${drawerProps.value.title}Success`, `${drawerProps.value.title}成功`) });
      drawerProps.value.getTableList!();
      drawerVisible.value = false;
    } catch {}
  });
};

defineExpose({
  acceptParams
});
</script>
