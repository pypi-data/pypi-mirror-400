<template>
  <div class="organization-manage">
    <el-tabs v-model="activeTab">
      <!-- 公司管理 -->
      <el-tab-pane label="公司管理" name="company" :lazy="true">
        <div class="table-box">
          <ProTable
            ref="companyTableRef"
            :title="'公司列表'"
            :columns="companyColumns"
            :request-api="getCompanyList"
            :data-callback="dataCallback"
          >
            <template #tableHeader>
              <el-button type="primary" :icon="CirclePlus" @click="openCompanyDrawer('新增')">新增公司</el-button>
            </template>
            <template #operation="scope">
              <el-button type="primary" link :icon="EditPen" @click="openCompanyDrawer('编辑', scope.row)">编辑</el-button>
              <el-button type="danger" link :icon="Delete" @click="deleteCompanyFunc(scope.row)">删除</el-button>
            </template>
          </ProTable>
          <CompanyDrawer ref="companyDrawerRef" />
        </div>
      </el-tab-pane>

      <!-- 部门管理 -->
      <el-tab-pane label="部门管理" name="department" :lazy="true">
        <div class="table-box">
          <ProTable
            ref="departmentTableRef"
            :title="'部门列表'"
            :columns="departmentColumns"
            :request-api="getDepartmentList"
            :data-callback="dataCallback"
          >
            <template #tableHeader>
              <el-button type="primary" :icon="CirclePlus" @click="openDepartmentDrawer('新增')">新增部门</el-button>
            </template>
            <template #operation="scope">
              <el-button type="primary" link :icon="EditPen" @click="openDepartmentDrawer('编辑', scope.row)">编辑</el-button>
              <el-button type="danger" link :icon="Delete" @click="deleteDepartmentFunc(scope.row)">删除</el-button>
            </template>
          </ProTable>
          <DepartmentDrawer ref="departmentDrawerRef" />
        </div>
      </el-tab-pane>

      <!-- 团队管理 -->
      <el-tab-pane label="团队管理" name="team" :lazy="true">
        <div class="table-box">
          <ProTable
            ref="teamTableRef"
            :title="'团队列表'"
            :columns="teamColumns"
            :request-api="getTeamList"
            :data-callback="dataCallback"
          >
            <template #tableHeader>
              <el-button type="primary" :icon="CirclePlus" @click="openTeamDrawer('新增')">新增团队</el-button>
            </template>
            <template #operation="scope">
              <el-button type="success" link :icon="User" @click="openTeamMemberDrawer(scope.row)">人员管理</el-button>
              <el-button type="primary" link :icon="EditPen" @click="openTeamDrawer('编辑', scope.row)">编辑</el-button>
              <el-button type="danger" link :icon="Delete" @click="deleteTeamFunc(scope.row)">删除</el-button>
            </template>
          </ProTable>
          <TeamDrawer ref="teamDrawerRef" />
          <TeamMemberDrawer ref="teamMemberDrawerRef" />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts" name="organizationManage">
import { ref, computed, watch, nextTick } from "vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import { CirclePlus, EditPen, Delete, User } from "@element-plus/icons-vue";
import ProTable from "@/components/ProTable/index.vue";
import CompanyDrawer from "./components/CompanyDrawer.vue";
import DepartmentDrawer from "./components/DepartmentDrawer.vue";
import TeamDrawer from "./components/TeamDrawer.vue";
import TeamMemberDrawer from "./components/TeamMemberDrawer.vue";
import {
  getCompanyList,
  addCompany,
  editCompany,
  deleteCompany,
  getDepartmentList,
  addDepartment,
  editDepartment,
  deleteDepartment,
  getTeamList,
  addTeam,
  editTeam,
  deleteTeam,
  getDepartmentsByCompany,
  getAllCompanies,
  type CompanyInfo,
  type DepartmentInfo,
  type TeamInfo
} from "@/api/modules/organization";
import { useHandleData } from "@/hooks/useHandleData";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const activeTab = ref("company");
const companyTableRef = ref<ProTableInstance>();
const departmentTableRef = ref<ProTableInstance>();
const teamTableRef = ref<ProTableInstance>();

