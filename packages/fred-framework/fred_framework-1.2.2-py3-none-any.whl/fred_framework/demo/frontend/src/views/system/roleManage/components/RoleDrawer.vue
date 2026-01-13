<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="450px" :title="`${drawerProps.title}${t('role.title')}`">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps.isView"
      :model="drawerProps.row"
      :hide-required-asterisk="drawerProps.isView"
    >
      <el-form-item :label="t('role.roleName')" prop="name">
        <el-input v-model="drawerProps.row!.name" :placeholder="t('role.enterRoleName')" clearable></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="drawerVisible = false">{{ t("common.cancel") }}</el-button>
      <el-button v-show="!drawerProps.isView" type="primary" @click="handleSubmit">{{ t("common.confirm") }}</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts" name="RoleDrawer">
import { ref, reactive } from "vue";
import { ElMessage, FormInstance } from "element-plus";
import { System } from "@/api/interface";
import { useI18n } from "vue-i18n";

// 国际化
const { t } = useI18n();

const rules = reactive({
  name: [{ required: true, message: t("role.nameRequired") }]
});

interface DrawerProps {
  title: string;
  isView: boolean;
  row: Partial<System.Role>;
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
      const params = { ...drawerProps.value.row };
      delete params.created;
      await drawerProps.value.api!(params);
      const successMessage = drawerProps.value.title === "新增" ? t("role.addSuccess") : t("role.editSuccess");
      ElMessage.success({ message: successMessage });
      drawerProps.value.getTableList!();
      drawerVisible.value = false;
    } catch {}
  });
};

defineExpose({
  acceptParams
});
</script>
