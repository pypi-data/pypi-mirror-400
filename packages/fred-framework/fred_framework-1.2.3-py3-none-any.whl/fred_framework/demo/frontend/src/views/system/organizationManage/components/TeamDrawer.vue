<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="450px" :title="`${drawerProps.title}团队`">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps.isView"
      :model="drawerProps.row"
      :hide-required-asterisk="drawerProps.isView"
    >
      <el-form-item label="团队名称" prop="name">
        <el-input v-model="drawerProps.row.name" placeholder="请填写团队名称" clearable></el-input>
      </el-form-item>
      <el-form-item label="所属公司" prop="company_id">
        <el-select
          v-model="selectedCompanyId"
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
      <el-form-item label="所属部门" prop="department_id">
        <el-select
          v-model="drawerProps.row.department_id"
          placeholder="请先选择公司，再选择部门"
          clearable
          filterable
          :disabled="drawerProps.isView || !selectedCompanyId"
          style="width: 100%"
        >
          <el-option
            v-for="department in departmentOptions"
            :key="department.id"
            :label="department.name"
            :value="department.id"
          />
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
import type { TeamInfo, CompanyInfo, DepartmentInfo } from "@/api/modules/organization";
import { getAllCompanies, getDepartmentsByCompany } from "@/api/modules/organization";

const rules = reactive({
  name: [{ required: true, message: "请填写团队名称", trigger: "blur" }],
  department_id: [{ required: true, message: "请选择所属部门", trigger: "change" }]
});

interface DrawerProps {
  title: string;
  isView: boolean;
  row: TeamInfo;
  api?: (params: any) => Promise<any>;
  getTableList?: () => void;
}

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: { name: "", department_id: undefined }
});

const companyOptions = ref<CompanyInfo[]>([]);
const departmentOptions = ref<DepartmentInfo[]>([]);
const selectedCompanyId = ref<number | undefined>(undefined);

const fetchCompanies = async () => {
  try {
    const response = await getAllCompanies();
    companyOptions.value = response.data || [];
  } catch {
    companyOptions.value = [];
  }
};

const fetchDepartments = async (companyId: number) => {
  try {
    const response = await getDepartmentsByCompany({ company_id: companyId });
    departmentOptions.value = response.data || [];
  } catch {
    departmentOptions.value = [];
  }
};

const handleCompanyChange = (companyId: number | undefined) => {
  if (companyId) {
    fetchDepartments(companyId);
    // 清空部门选择
    drawerProps.value.row.department_id = undefined;
  } else {
    departmentOptions.value = [];
    drawerProps.value.row.department_id = undefined;
  }
};

const acceptParams = (params: DrawerProps) => {
  drawerProps.value = params;
  // 新增时，确保department_id为undefined，不显示0
  if (params.title === "新增") {
    drawerProps.value.row.department_id = undefined;
    selectedCompanyId.value = undefined;
    departmentOptions.value = [];
  } else {
    // 编辑时，如果department_id为0，也设置为undefined
    if (drawerProps.value.row.department_id === 0) {
      drawerProps.value.row.department_id = undefined;
    }
    // 如果是编辑模式，根据部门ID反查公司ID
    if (drawerProps.value.row.department_id && drawerProps.value.row.company_id) {
      selectedCompanyId.value = drawerProps.value.row.company_id;
      fetchDepartments(drawerProps.value.row.company_id);
    } else {
      selectedCompanyId.value = undefined;
      departmentOptions.value = [];
    }
  }

  drawerVisible.value = true;
  fetchCompanies();
};

const ruleFormRef = ref<FormInstance>();
const handleSubmit = () => {
  ruleFormRef.value!.validate(async valid => {
    if (!valid) return;
    try {
      await drawerProps.value.api!(drawerProps.value.row);
      ElMessage.success({ message: `${drawerProps.value.title}团队成功！` });
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