const companyDrawerRef = ref<InstanceType<typeof CompanyDrawer> | null>(null);
const departmentDrawerRef = ref<InstanceType<typeof DepartmentDrawer> | null>(null);
const teamDrawerRef = ref<InstanceType<typeof TeamDrawer> | null>(null);
const teamMemberDrawerRef = ref<InstanceType<typeof TeamMemberDrawer> | null>(null);

const dataCallback = (data: any) => {
  // 确保返回正确的数据格式
  const result = {
    records: Array.isArray(data?.records) ? data.records : [],
    total: data?.total || 0
  };
  return result;
};

// 公司相关
const companyColumns = computed<ColumnProps<CompanyInfo>[]>(() => [
  { prop: "id", label: "ID", width: 80 },
  {
    prop: "name",
    label: "公司名称",
    search: { el: "input", props: { placeholder: "请输入公司名称" } }
  },
  { prop: "operation", label: "操作", fixed: "right", width: 200 }
]);

const openCompanyDrawer = (title: string, row: Partial<CompanyInfo> = {}) => {
  const params = {
    title,
    isView: title === "查看",
    row: { ...row },
    api: title === "新增" ? addCompany : title === "编辑" ? editCompany : undefined,
    getTableList: companyTableRef.value?.getTableList
  };
  companyDrawerRef.value?.acceptParams(params);
};

const deleteCompanyFunc = async (row: CompanyInfo) => {
  await useHandleData(deleteCompany, { id: row.id! }, `确定删除公司"${row.name}"吗？`, "warning", t);
  companyTableRef.value?.getTableList();
};

// 部门相关
const departmentColumns = computed<ColumnProps<DepartmentInfo>[]>(() => [
  { prop: "id", label: "ID", width: 80 },
  {
    prop: "name",
    label: "部门名称",
    search: { el: "input", props: { placeholder: "请输入部门名称" } }
  },
  {
    prop: "company_name",
    label: "所属公司",
    width: 150,
    isFilterEnum: false,
    search: {
      el: "select",
      props: { filterable: true, clearable: true, placeholder: "请选择公司" },
      key: "company_id"
    },
    enum: async () => {
      try {
        const response = await getAllCompanies();
        // 确保 response.data 是数组
        const companies = Array.isArray(response.data) ? response.data : [];
        return { data: companies.map((item: any) => ({ label: item.name, value: item.id })) };
      } catch {
        return { data: [] };
      }
    }
  },
  { prop: "operation", label: "操作", fixed: "right", width: 200 }
]);

const openDepartmentDrawer = (title: string, row: Partial<DepartmentInfo> = {}) => {
  const params = {
    title,
    isView: title === "查看",
    row: { ...row },
    api: title === "新增" ? addDepartment : title === "编辑" ? editDepartment : undefined,
    getTableList: departmentTableRef.value?.getTableList
  };
  departmentDrawerRef.value?.acceptParams(params);
};

const deleteDepartmentFunc = async (row: DepartmentInfo) => {
  await useHandleData(deleteDepartment, { id: row.id! }, `确定删除部门"${row.name}"吗？`, "warning", t);
  departmentTableRef.value?.getTableList();
};

// 团队相关 - 部门选项（动态更新）
const teamDepartmentOptions = ref<{ label: string; value: number }[]>([]);

// 获取团队部门的 enum 函数
const getTeamDepartmentEnum = async () => {
  // 如果已经有缓存的选项，直接返回
  if (teamDepartmentOptions.value.length > 0) {
    return { data: teamDepartmentOptions.value };
  }
  // 否则返回空数组
  return { data: [] };
};

// 团队相关
const teamColumns = computed<ColumnProps<TeamInfo>[]>(() => [
  {
    prop: "name",
    label: "团队名称",
    search: { el: "input", props: { placeholder: "请输入团队名称" } }
  },
  {
    prop: "company_name",
    label: "所属公司",
    width: 150,
    isFilterEnum: false,
    search: {
      el: "select",
      props: { filterable: true, clearable: true, placeholder: "请选择公司" },
      key: "company_id"
    },
    enum: async () => {
      try {
        const response = await getAllCompanies();
        // 确保 response.data 是数组
        const companies = Array.isArray(response.data) ? response.data : [];
        return { data: companies.map((item: any) => ({ label: item.name, value: item.id })) };
      } catch {
        return { data: [] };
      }
    }
  },
  {
    prop: "department_name",
    label: "所属部门",
    width: 150,
    isFilterEnum: false,
    search: {
      el: "select",
      props: { filterable: true, clearable: true, placeholder: "请先选择公司" },
      key: "department_id"
    },
    enum: getTeamDepartmentEnum
  },
  { prop: "operation", label: "操作", fixed: "right", width: 250 }
]);

