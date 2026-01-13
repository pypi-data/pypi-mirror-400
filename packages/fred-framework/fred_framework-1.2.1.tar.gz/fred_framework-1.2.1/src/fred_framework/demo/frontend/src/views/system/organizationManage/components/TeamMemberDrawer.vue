<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="50%" :title="`${teamName} - 人员管理`">
    <div class="team-member-drawer">
      <!-- 添加人员区域 -->
      <div class="add-member-section">
        <el-form :inline="true" class="add-member-form">
          <el-form-item label="选择人员">
            <el-select
              v-model="selectedAdminIds"
              placeholder="请选择要添加的管理员"
              clearable
              filterable
              multiple
              style="width: 400px"
              @change="handleAdminSelectChange"
            >
              <el-option v-for="admin in availableAdmins" :key="admin.id" :label="admin.username" :value="admin.id" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :disabled="!selectedAdminIds.length" @click="addMembers">添加人员</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 人员列表 -->
      <ProTable
        ref="proTable"
        :columns="columns"
        :request-api="getTableList"
        :init-param="initParam"
        :data-callback="dataCallback"
        row-key="id"
        :tool-button="false"
        :pagination="true"
      >
        <template #tableHeader>
          <div class="member-count">当前团队人员：{{ memberCount }} 人</div>
        </template>
        <!-- 头像 -->
        <template #avatar="scope">
          <el-avatar v-if="scope.row.avatar" :src="scope.row.avatar" :size="40" />
          <el-avatar v-else :size="40">
            <span>{{ scope.row.username?.charAt(0)?.toUpperCase() || "U" }}</span>
          </el-avatar>
        </template>
        <!-- 角色 -->
        <template #is_manager="scope">
          <el-select
            :model-value="scope.row.is_manager"
            size="small"
            style="width: 120px"
            @change="val => handleManagerChange(scope.row, val)"
          >
            <el-option label="普通成员" :value="0" />
            <el-option label="公司管理员" :value="1" />
            <el-option label="部门管理" :value="2" />
            <el-option label="团队管理" :value="3" />
          </el-select>
        </template>
        <!-- 操作 -->
        <template #operation="scope">
          <el-button type="danger" link :icon="Delete" @click="removeMember(scope.row)">移除</el-button>
        </template>
      </ProTable>
    </div>
  </el-drawer>
</template>

<script setup lang="ts" name="TeamMemberDrawer">
import { reactive, ref, computed } from "vue";
import { ElMessage } from "element-plus";
import { Delete } from "@element-plus/icons-vue";
import { useHandleData } from "@/hooks/useHandleData";
import ProTable from "@/components/ProTable/index.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import {
  getTeamMemberList,
  addTeamMembers,
  deleteTeamMember,
  getAvailableAdmins,
  updateTeamMemberManager,
  type TeamMemberInfo,
  type AvailableAdminInfo
} from "@/api/modules/organization";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

interface DrawerProps {
  teamId: number;
  teamName: string;
}

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  teamId: 0,
  teamName: ""
});

const proTable = ref<ProTableInstance>();
const initParam = reactive({ team_id: 0 });
const selectedAdminIds = ref<number[]>([]);
const availableAdmins = ref<AvailableAdminInfo[]>([]);
const memberCount = ref(0);

const dataCallback = (data: any) => {
  const result = {
    records: data.records || [],
    total: data.total || 0
  };
  memberCount.value = result.total;
  return result;
};

const getTableList = (params: any) => {
  return getTeamMemberList({ ...params, team_id: initParam.team_id });
};

// 获取可用管理员列表
const fetchAvailableAdmins = async () => {
  if (!initParam.team_id) return;
  try {
    const response = await getAvailableAdmins({ team_id: initParam.team_id });
    availableAdmins.value = response.data || [];
  } catch {
    availableAdmins.value = [];
  }
};

const handleAdminSelectChange = () => {
  // 选择变化时的处理
};

const addMembers = async () => {
  if (!selectedAdminIds.value.length) {
    ElMessage.warning("请选择要添加的管理员");
    return;
  }

  try {
    await addTeamMembers({
      team_id: initParam.team_id,
      admin_ids: selectedAdminIds.value
    });
    ElMessage.success("添加成功");
    selectedAdminIds.value = [];
    proTable.value?.getTableList();
    fetchAvailableAdmins();
  } catch {
    // 静默处理错误
  }
};

const removeMember = async (row: TeamMemberInfo) => {
  await useHandleData(
    deleteTeamMember,
    { team_id: initParam.team_id, admin_id: row.admin_id },
    `确定移除"${row.username}"吗？`,
    "warning",
    t
  );
  proTable.value?.getTableList();
  fetchAvailableAdmins();
};

const handleManagerChange = async (row: TeamMemberInfo, isManager: number) => {
  try {
    await updateTeamMemberManager({
      team_id: initParam.team_id,
      admin_id: row.admin_id,
      is_manager: isManager
    });
    const managerLabels: Record<number, string> = {
      0: "普通成员",
      1: "公司管理员",
      2: "部门管理",
      3: "团队管理"
    };
    ElMessage.success(`已设置为${managerLabels[isManager] || "普通成员"}`);
    proTable.value?.getTableList();
  } catch {
    // 恢复原值
    proTable.value?.getTableList();
  }
};

const columns = computed<ColumnProps<TeamMemberInfo>[]>(() => [
  { prop: "id", label: "ID", width: 80 },
  {
    prop: "avatar",
    label: "头像",
    width: 100
  },
  {
    prop: "username",
    label: "用户名"
  },
  {
    prop: "is_manager",
    label: "角色",
    width: 150
  },
  { prop: "operation", label: "操作", fixed: "right", width: 120 }
]);

const acceptParams = (params: DrawerProps) => {
  drawerProps.value = params;
  initParam.team_id = params.teamId;
  drawerVisible.value = true;
  selectedAdminIds.value = [];
  fetchAvailableAdmins();
  // 延迟刷新表格，确保initParam已更新
  setTimeout(() => {
    proTable.value?.getTableList();
  }, 100);
};

defineExpose({
  acceptParams
});
</script>

<style scoped lang="scss">
.team-member-drawer {
  .add-member-section {
    margin-bottom: 20px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 4px;

    .add-member-form {
      margin: 0;
    }
  }

  .member-count {
    font-size: 14px;
    color: #606266;
    font-weight: 500;
  }
}
</style>
