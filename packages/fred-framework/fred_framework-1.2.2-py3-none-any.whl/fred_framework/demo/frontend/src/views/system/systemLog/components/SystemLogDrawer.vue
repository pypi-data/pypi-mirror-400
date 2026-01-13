<template>
  <el-drawer v-model="drawerVisible" :title="drawerTitle" size="50%">
    <el-skeleton v-if="loading" :rows="8" animated />
    <div v-else-if="formData" class="log-detail-container">
      <!-- 基本信息网格布局 -->
      <el-card class="basic-info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-descriptions :column="1" size="small">
              <el-descriptions-item label="日志ID">{{ formData.id }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="8">
            <el-descriptions :column="1" size="small">
              <el-descriptions-item label="用户ID">{{ formData.user_id }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="8">
            <el-descriptions :column="1" size="small">
              <el-descriptions-item label="用户名">{{ formData.username }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="8">
            <el-descriptions :column="1" size="small">
              <el-descriptions-item label="API路径">{{ formData.api }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="8">
            <el-descriptions :column="1" size="small">
              <el-descriptions-item label="请求方法">{{ formData.method }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="8">
            <el-descriptions :column="1" size="small">
              <el-descriptions-item label="状态码">{{ formData.code }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="24">
            <el-descriptions :column="1" size="small">
              <el-descriptions-item label="创建时间">{{ formData.created }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
      </el-card>

      <!-- 请求数据 -->
      <el-card class="data-card">
        <template #header>
          <div class="card-header">
            <span>请求数据</span>
            <el-button link type="primary" @click="toggleRequestFormat" size="small" v-if="formData.request">
              {{ isRequestFormatted ? "显示原始数据" : "显示格式化数据" }}
            </el-button>
          </div>
        </template>
        <div v-if="formData.request">
          <el-input
            v-if="isRequestFormatted"
            type="textarea"
            :rows="10"
            readonly
            :model-value="formattedRequest"
            class="formatted-json"
          />
          <el-input v-else type="textarea" :rows="10" readonly :model-value="formData.request" />
        </div>
        <div v-else class="empty-data">空</div>
      </el-card>

      <!-- 响应数据 -->
      <el-card class="data-card">
        <template #header>
          <div class="card-header">
            <span>响应数据</span>
            <el-button link type="primary" @click="toggleResponseFormat" size="small" v-if="formData.response">
              {{ isResponseFormatted ? "显示原始数据" : "显示格式化数据" }}
            </el-button>
          </div>
        </template>
        <div v-if="formData.response">
          <el-input
            v-if="isResponseFormatted"
            type="textarea"
            :rows="10"
            readonly
            :model-value="formattedResponse"
            class="formatted-json"
          />
          <el-input v-else type="textarea" :rows="10" readonly :model-value="formData.response" />
        </div>
        <div v-else class="empty-data">空</div>
      </el-card>
    </div>

    <template #footer>
      <el-button @click="drawerVisible = false">关闭</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts" name="systemLogDrawer">
import { ref, computed } from "vue";
import { SystemLog } from "@/api/model/systemModel";
import { getSystemLogDetail } from "@/api/modules/system";

const drawerVisible = ref(false);
const drawerTitle = ref("查看日志");
const formData = ref<SystemLog | null>(null);
const loading = ref(false);
const isRequestFormatted = ref(true);
const isResponseFormatted = ref(true);

// 格式化JSON数据
const formatJson = (str: string | null | undefined): string => {
  if (!str) return "";
  try {
    // 如果已经是格式化的JSON，直接返回
    if (str.trim().startsWith("{") || str.trim().startsWith("[")) {
      const jsonObj = JSON.parse(str);
      return JSON.stringify(jsonObj, null, 2);
    }
    return str;
  } catch {
    // 如果解析失败，返回原始字符串
    return str;
  }
};

// 计算格式化后的请求数据
const formattedRequest = computed(() => {
  return formatJson(formData.value?.request);
});

// 计算格式化后的响应数据
const formattedResponse = computed(() => {
  return formatJson(formData.value?.response);
});

// 切换请求数据格式显示
const toggleRequestFormat = () => {
  isRequestFormatted.value = !isRequestFormatted.value;
};

// 切换响应数据格式显示
const toggleResponseFormat = () => {
  isResponseFormatted.value = !isResponseFormatted.value;
};

// 打开抽屉
const openDrawer = async (row: SystemLog) => {
  // 先显示基础信息
  formData.value = row;
  drawerVisible.value = true;
  loading.value = true;

  try {
    // 请求详细信息
    const res = await getSystemLogDetail({ id: row.id });
    formData.value = res.data;
  } catch (error) {
    console.error("获取日志详情失败:", error);
  } finally {
    loading.value = false;
  }
};

// 暴露给父组件的方法
defineExpose({
  openDrawer
});
</script>

<style scoped>
.log-detail-container {
  padding: 20px;
}

.basic-info-card {
  margin-bottom: 20px;
}

.data-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.formatted-json {
  font-family: "Courier New", Courier, monospace;
}

.empty-data {
  color: #909399;
  font-style: italic;
  padding: 20px;
  text-align: center;
}
</style>
