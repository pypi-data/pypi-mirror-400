<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="15%" :title="`${drawerProps.row?.name} - 菜单权限`">
    <!-- 超级管理员提示 -->
    <div v-if="isSuperAdmin" class="super-admin-hint">
      <el-alert title="超级管理员权限" type="info" :closable="false" show-icon>
        <template #default>
          <p>该角色为超级管理员，拥有所有菜单权限，无需手动设置。</p>
        </template>
      </el-alert>
    </div>

    <el-tree
      v-if="!isSuperAdmin"
      ref="menuTreeRef"
      :data="menuList"
      :props="treeProps"
      show-checkbox
      node-key="id"
      :default-checked-keys="checkedKeys"
      :check-strictly="false"
      @check="handleCheck"
      @check-change="handleCheckChange"
    >
      <template #default="{ data }">
        <div class="menu-node" :class="{ 'disabled-node': data.id === '1' }">
          <el-icon v-if="data.meta?.icon" class="menu-icon">
            <component :is="data.meta.icon" />
          </el-icon>
          <span class="menu-title">{{ data.meta?.title || data.name }}</span>
          <el-tag v-if="data.id === '1'" type="warning" size="small">默认权限</el-tag>
        </div>
      </template>
    </el-tree>

    <!-- 超级管理员显示所有菜单（只读） -->
    <el-tree
      v-else
      :data="menuList"
      :props="treeProps"
      node-key="id"
      :default-checked-keys="allMenuKeys"
      :check-strictly="false"
      :show-checkbox="false"
    >
      <template #default="{ data }">
        <div class="menu-node">
          <el-icon v-if="data.meta?.icon" class="menu-icon">
            <component :is="data.meta.icon" />
          </el-icon>
          <span class="menu-title">{{ data.meta?.title || data.name }}</span>
          <el-tag type="success" size="small">已授权</el-tag>
        </div>
      </template>
    </el-tree>

    <template #footer>
      <el-button @click="drawerVisible = false">关闭</el-button>
      <el-button v-if="!isSuperAdmin" type="primary" @click="handleSave">保存</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts" name="RoleMenuDrawer">
import { ref, computed } from "vue";
import { System } from "@/api/interface";
import { useHandleData } from "@/hooks/useHandleData";
import { getRoleMenus, setRoleMenuPermissions } from "@/api/modules/system";
import { ElMessage } from "element-plus";
import { useI18n } from "vue-i18n";

interface DrawerProps {
  row: Partial<System.Role>;
}

const { t } = useI18n();

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  row: {}
});

const menuTreeRef = ref();
const menuList = ref<System.Menu[]>([]);
const checkedKeys = ref<string[]>([]);

// 判断是否为超级管理员
const isSuperAdmin = computed(() => {
  return drawerProps.value.row?.id === 1;
});

// 超级管理员的所有菜单keys
const allMenuKeys = computed(() => {
  const keys: string[] = [];
  const collectAllKeys = (menus: System.Menu[]) => {
    menus.forEach(menu => {
      keys.push(String(menu.id));
      if (menu.children) {
        collectAllKeys(menu.children);
      }
    });
  };
  collectAllKeys(menuList.value);
  return keys;
});

const treeProps = {
  children: "children",
  label: "name"
};

// 接收父组件传过来的参数
const acceptParams = async (params: DrawerProps) => {
  drawerProps.value = params;
  drawerVisible.value = true;

  // 加载菜单数据
  await loadMenuData();
};

// 加载菜单数据
const loadMenuData = async () => {
  try {
    const response = await getRoleMenus({ roleId: drawerProps.value.row.id! });
    menuList.value = response.data || [];

    // 设置已选中的菜单 - 只选中真正被分配的菜单，不考虑父菜单的assigned状态
    const getCheckedKeys = (menus: System.Menu[]): string[] => {
      let keys: string[] = [];
      menus.forEach(menu => {
        // 只有当菜单本身被分配时才选中，不考虑父菜单的assigned状态
        if (menu.assigned) {
          keys.push(String(menu.id));
        }
        if (menu.children) {
          keys = keys.concat(getCheckedKeys(menu.children));
        }
      });
      return keys;
    };

    checkedKeys.value = getCheckedKeys(menuList.value);

    // 确保ID为1的菜单始终被选中
    if (!checkedKeys.value.includes("1")) {
      checkedKeys.value.push("1");
    }

    // 设置树形控件的选中状态
    setTimeout(() => {
      menuTreeRef.value?.setCheckedKeys(checkedKeys.value);
    }, 100);
  } catch (error) {
    console.error("加载菜单数据失败:", error);
    ElMessage.error("加载菜单数据失败");
  }
};

// 处理树形控件选中事件
const handleCheck = () => {
  // 可以在这里处理选中逻辑
};

// 处理树形控件选中状态变化事件
const handleCheckChange = (data: any, checked: boolean) => {
  // 如果尝试取消选中ID为1的菜单，则阻止并重新选中
  if (data.id === "1" && !checked) {
    ElMessage.warning("默认权限不能取消");
    // 重新选中该节点
    setTimeout(() => {
      menuTreeRef.value?.setChecked(data.id, true, false);
    }, 0);
  }
};

// 保存菜单权限
const handleSave = async () => {
  try {
    const checkedNodes = menuTreeRef.value?.getCheckedKeys(false) || [];
    const halfCheckedNodes = menuTreeRef.value?.getHalfCheckedKeys() || [];
    let allCheckedKeys = [...checkedNodes, ...halfCheckedNodes];

    // 确保ID为1的菜单始终被包含在保存的权限中
    if (!allCheckedKeys.includes("1")) {
      allCheckedKeys.push("1");
    }

    await useHandleData(
      setRoleMenuPermissions,
      {
        roleId: drawerProps.value.row.id,
        menuIds: allCheckedKeys.map(id => Number(id))
      },
      "保存菜单权限",
      "warning",
      t
    );

    drawerVisible.value = false;
  } catch (error) {
    console.error("保存菜单权限失败:", error);
  }
};

defineExpose({
  acceptParams
});
</script>

<style scoped>
.super-admin-hint {
  margin-bottom: 16px;
}

.menu-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.menu-icon {
  font-size: 16px;
}

.menu-title {
  font-size: 14px;
}

.disabled-node {
  opacity: 0.7;
  cursor: not-allowed;
}

.disabled-node .menu-title {
  color: #909399;
}
</style>
