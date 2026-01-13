<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="30%" :title="`${drawerProps.row?.name} - 按钮权限`">
    <!-- 超级管理员提示 -->
    <div v-if="isSuperAdmin" class="super-admin-hint">
      <el-alert title="超级管理员权限" type="info" :closable="false" show-icon>
        <template #default>
          <p>该角色为超级管理员，拥有所有按钮权限，无需手动设置。</p>
        </template>
      </el-alert>
    </div>

    <div class="button-permission-container">
      <!-- 操作按钮 -->
      <div v-if="!isSuperAdmin" class="permission-actions">
        <el-button type="primary" size="small" @click="selectAllButtons">全选按钮</el-button>
        <el-button size="small" @click="unselectAllButtons">全不选</el-button>
        <el-button size="small" @click="testMenuSelection">测试菜单选择</el-button>
        <el-button size="small" @click="debugButtonStates">调试状态</el-button>
        <el-tag type="info" size="small"> 已选择 {{ selectedButtonIds.length }} 个按钮权限 </el-tag>
      </div>

      <!-- 超级管理员显示所有按钮（只读） -->
      <div v-if="isSuperAdmin" class="super-admin-actions">
        <el-tag type="success" size="small">拥有所有按钮权限</el-tag>
        <el-tag type="info" size="small">共 {{ allButtonCount }} 个按钮权限</el-tag>
      </div>

      <el-tree
        ref="treeRef"
        :data="menuTreeData"
        :props="treeProps"
        node-key="id"
        :show-checkbox="!isSuperAdmin"
        :default-checked-keys="isSuperAdmin ? allButtonKeys : checkedKeys"
        @check="handleCheck"
        @check-change="handleCheckChange"
        @node-click="handleNodeClick"
        class="permission-tree"
      >
        <template #default="{ data }">
          <div class="tree-node" :class="{ 'button-node': data.isButton }">
            <div class="node-content">
              <el-icon v-if="data.meta?.icon" class="menu-icon" :class="{ 'button-icon': data.isButton }">
                <component :is="data.meta.icon" />
              </el-icon>
              <span class="menu-name" :class="{ 'button-name': data.isButton }">{{ data.meta?.title || data.name }}</span>
              <el-tag v-if="data.hasButtons && !data.isButton" size="small" type="info">
                {{ isSuperAdmin ? data.totalButtons : data.assignedButtons }}/{{ data.totalButtons }} 个按钮
              </el-tag>
              <el-tag v-if="isSuperAdmin && data.isButton" type="success" size="small">已授权</el-tag>
              <span v-if="data.isButton && data.explain" class="button-desc">({{ data.explain }})</span>
            </div>
          </div>
        </template>
      </el-tree>
    </div>

    <template #footer>
      <el-button @click="drawerVisible = false">关闭</el-button>
      <el-button v-if="!isSuperAdmin" type="primary" @click="handleSave">保存</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts" name="RoleButtonDrawer">
import { ref, computed } from "vue";
import { System } from "@/api/interface";
import { useHandleData } from "@/hooks/useHandleData";
import { getRoleButtons, setRoleButtonPermissions } from "@/api/modules/system";
import { ElMessage } from "element-plus";
import { useI18n } from "vue-i18n";

interface DrawerProps {
  row: Partial<System.Role>;
}

// 使用System.MenuNode接口

const { t } = useI18n();

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  row: {}
});

const treeRef = ref();
const menuTreeData = ref<System.MenuNode[]>([]);
const selectedButtonIds = ref<number[]>([]);

// 判断是否为超级管理员
const isSuperAdmin = computed(() => {
  return drawerProps.value.row?.id === 1;
});

// 超级管理员的所有按钮keys
const allButtonKeys = computed(() => {
  const keys: string[] = [];
  const collectAllButtonKeys = (menus: System.MenuNode[]) => {
    menus.forEach(menu => {
      if (menu.isButton) {
        keys.push(menu.id);
      }
      if (menu.children) {
        collectAllButtonKeys(menu.children);
      }
    });
  };
  collectAllButtonKeys(menuTreeData.value);
  return keys;
});

