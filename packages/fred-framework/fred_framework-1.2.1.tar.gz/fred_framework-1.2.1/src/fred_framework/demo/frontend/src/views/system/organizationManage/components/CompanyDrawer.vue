<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="450px" :title="`${drawerProps.title}公司`">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps.isView"
      :model="drawerProps.row"
      :hide-required-asterisk="drawerProps.isView"
    >
      <el-form-item label="公司名称" prop="name">
        <el-input v-model="drawerProps.row.name" placeholder="请填写公司名称" clearable></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="drawerVisible = false">取消</el-button>
      <el-button v-show="!drawerProps.isView" type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { ElMessage, FormInstance } from "element-plus";
import type { CompanyInfo } from "@/api/modules/organization";

const rules = reactive({
  name: [{ required: true, message: "请填写公司名称", trigger: "blur" }]
});

interface DrawerProps {
  title: string;
  isView: boolean;
  row: CompanyInfo;
  api?: (params: any) => Promise<any>;
  getTableList?: () => void;
}

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: { name: "" }
});

const acceptParams = (params: DrawerProps) => {
  drawerProps.value = params;
  drawerVisible.value = true;
};

const ruleFormRef = ref<FormInstance>();
const handleSubmit = () => {
  ruleFormRef.value!.validate(async valid => {
    if (!valid) return;
    try {
      await drawerProps.value.api!(drawerProps.value.row);
      ElMessage.success({ message: `${drawerProps.value.title}公司成功！` });
      if (drawerProps.value.getTableList) {
        drawerProps.value.getTableList();
      }
      drawerVisible.value = false;
    } catch {
      // 静默处理错误
    }
  });
};

defineExpose({
  acceptParams
});
</script>
