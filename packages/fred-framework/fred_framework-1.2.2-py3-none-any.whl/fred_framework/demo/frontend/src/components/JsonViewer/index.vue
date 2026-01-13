<template>
  <div class="json-viewer-wrapper">
    <div class="content-header">
      <div class="header-left">
        <span class="content-title">{{ title }}</span>
        <el-tag v-if="hasJsonContent && showStats" type="success" size="small">
          {{ jsonStats }}
        </el-tag>
      </div>
      <div v-if="showActions" class="content-actions">
        <el-button v-if="showExpandCollapse" size="small" @click="toggleExpandCollapse" :icon="isExpanded ? 'Minus' : 'Plus'">
          {{ isExpanded ? "折叠全部" : "展开全部" }}
        </el-button>
        <el-button v-if="showCopy" size="small" @click="copyJsonContent" :icon="'Copy'"> 复制 </el-button>
        <el-button v-if="showDownload" size="small" @click="downloadJson" :icon="'Download'"> 下载 </el-button>
      </div>
    </div>
    <div class="content-display" :style="{ height: height }">
      <div v-if="hasJsonContent" class="json-viewer-container">
        <vue-json-pretty
          :key="`json-viewer-${deep}-${forceUpdate}`"
          :data="parsedJsonData"
          :show-length="true"
          :show-double-quotes="false"
          :show-line="true"
          :deep="deep"
          :path="'res'"
          :show-line-number="true"
          :highlight-mouseover-node="true"
          :highlight-selected-node="true"
          :select-on-click-node="true"
          :collapsed-on-click-brackets="true"
          :theme="'light'"
          class="json-pretty"
        />
      </div>
      <div v-else class="empty-json">
        <el-empty :description="emptyText" :image-size="100" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from "vue";
import { ElMessage } from "element-plus";
import VueJsonPretty from "vue-json-pretty";
import "vue-json-pretty/lib/styles.css";

// 类型定义
interface Props {
  content: string;
  title?: string;
  height?: string;
  emptyText?: string;
  showStats?: boolean;
  showActions?: boolean;
  showExpandCollapse?: boolean;
  showCopy?: boolean;
  showDownload?: boolean;
  downloadFileName?: string;
  deep?: number;
}

// Props
const props = withDefaults(defineProps<Props>(), {
  content: "",
  title: "配置内容",
  height: "calc(100vh - 400px)",
  emptyText: "暂无配置内容",
  showStats: true,
  showActions: true,
  showExpandCollapse: true,
  showCopy: true,
  showDownload: true,
  downloadFileName: "",
  deep: 3
});

// 响应式数据
const deep = ref(props.deep);
const forceUpdate = ref(0);
const isExpanded = ref(false); // 展开状态

// 计算属性
const hasJsonContent = computed(() => !!(props.content && String(props.content).trim().length > 0));

// 解析JSON数据
const parsedJsonData = computed(() => {
  if (!props.content) return {};
  try {
    // 首先尝试解析为JSON
    return JSON.parse(props.content);
  } catch {
    // 如果JSON解析失败，尝试处理Python字典格式
    const content = props.content.trim();
    if (content.startsWith("{") && content.endsWith("}")) {
      try {
        // 简单的Python字典到JSON转换
        const jsonStr = content
          .replace(/'/g, '"') // 单引号替换为双引号
          .replace(/(\w+):/g, '"$1":') // 键名加引号
          .replace(/: True/g, ": true") // Python True -> JSON true
          .replace(/: False/g, ": false") // Python False -> JSON false
          .replace(/: None/g, ": null"); // Python None -> JSON null
        return JSON.parse(jsonStr);
      } catch {
        return {};
      }
    }
    return {};
  }
});

const jsonStats = computed(() => {
  if (!hasJsonContent.value) return "空配置";

  const countKeys = (obj: any): number => {
    if (typeof obj !== "object" || obj === null) return 0;
    let count = Object.keys(obj).length;
    for (const key in obj) {
      if (typeof obj[key] === "object" && obj[key] !== null) {
        count += countKeys(obj[key]);
      }
    }
    return count;
  };

  const parsedData = parsedJsonData.value;
  if (!parsedData || Object.keys(parsedData).length === 0) {
    return "配置格式错误";
  }

  const totalKeys = countKeys(parsedData);
  return `${totalKeys} 个配置项`;
});

// 方法
const toggleExpandCollapse = async () => {
  if (isExpanded.value) {
    // 当前是展开状态，执行折叠
    deep.value = 1; // 设置为1来折叠所有子节点，只保留根节点
    isExpanded.value = false;
  } else {
    // 当前是折叠状态，执行展开
    deep.value = Infinity; // 设置为无穷大来展开所有
    isExpanded.value = true;
  }
  forceUpdate.value++; // 强制重新渲染
  await nextTick(); // 等待DOM更新
};

// 工具方法
const copyJsonContent = async () => {
  try {
    await navigator.clipboard.writeText(props.content);
    ElMessage.success("配置内容已复制到剪贴板");
  } catch {
    ElMessage.error("复制失败");
  }
};

const downloadJson = () => {
  try {
    const blob = new Blob([props.content], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    const fileName = props.downloadFileName || `json-config-${Date.now()}.json`;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    ElMessage.success("配置文件已下载");
  } catch {
    ElMessage.error("下载失败");
  }
};

// 暴露方法给父组件
defineExpose({
  toggleExpandCollapse,
  copyJsonContent,
  downloadJson
});
</script>

<style scoped lang="scss">
.json-viewer-wrapper {
  .content-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0;
    padding-bottom: 4px;
    border-bottom: 1px solid #e4e7ed;

    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;

      .content-title {
        font-weight: 600;
        color: #303133;
      }
    }

    .content-actions {
      display: flex;
      gap: 8px;
    }
  }

  .content-display {
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    background-color: #fafafa;
    min-height: 300px;
    overflow: hidden;

    .json-viewer-container {
      height: 100%;
      background-color: #f8f9fa;
      overflow: auto;
      border-radius: 6px;
      border: 1px solid #e4e7ed;
      padding: 16px;

      .json-pretty {
        font-family: "JetBrains Mono", "Fira Code", "Consolas", "Monaco", "Courier New", monospace;
        font-size: 13px;
        line-height: 1.6;
      }
    }

    .empty-json {
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #f8f9fa;
      border-radius: 6px;
      border: 1px solid #e4e7ed;
    }
  }
}
</style>