// 超级管理员的按钮总数
const allButtonCount = computed(() => {
  let count = 0;
  const countButtons = (menus: System.MenuNode[]) => {
    menus.forEach(menu => {
      if (menu.isButton) {
        count++;
      }
      if (menu.children) {
        countButtons(menu.children);
      }
    });
  };
  countButtons(menuTreeData.value);
  return count;
});

// 树形组件配置
const treeProps = {
  children: "children",
  label: "name"
};

// 计算已选中的节点keys
const checkedKeys = computed(() => {
  const keys: string[] = [];

  // 递归收集所有选中的节点ID
  const collectCheckedKeys = (menus: System.MenuNode[]) => {
    menus.forEach(menu => {
      // 如果当前节点是按钮且已选中，添加其ID
      if (menu.isButton && menu.buttonId && menu.assigned) {
        keys.push(menu.id);
      }

      // 如果当前节点是菜单且已选中，添加其ID
      if (!menu.isButton && menu.assigned) {
        keys.push(menu.id);
      }

      // 递归处理子节点
      if (menu.children) {
        collectCheckedKeys(menu.children);
      }
    });
  };

  collectCheckedKeys(menuTreeData.value);
  return keys;
});

// 接收父组件传过来的参数
const acceptParams = async (params: DrawerProps) => {
  drawerProps.value = params;
  drawerVisible.value = true;

  // 加载按钮数据
  await loadButtonData();
};

// 加载按钮数据
const loadButtonData = async () => {
  try {
    const response = await getRoleButtons({ roleId: drawerProps.value.row.id! });
    menuTreeData.value = response.data || [];

    // 收集所有已分配的按钮ID
    selectedButtonIds.value = [];
    collectAssignedButtons(menuTreeData.value);

    // 根据收集到的按钮ID更新按钮的assigned状态
    updateButtonAssignedStatus(menuTreeData.value);

    // 更新菜单的按钮统计
    updateMenuButtonStats(menuTreeData.value);
  } catch (error) {
    console.error("加载按钮数据失败:", error);
    ElMessage.error("加载按钮数据失败");
  }
};

// 递归收集已分配的按钮ID
const collectAssignedButtons = (menus: System.MenuNode[]) => {
  menus.forEach(menu => {
    // 如果当前节点是按钮且已选中，添加到列表中
    if (menu.isButton && menu.buttonId && menu.assigned) {
      if (!selectedButtonIds.value.includes(menu.buttonId)) {
        selectedButtonIds.value.push(menu.buttonId);
      }
    }

    // 处理子节点
    if (menu.children) {
      menu.children.forEach(child => {
        if (child.isButton && child.buttonId && child.assigned) {
          if (!selectedButtonIds.value.includes(child.buttonId)) {
            selectedButtonIds.value.push(child.buttonId);
          }
        }
        // 递归处理子节点
        if (child.children) {
          collectAssignedButtons(child.children);
        }
      });
    }
  });
};

// 根据selectedButtonIds更新按钮的assigned状态
const updateButtonAssignedStatus = (menus: System.MenuNode[]) => {
  menus.forEach(menu => {
    // 如果当前节点是按钮，根据selectedButtonIds更新assigned状态
    if (menu.isButton && menu.buttonId) {
      menu.assigned = selectedButtonIds.value.includes(menu.buttonId);
    }

    // 递归处理子节点
    if (menu.children) {
      updateButtonAssignedStatus(menu.children);
    }
  });
};