// 监听团队表格的搜索参数变化，实现级联选择（只在团队管理标签页激活时监听）
watch(
  () => {
    // 只在团队管理标签页激活时才监听
    if (activeTab.value !== "team") return null;
    return (teamTableRef.value as any)?.searchParam;
  },
  async newParam => {
    if (!newParam || activeTab.value !== "team") return;
    const companyId = newParam.company_id;

    // 如果选择了公司，获取该公司的部门列表
    if (companyId) {
      try {
        const response = await getDepartmentsByCompany({ company_id: companyId });
        const departments = Array.isArray(response.data) ? response.data : [];
        teamDepartmentOptions.value = departments.map((item: any) => ({
          label: item.name,
          value: item.id
        }));

        // 等待下一个 tick 确保组件已渲染
        await nextTick();

        // 更新 enumMap - 使用和 loadCompanyEnum 相同的逻辑
        const enumMapRef = (teamTableRef.value as any)?.enumMap;
        if (enumMapRef) {
          const enumMap = enumMapRef.value || enumMapRef;
          if (enumMap && enumMap instanceof Map) {
            // 先删除旧的缓存，强制重新加载
            enumMap.delete("department_name");
            // 设置新的数据
            enumMap.set("department_name", teamDepartmentOptions.value);
            // 如果是 ref，需要更新 ref 的值以触发响应式更新
            if (enumMapRef.value) {
              enumMapRef.value = new Map(enumMap);
            }
          }
        }
      } catch {
        teamDepartmentOptions.value = [];
      }
    } else {
      // 如果清空了公司选择，清空部门选项
      teamDepartmentOptions.value = [];
      // 清空部门选择
      if (newParam.department_id) {
        newParam.department_id = undefined;
      }
      // 更新 enumMap
      await nextTick();
      const enumMapRef = (teamTableRef.value as any)?.enumMap;
      if (enumMapRef) {
        const enumMap = enumMapRef.value || enumMapRef;
        if (enumMap && enumMap instanceof Map) {
          enumMap.delete("department_name");
          enumMap.set("department_name", []);
          if (enumMapRef.value) {
            enumMapRef.value = new Map(enumMap);
          }
        }
      }
    }
  },
  { deep: true }
);

const openTeamDrawer = (title: string, row: Partial<TeamInfo> = {}) => {
  const params = {
    title,
    isView: title === "查看",
    row: { ...row },
    api: title === "新增" ? addTeam : title === "编辑" ? editTeam : undefined,
    getTableList: teamTableRef.value?.getTableList
  };
  teamDrawerRef.value?.acceptParams(params);
};

const deleteTeamFunc = async (row: TeamInfo) => {
  await useHandleData(deleteTeam, { id: row.id! }, `确定删除团队"${row.name}"吗？`, "warning", t);
  teamTableRef.value?.getTableList();
};

const openTeamMemberDrawer = (row: TeamInfo) => {
  teamMemberDrawerRef.value?.acceptParams({ teamId: row.id!, teamName: row.name });
};
</script>

<style scoped lang="scss">
.organization-manage {
  .table-box {
    padding: 20px;
  }
}

// 确保表格空数据状态正确显示
:deep(.el-table) {
  .el-table__empty-block {
    width: 100% !important;
    min-height: 300px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    position: relative !important;
    left: 0 !important;
    top: 0 !important;

    .table-empty {
      line-height: 30px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 200px;
      width: 100%;

      img {
        display: block !important;
        width: 80px !important;
        height: 80px !important;
        margin-bottom: 16px;
        object-fit: contain;
      }

      div {
        color: #909399;
        font-size: 14px;
        text-align: center;
      }
    }
  }

  .el-table__empty-text {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

// 确保表格容器有足够高度
:deep(.el-table__body-wrapper) {
  min-height: 300px;

  // 当表格为空时，隐藏滚动条
  &:has(.el-table__empty-block) {
    overflow: hidden !important;
  }
}

// 确保ProTable容器有足够高度
:deep(.pro-table) {
  .table-main {
    min-height: 400px;
  }
}
</style>
