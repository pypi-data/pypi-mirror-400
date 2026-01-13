<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="450px" :title="`${drawerProps.title}配置`">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps.isView"
      :model="drawerProps.row"
      :hide-required-asterisk="drawerProps.isView"
    >
      <el-form-item :label="t('config.name')" prop="name">
        <el-input
          v-model="drawerProps.row!.name"
          :placeholder="t('config.inputName')"
          clearable
          :disabled="drawerProps.isView"
        ></el-input>
      </el-form-item>
      <el-form-item :label="t('config.value')" prop="value">
        <el-input
          v-model="drawerProps.row!.value"
          :placeholder="t('config.inputValue')"
          clearable
          :disabled="drawerProps.isView"
        ></el-input>
      </el-form-item>
      <el-form-item :label="t('config.desc')" prop="desc">
        <el-input
          v-model="drawerProps.row!.desc"
          type="textarea"
          :rows="4"
          :placeholder="t('config.inputDesc')"
          clearable
          :disabled="drawerProps.isView"
        ></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="drawerVisible = false">{{ t("common.cancel") }}</el-button>
      <el-button v-show="!drawerProps.isView" type="primary" @click="handleSubmit">{{ t("common.confirm") }}</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts" name="ConfigDrawer">
import { ref, reactive } from "vue";
import { ElMessage, FormInstance } from "element-plus";
import { SystemConfig } from "@/api/model/systemModel";
import { useI18n } from "vue-i18n";

// 国际化
const { t } = useI18n();

const rules = reactive({
  name: [{ required: true, message: t("config.nameRequired") }],
  value: [{ required: true, message: t("config.valueRequired") }]
});

interface DrawerProps {
  title: string;
  isView: boolean;
  row: Partial<SystemConfig>;
  api?: (params: any) => Promise<any>;
  getTableList?: () => void;
}

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: {}
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
      const submitData = {
        id: drawerProps.value.row!.id || 0,
        name: drawerProps.value.row!.name,
        value: drawerProps.value.row!.value,
        desc: drawerProps.value.row!.desc || ""
      };
      await drawerProps.value.api!(submitData);

      ElMessage.success({ message: t("config.operateSuccess", { message: drawerProps.value.title }) });
      drawerProps.value.getTableList!();
      drawerVisible.value = false;
    } catch {}
  });
};

defineExpose({
  acceptParams
});
</script>
