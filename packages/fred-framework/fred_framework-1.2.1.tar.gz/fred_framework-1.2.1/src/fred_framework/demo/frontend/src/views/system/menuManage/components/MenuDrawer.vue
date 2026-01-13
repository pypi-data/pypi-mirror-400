<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="450px" :title="`${drawerProps.title}菜单`">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps.isView"
      :model="drawerProps.row"
      :hide-required-asterisk="drawerProps.isView"
    >
      <el-form-item label="菜单名称" prop="meta.title">
        <el-input v-model="drawerProps.row.meta.title" placeholder="请填写菜单名称" clearable></el-input>
      </el-form-item>
      <el-form-item label="菜单图标" prop="meta.icon">
        <SelectIcon v-model:icon-value="drawerProps.row.meta.icon" />
      </el-form-item>
      <el-form-item label="菜单路径" prop="path">
        <el-input v-model="drawerProps.row.path" placeholder="请填写菜单路径" clearable></el-input>
      </el-form-item>
      <el-form-item label="组件路径" prop="component">
        <el-input v-model="drawerProps.row.component" placeholder="请填写组件路径" clearable></el-input>
      </el-form-item>
      <el-form-item label="排序" prop="sort">
        <el-input-number v-model="drawerProps.row.sort" :min="0" :max="999" placeholder="请填写排序号" />
      </el-form-item>
      <!-- 新增 meta 字段设置项 -->
      <el-form-item label="固定标签" prop="meta.isAffix">
        <el-switch v-model="drawerProps.row.meta.isAffix" active-text="是" inactive-text="否" />
      </el-form-item>
      <el-form-item label="全屏" prop="meta.isFull">
        <el-switch v-model="drawerProps.row.meta.isFull" active-text="是" inactive-text="否" />
      </el-form-item>
      <el-form-item label="隐藏" prop="meta.isHide">
        <el-switch v-model="drawerProps.row.meta.isHide" active-text="是" inactive-text="否" />
      </el-form-item>
      <el-form-item label="缓存" prop="meta.isKeepAlive">
        <el-switch v-model="drawerProps.row.meta.isKeepAlive" active-text="是" inactive-text="否" />
      </el-form-item>
      <el-form-item label="外链地址" prop="meta.isLink">
        <el-input v-model="drawerProps.row.meta.isLink" placeholder="请输入外链地址" clearable></el-input>
      </el-form-item>
      <!-- 父菜单选择器 -->
      <el-form-item label="父菜单" prop="parent_id">
        <el-select
          v-model="drawerProps.row.parent_id"
          placeholder="请选择父菜单"
          clearable
          filterable
          :disabled="drawerProps.isView"
          style="width: 100%"
        >
          <el-option
            v-for="menu in parentMenuOptions"
            :key="menu.id"
            :label="menu.displayTitle"
            :value="menu.id"
            :disabled="menu.disabled"
            :class="{ 'top-level-option': menu.isTopLevel }"
          />
        </el-select>
      </el-form-item>
      <!-- 可根据实际需求添加更多表单项 -->
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
import SelectIcon from "@/components/SelectIcon/index.vue";
import { getMenu } from "@/api/modules/system";
import { getFlatMenuList } from "@/utils";

const rules = reactive({
  "meta.title": [{ required: true, message: "请填写菜单名称" }],
  path: [{ required: true, message: "请填写菜单路径" }],
  parent_id: [
    {
      validator: (rule: any, value: any, callback: any) => {
        if (value === undefined || value === null) {
          callback(new Error("请选择父菜单"));
        } else {
          callback();
        }
      },
      trigger: "change"
    }
  ]
});

interface DrawerProps {
  title: string;
  isView: boolean;
  row: any;
  api?: (params: any) => Promise<any>;
  getTableList?: () => void;
  parentMenu?: any;
  allMenus?: any[]; // 新增：完整的菜单数据
}

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: { meta: {} },
  parentMenu: null
});

// 父菜单选项数据
const allMenus = ref<any[]>([]);
const parentMenuOptions = ref<any[]>([]);

// 获取所有菜单数据
const fetchAllMenus = async () => {
  try {
    const response = await getMenu({ deleted: 0 });
    allMenus.value = response.data || [];
    updateParentMenuOptions();
  } catch {
    console.error("获取菜单列表失败:", error);
    allMenus.value = [];
  }
};