// 处理树节点选中事件
const handleCheck = (data: System.MenuNode, checked: any) => {
  // Element Plus 树形组件的 @check 事件参数结构
  // checked 包含 { checked, checkedKeys, halfChecked, halfCheckedKeys }
  const isChecked = checked.checked;

  // 如果 isChecked 是 undefined，跳过处理
  if (isChecked === undefined) {
    return;
  }

  // 处理菜单选中逻辑
  handleMenuSelection(data, isChecked);

  // 如果是选中状态，需要同时选中所有子菜单
  if (isChecked) {
    selectAllChildren(data);
  } else {
    // 如果是取消选中状态，需要同时取消选中所有子菜单
    unselectAllChildren(data);
  }
};

// 处理节点点击事件
const handleNodeClick = () => {
  // 这里可以添加点击节点的逻辑，比如展开/收起
};

// 处理节点选中状态变化事件
const handleCheckChange = (data: System.MenuNode, checked: boolean) => {
  // 找到对应的菜单节点并处理选中逻辑
  const findAndHandleMenu = (menus: System.MenuNode[], targetId: string) => {
    for (const menu of menus) {
      if (menu.id === targetId) {
        handleMenuSelection(menu, checked);

        // 如果是选中状态，需要同时选中所有子菜单
        if (checked) {
          selectAllChildren(menu);
        } else {
          // 如果是取消选中状态，需要同时取消选中所有子菜单
          unselectAllChildren(menu);
        }
        return true;
      }
      if (menu.children && menu.children.length > 0) {
        if (findAndHandleMenu(menu.children, targetId)) {
          return true;
        }
      }
    }
    return false;
  };

  findAndHandleMenu(menuTreeData.value, data.id);
};

// 选中所有子菜单
const selectAllChildren = (menu: System.MenuNode) => {
  if (menu.children && menu.children.length > 0) {
    menu.children.forEach(child => {
      handleMenuSelection(child, true);
      // 递归处理子菜单的子菜单
      selectAllChildren(child);
    });
  }
};

// 取消选中所有子菜单
const unselectAllChildren = (menu: System.MenuNode) => {
  if (menu.children && menu.children.length > 0) {
    menu.children.forEach(child => {
      handleMenuSelection(child, false);
      // 递归处理子菜单的子菜单
      unselectAllChildren(child);
    });
  }
};

// 处理菜单选中逻辑
const handleMenuSelection = (data: System.MenuNode, isChecked: boolean) => {
  // 如果 isChecked 是 undefined，跳过处理
  if (isChecked === undefined) {
    return;
  }

  // 如果是按钮节点，直接处理按钮选中
  if (data.isButton && data.buttonId) {
    data.assigned = isChecked;

    if (isChecked) {
      if (!selectedButtonIds.value.includes(data.buttonId)) {
        selectedButtonIds.value.push(data.buttonId);
      }
    } else {
      const index = selectedButtonIds.value.indexOf(data.buttonId);
      if (index > -1) {
        selectedButtonIds.value.splice(index, 1);
      }
    }

    // 更新父菜单的按钮统计
    updateMenuButtonStats(menuTreeData.value);
    return;
  }

  // 处理菜单节点
  if (data.children && data.children.length > 0) {
    data.children.forEach(child => {
      handleMenuSelection(child, isChecked);
    });
  } else {
  }
};

// 全选所有按钮
const selectAllButtons = () => {
  selectedButtonIds.value = [];
  selectAllButtonsRecursive(menuTreeData.value, true);
  updateMenuButtonStats(menuTreeData.value);
};

// 全不选所有按钮
const unselectAllButtons = () => {
  selectedButtonIds.value = [];
  selectAllButtonsRecursive(menuTreeData.value, false);
  updateMenuButtonStats(menuTreeData.value);
};

// 递归选择/取消选择所有按钮
const selectAllButtonsRecursive = (menus: System.MenuNode[], selected: boolean) => {
  menus.forEach(menu => {
    if (menu.children && menu.children.length > 0) {
      menu.children.forEach(child => {
        if (child.isButton && child.buttonId) {
          child.assigned = selected;
          if (selected && !selectedButtonIds.value.includes(child.buttonId)) {
            selectedButtonIds.value.push(child.buttonId);
          } else if (!selected) {
            const index = selectedButtonIds.value.indexOf(child.buttonId);
            if (index > -1) {
              selectedButtonIds.value.splice(index, 1);
            }
          }
        }

        // 递归处理子菜单
        if (child.children && child.children.length > 0) {
          selectAllButtonsRecursive(child.children, selected);
        }
      });
    }
  });
};

