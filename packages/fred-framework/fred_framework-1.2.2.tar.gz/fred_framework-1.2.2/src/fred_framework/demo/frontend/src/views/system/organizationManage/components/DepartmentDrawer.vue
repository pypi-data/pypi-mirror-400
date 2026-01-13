<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="450px" :title="`${drawerProps.title}部门`">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps.isView"
      :model="drawerProps.row"
      :hide-required-asterisk="drawerProps.isView"
    >
      <el-form-item label="部门名称" prop="name">
        <el-input v-model="drawerProps.row.name" placeholder="请填写部门名称" clearable></el-input>
      </el-form-item>
      <el-form-item label="所属公司" prop="company_id">
        <el-select
          v-model="drawerProps.row.company_id"
          placeholder="请选择所属公司"
          clearable
          filterable
          :disabled="drawerProps.isView"
          style="width: 100%"
          @change="handleCompanyChange"
        >
          <el-option v-for="company in companyOptions" :key="company.id" :label="company.name" :value="company.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="drawerVisible = false">取消</el-button>
      <el-button v-show="!drawerProps.isView" type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, FormInstance } from "element-plus";
import type { DepartmentInfo, CompanyInfo } from "@/api/modules/organization";
import { getAllCompanies } from "@/api/modules/organization";

const rules = reactive({
  name: [{ required: true, message: "请填写部门名称", trigger: "blur" }],
  company_id: [{ required: true, message: "请选择所属公司", trigger: "change" }]
});

interface DrawerProps {
  title: string;
  isView: boolean;
  row: DepartmentInfo;
  api?: (params: any) => Promise<any>;
  getTableList?: () => void;
}

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: { name: "", company_id: undefined }
});

const companyOptions = ref<CompanyInfo[]>([]);

const fetchCompanies = async () => {
  try {
    const response = await getAllCompanies();
    companyOptions.value = response.data || [];
  } catch {
    companyOptions.value = [];
  }
};

const handleCompanyChange = () => {
  // 公司变更时的处理逻辑
};

const acceptParams = (params: DrawerProps) => {
  drawerProps.value = params;
  // 新增时，确保company_id为undefined，不显示0
  if (params.title === "新增" && !drawerProps.value.row.company_id) {
    drawerProps.value.row.company_id = undefined;
  }
  // 编辑时，如果company_id为0，也设置为undefined
  if (drawerProps.value.row.company_id === 0) {
    drawerProps.value.row.company_id = undefined;
  }
  drawerVisible.value = true;
  fetchCompanies();
};

const ruleFormRef = ref<FormInstance>();
const handleSubmit = () => {
  ruleFormRef.value!.validate(async valid => {
    if (!valid) return;
    try {
      // 确保提交的数据中company_id是有效的数字
      const submitData = {
        ...drawerProps.value.row,
        company_id: drawerProps.value.row.company_id
      };
      await drawerProps.value.api!(submitData);
      ElMessage.success({ message: `${drawerProps.value.title}部门成功！` });
      if (drawerProps.value.getTableList) {
        drawerProps.value.getTableList();
      }
      drawerVisible.value = false;
    } catch {
      // 静默处理错误
    }
  });
};

onMounted(() => {
  fetchCompanies();
});

defineExpose({
  acceptParams
});
</script>