// 更新父菜单选项
const updateParentMenuOptions = () => {
  const currentMenuId = drawerProps.value.row.id;
  const flatMenus = getFlatMenuList(allMenus.value);

  // 添加"无父菜单"选项（顶级菜单）
  const options = [
    {
      id: 0,
      displayTitle: "无父菜单（顶级菜单）",
      disabled: false,
      isTopLevel: true
    }
  ];

  // 添加所有菜单选项
  const menuOptions = flatMenus.map(menu => {
    // 禁用当前菜单及其子菜单
    const isCurrentMenu = menu.id === currentMenuId;
    const isChildOfCurrent = isChildMenu(menu, currentMenuId, flatMenus);

    // 确保菜单标题存在，优先使用meta.title，其次使用name
    const menuTitle = menu.meta && menu.meta.title ? menu.meta.title : menu.name || `菜单${menu.id}`;

    // 根据层级添加缩进显示
    const level = getMenuLevel(menu, flatMenus);
    const indent = "　".repeat(level); // 使用全角空格作为缩进
    const displayTitle = `${indent}${menuTitle}`;

    return {
      ...menu,
      displayTitle,
      disabled: isCurrentMenu || isChildOfCurrent,
      isTopLevel: false
    };
  });

  parentMenuOptions.value = [...options, ...menuOptions];
};

// 获取菜单层级
const getMenuLevel = (menu: any, allMenus: any[]): number => {
  if (menu.parent_id === 0) return 0;

  const parent = allMenus.find(m => m.id === menu.parent_id);
  if (!parent) return 0;

  return 1 + getMenuLevel(parent, allMenus);
};

// 检查菜单是否为指定菜单的子菜单
const isChildMenu = (menu: any, parentId: number, allMenus: any[]): boolean => {
  if (menu.parent_id === parentId) {
    return true;
  }
  if (menu.parent_id === 0) {
    return false;
  }
  const parent = allMenus.find(m => m.id === menu.parent_id);
  return parent ? isChildMenu(parent, parentId, allMenus) : false;
};

// 接收父组件传过来的参数
const acceptParams = async (params: DrawerProps) => {
  drawerProps.value = params;
  if (!drawerProps.value.row.meta) drawerProps.value.row.meta = {};
  if (drawerProps.value.row.sort === undefined) drawerProps.value.row.sort = 0; //设置默认排序值

  // 确保parent_id有默认值
  if (drawerProps.value.row.parent_id === undefined) {
    drawerProps.value.row.parent_id = 0;
  }

  // 优先使用传入的菜单数据，如果没有则重新获取
  if (params.allMenus && params.allMenus.length > 0) {
    allMenus.value = params.allMenus;
    updateParentMenuOptions();
  } else {
    await fetchAllMenus();
  }

  drawerVisible.value = true;
};

// 提交数据（新增/编辑）
const ruleFormRef = ref<FormInstance>();
const handleSubmit = () => {
  ruleFormRef.value!.validate(async valid => {
    if (!valid) return;
    try {
      // 只取表单字段
      const { meta, path, component, sort, parent_id, id } = drawerProps.value.row;
      // 只组装需要的内容
      const submitData: any = {
        meta: {
          title: meta?.title,
          icon: meta?.icon,
          isAffix: meta?.isAffix,
          isFull: meta?.isFull,
          isHide: meta?.isHide,
          isKeepAlive: meta?.isKeepAlive,
          isLink: meta?.isLink
        },
        path,
        component,
        sort,
        id
      };
      // 添加parent_id属性（确保有值，0表示顶级菜单）
      submitData.parent_id = parent_id !== undefined ? parent_id : 0;
      // 注意：isNew 只用于前端逻辑判断，不提交给后端

      await drawerProps.value.api!(submitData);
      ElMessage.success({ message: `${drawerProps.value.title}菜单成功！` });
      if (drawerProps.value.getTableList) {
        drawerProps.value.getTableList();
      }
      drawerVisible.value = false;
    } catch {}
  });
};

defineExpose({
  acceptParams
});
</script>

<style scoped lang="scss">
:deep(.top-level-option) {
  font-weight: bold;
  color: var(--el-color-primary);
}
</style>
