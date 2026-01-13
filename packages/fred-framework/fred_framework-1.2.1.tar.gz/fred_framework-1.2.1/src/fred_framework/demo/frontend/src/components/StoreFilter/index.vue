<template>
  <div class="store-filter-wrapper">
    <el-card class="store-filter-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>{{ title || t("storeFilter.storeSelection") }}</span>
          <el-button type="primary" link @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            {{ refreshText || t("storeFilter.refresh") }}
          </el-button>
        </div>
      </template>

      <div class="store-filter-content">
        <el-input
          v-model="searchKeyword"
          :placeholder="searchPlaceholder || t('storeFilter.searchStore')"
          :prefix-icon="Search"
          clearable
          class="store-search-input"
          @input="handleSearchInput"
        />

        <div class="store-list">
          <div
            v-for="store in filteredStores"
            :key="store.id"
            :class="['store-item', { active: currentStoreId === store.id }]"
            @click="handleSelectStore(store)"
          >
            <div class="store-name">{{ store.name }}</div>
            <div class="store-address">{{ store.address || t("storeFilter.noAddress") }}</div>
            <div class="store-location">
              {{
                [store.province_name, store.city_name, store.district_name].filter(Boolean).join(" ") ||
                t("storeFilter.noLocation")
              }}
            </div>
          </div>

          <div v-if="filteredStores.length === 0" class="no-stores">{{ t("storeFilter.noStoreData") }}</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { Refresh, Search } from "@element-plus/icons-vue";
import { useI18n } from "vue-i18n";
import { getStoreList, type StoreInfo } from "@/api/modules/store";
import { ElMessage } from "element-plus";

interface Props {
  modelValue?: number | null;
  title?: string;
  refreshText?: string;
  searchPlaceholder?: string;
  autoLoad?: boolean;
}

interface Emits {
  (e: "update:modelValue", value: number | null): void;
  (e: "change", store: StoreInfo | null): void;
  (e: "refresh"): void;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  autoLoad: true
});

const emit = defineEmits<Emits>();

const { t } = useI18n();

// 门店列表
const storeList = ref<StoreInfo[]>([]);
const searchKeyword = ref<string>("");
const currentStoreId = ref<number | null>(props.modelValue || null);

// 计算过滤后的门店列表
const filteredStores = computed(() => {
  let filtered = storeList.value;

  // 按搜索关键词过滤
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.toLowerCase();
    filtered = filtered.filter(
      store => store.name.toLowerCase().includes(keyword) || (store.address && store.address.toLowerCase().includes(keyword))
    );
  }

  return filtered;
});

// 加载门店列表
const loadStoreList = async () => {
  try {
    const response = await getStoreList({ page: 1, limit: 1000 });

    // 根据 axios 拦截器的处理，response 是包含 code 和 data 的对象
    // 接口返回格式: { code: 200, data: { records: [], total: 2 } }
    // axios 拦截器返回整个对象（包含 code 和 data）

    let records: StoreInfo[] = [];

    // 优先检查 response.data.records（标准格式）
    if (response && response.data && response.data.records && Array.isArray(response.data.records)) {
      records = response.data.records;
    }
    // 如果 response 本身就是 ResPage 结构（直接包含 records）
    else if (response && response.records && Array.isArray(response.records)) {
      records = response.records;
    }
    // 如果 response.data 本身就是数组
    else if (response && response.data && Array.isArray(response.data)) {
      records = response.data;
    }
    // 如果 response.data.data 是数组（嵌套结构）
    else if (response && response.data && response.data.data && Array.isArray(response.data.data)) {
      records = response.data.data;
    } else {
      records = [];
    }

    storeList.value = records;

    // 如果没有选中门店，默认选中第一个
    if (!props.modelValue && storeList.value.length > 0) {
      handleSelectStore(storeList.value[0]);
    } else if (props.modelValue) {
      // 如果有modelValue，确保它在列表中
      const selected = storeList.value.find(s => s.id === props.modelValue);
      if (!selected && storeList.value.length > 0) {
        handleSelectStore(storeList.value[0]); // 如果modelValue不在列表中，默认选中第一个
      }
    }
  } catch (error: any) {
    // 如果是请求被取消（CanceledError），静默处理，不显示错误消息
    // 这通常发生在以下情况，都是正常行为：
    // 1. 组件卸载或页面切换时，正在进行的请求被取消
    // 2. 相同 URL 的重复请求，之前的请求被自动取消（AxiosCanceler 机制）
    // 3. 用户快速切换页面时，之前的请求被取消
    if (error?.name === "CanceledError" || error?.code === "ERR_CANCELED" || error?.message === "canceled") {
      return;
    }

    console.error("StoreFilter - 加载门店列表失败:", error);
    const errorMessage = error?.response?.data?.message || error?.message || "加载门店列表失败";
    ElMessage.error(errorMessage);
    storeList.value = [];
  }
};