// 测试菜单选择功能
const testMenuSelection = () => {
  // 测试选择第一个菜单的所有按钮
  if (menuTreeData.value.length > 0) {
    const firstMenu = menuTreeData.value[0];

    handleMenuSelection(firstMenu, true);
  }
};

// 调试函数：检查所有按钮的选中状态
const debugButtonStates = () => {
  const checkButtons = (menus: System.MenuNode[]) => {
    menus.forEach(menu => {
      if (menu.isButton && menu.buttonId) {
        // 按钮已处理
      }

      if (menu.children) {
        checkButtons(menu.children, level + 1);
      }
    });
  };

  checkButtons(menuTreeData.value);
};

// 更新菜单的按钮统计
const updateMenuButtonStats = (menus: System.MenuNode[]) => {
  menus.forEach(menu => {
    if (menu.children) {
      // 统计子节点中的按钮
      const buttonChildren = menu.children.filter(child => child.isButton);
      menu.assignedButtons = buttonChildren.filter(btn => btn.assigned).length;
      menu.totalButtons = buttonChildren.length;
      menu.hasButtons = buttonChildren.length > 0;

      // 递归处理子菜单
      updateMenuButtonStats(menu.children);
    }
  });
};

// 保存按钮权限
const handleSave = async () => {
  // 重新收集一次按钮ID，确保数据是最新的
  selectedButtonIds.value = [];
  collectAssignedButtons(menuTreeData.value);

  // 根据收集到的按钮ID更新按钮的assigned状态
  updateButtonAssignedStatus(menuTreeData.value);

  try {
    await useHandleData(
      setRoleButtonPermissions,
      {
        roleId: drawerProps.value.row.id,
        buttonIds: selectedButtonIds.value
      },
      "保存按钮权限",
      "warning",
      t
    );

    drawerVisible.value = false;
  } catch (error) {
    console.error("保存按钮权限失败:", error);
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

.button-permission-container {
  padding: 16px 0;
}

.permission-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.super-admin-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f0f9ff;
  border-radius: 6px;
  border: 1px solid #bae6fd;
}

.permission-tree {
  max-height: 500px;
  overflow-y: auto;
}

.tree-node {
  width: 100%;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.menu-icon {
  font-size: 16px;
  color: #409eff;
}

.menu-name {
  font-weight: 500;
  color: #303133;
}

.button-node {
  margin-left: 20px;
}

.button-icon {
  color: #909399;
  font-size: 14px;
}

.button-name {
  font-weight: 400;
  color: #606266;
  font-size: 14px;
}

.button-desc {
  font-size: 12px;
  color: #909399;
  margin-left: 4px;
}

.button-list {
  margin-left: 24px;
  margin-top: 8px;
  padding: 8px 0;
  border-left: 2px solid #f0f0f0;
  padding-left: 12px;
}

.button-checkbox {
  display: block;
  margin: 4px 0;
  padding: 2px 0;
}

.button-checkbox :deep(.el-checkbox__label) {
  display: flex;
  align-items: center;
  gap: 4px;
}

.button-name {
  font-weight: 400;
  color: #606266;
}

.button-desc {
  font-size: 12px;
  color: #909399;
}

/* 树形组件样式优化 */
.permission-tree :deep(.el-tree-node__content) {
  height: auto;
  min-height: 32px;
  padding: 4px 0;
}

.permission-tree :deep(.el-tree-node__expand-icon) {
  margin-right: 8px;
}

.permission-tree :deep(.el-tree-node__label) {
  width: 100%;
}
</style>
