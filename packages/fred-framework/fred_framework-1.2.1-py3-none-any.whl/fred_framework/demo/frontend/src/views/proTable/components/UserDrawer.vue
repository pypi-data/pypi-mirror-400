<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="450px" :title="`${drawerProps.title}用户`">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps.isView"
      :model="drawerProps.row"
      :hide-required-asterisk="drawerProps.isView"
    >
      <el-form-item :label="t('user.userAvatar')" prop="avatar">
        <UploadImg v-model:image-url="avatar" width="135px" height="135px" :file-size="3">
          <template #empty>
            <el-icon><Avatar /></el-icon>
            <span>{{ t("user.uploadAvatar") }}</span>
          </template>
          <template #tip> {{ t("user.avatarSizeLimit") }} </template>
        </UploadImg>
      </el-form-item>
      <el-form-item :label="t('user.userName')" prop="username">
        <el-input v-model="drawerProps.row!.username" :placeholder="t('user.enterUserName')" clearable></el-input>
      </el-form-item>
      <el-form-item :label="t('user.phoneNumber')" prop="username">
        <el-input v-model="drawerProps.row!.phone" :disabled="drawerProps.title !== '新增'" clearable></el-input>
      </el-form-item>
      <el-form-item :label="t('user.userRole')" prop="roleIds">
        <el-select
          v-model="selectedRoleIds"
          multiple
          :placeholder="t('user.selectRole')"
          style="width: 100%"
          :disabled="drawerProps.isView"
          collapse-tags
          collapse-tags-tooltip
          :max-collapse-tags="2"
        >
          <el-option v-for="role in roleList" :key="role.id" :label="role.name" :value="role.id" />
        </el-select>
        <div v-if="drawerProps.isView && selectedRoleIds.length === 0" class="text-gray-400 text-sm mt-1">
          {{ t("user.noRole") }}
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="drawerVisible = false">{{ t("common.cancel") }}</el-button>
      <el-button v-show="!drawerProps.isView" type="primary" @click="handleSubmit">{{ t("common.confirm") }}</el-button>
    </template>
  </el-drawer>
</template>
<script setup lang="ts" name="UserDrawer">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, FormInstance } from "element-plus";
import { User, System } from "@/api/interface";
import UploadImg from "@/components/Upload/Img.vue";
import { useI18n } from "vue-i18n";
import { getAllRoleList, getUserRoles } from "@/api/modules/role";

// 国际化
const { t } = useI18n();

const rules = reactive({
  username: [{ required: true, message: t("user.nameRequired") }]
});

interface DrawerProps {
  title: string;
  isView: boolean;
  row: Partial<User.ResUserList>;
  api?: (params: any) => Promise<any>;
  getTableList?: () => void;
}

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: {}
});

const avatar = ref(""); // 👈 新增 ref，默认空字符串
const roleList = ref<System.RoleList[]>([]); // 角色列表
const selectedRoleIds = ref<number[]>([]); // 选中的角色ID列表

// 获取角色列表
const loadRoleList = async () => {
  try {
    const { data } = await getAllRoleList();
    roleList.value = data;
  } catch {
    console.error("获取角色列表失败:", error);
  }
};

// 获取用户角色
const loadUserRoles = async (userId: number) => {
  try {
    const { data } = await getUserRoles({ userId });

    selectedRoleIds.value = data.map(role => role.id);
  } catch {
    console.error("获取用户角色失败:", error);
  }
};

// 接收父组件传过来的参数
const acceptParams = async (params: DrawerProps) => {
  drawerProps.value = params;
  avatar.value = params.row?.avatar ?? ""; // 👈 初始化 avatar

  // 如果是编辑或查看模式，加载用户角色
  if ((params.title === "编辑" || params.title === "查看") && params.row?.id) {
    await loadUserRoles(Number(params.row.id));
  } else {
    selectedRoleIds.value = [];
  }

  drawerVisible.value = true;
};

// 提交数据（新增/编辑）
const ruleFormRef = ref<FormInstance>();
const handleSubmit = () => {
  ruleFormRef.value!.validate(async valid => {
    if (!valid) return;

    drawerProps.value.row!.avatar = avatar.value; // 👈 提交前同步回去

    try {
      // 保存用户信息（包含角色信息）
      const userData = {
        ...drawerProps.value.row,
        role_ids: selectedRoleIds.value
      };
      await drawerProps.value.api!(userData);

      ElMessage.success({ message: t("user.operateSuccess", { message: drawerProps.value.title }) });
      drawerProps.value.getTableList!();
      drawerVisible.value = false;
    } catch {}
  });
};

// 组件挂载时加载角色列表
onMounted(() => {
  loadRoleList();
});

defineExpose({
  acceptParams
});
</script>