// 刷新门店列表
const handleRefresh = () => {
  loadStoreList();
  emit("refresh");
};

// 选择门店
const handleSelectStore = (store: StoreInfo) => {
  currentStoreId.value = store.id;
  emit("update:modelValue", store.id);
  emit("change", store);
};

// 搜索输入处理
const handleSearchInput = () => {
  // 可以在这里添加防抖等逻辑
};

// 监听外部传入的 modelValue 变化
watch(
  () => props.modelValue,
  newValue => {
    currentStoreId.value = newValue || null;
  }
);

// 暴露方法供父组件调用
defineExpose({
  loadStoreList,
  refreshStoreList: handleRefresh,
  getCurrentStore: () => {
    return storeList.value.find(store => store.id === currentStoreId.value) || null;
  }
});

// 组件挂载时初始化
onMounted(() => {
  if (props.autoLoad) {
    loadStoreList();
  }
});
</script>

<style scoped lang="scss">
.store-filter-wrapper {
  width: 320px;
  min-width: 240px;
  max-width: 100%;
  flex-shrink: 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.store-filter-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: none;
  border-radius: 8px;

  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid #e4e7ed;
    background-color: #fafafa;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
      color: #303133;
    }
  }

  :deep(.el-card__body) {
    padding: 0;
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
}

.store-filter-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.store-search-input {
  margin: 16px 20px;
  flex-shrink: 0;
  width: calc(100% - 40px);
  max-width: 100%;
  box-sizing: border-box;

  :deep(.el-input__wrapper) {
    width: 100%;
    max-width: 100%;
  }

  :deep(.el-input) {
    width: 100%;
    max-width: 100%;
  }
}

.store-list {
  flex: 1;
  overflow-y: auto;
  padding: 2px 20px 20px;

  .store-item {
    padding: 12px 16px;
    margin-bottom: 8px;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    background: #fafafa;

    &:hover {
      border-color: #409eff;
      background: #f0f9ff;
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
    }

    &.active {
      border-color: #409eff;
      background: #e6f7ff;
      box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
    }

    .store-name {
      font-size: 14px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .store-address {
      font-size: 12px;
      color: #606266;
      margin-bottom: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .store-location {
      font-size: 12px;
      color: #909399;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  .no-stores {
    text-align: center;
    color: #909399;
    font-size: 14px;
    padding: 40px 20px;
  }
}

/* 低分辨率适配 */
@media screen and (max-width: 1440px) {
  .store-filter-wrapper {
    width: 280px;
    min-width: 200px;
  }

  .store-search-input {
    margin: 12px 16px;
    width: calc(100% - 32px);
  }
}

@media screen and (max-width: 1024px) {
  .store-filter-wrapper {
    width: 240px;
    min-width: 180px;
  }

  .store-search-input {
    margin: 10px 12px;
    width: calc(100% - 24px);
  }
}
</style>
