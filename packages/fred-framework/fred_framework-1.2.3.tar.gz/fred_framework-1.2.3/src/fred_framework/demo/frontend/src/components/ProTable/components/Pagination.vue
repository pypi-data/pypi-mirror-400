<template>
  <!-- 分页组件 -->
  <div class="pagination-wrapper">
    <el-pagination
      :background="true"
      :current-page="pageable.pageNum"
      :page-size="pageable.pageSize"
      :page-sizes="[10, 25, 50, 100]"
      :total="computedTotal"
      :size="globalStore?.assemblySize ?? 'default'"
      :layout="paginationLayout"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    ></el-pagination>
  </div>
</template>

<script setup lang="ts" name="Pagination">
import { useGlobalStore } from "@/stores/modules/global";
import { computed } from "vue";
const globalStore = useGlobalStore();

interface Pageable {
  pageNum: number;
  pageSize: number;
  total: number;
}

interface PaginationProps {
  pageable: Pageable;
  handleSizeChange: (size: number) => void;
  handleCurrentChange: (currentPage: number) => void;
  useComputedTotal?: boolean; // 是否使用计算后的 total（默认为 true，用于处理后端不返回总记录数的情况）
  tableData?: any[]; // 当前页的表格数据，用于判断是否可以翻页
}

const props = withDefaults(defineProps<PaginationProps>(), {
  useComputedTotal: true
});

// 根据 useComputedTotal 决定分页组件的 layout
// 如果 useComputedTotal 为 false，使用简化 layout（不显示 total、pager，但显示 jumper）
// 如果 useComputedTotal 为 true，使用完整 layout（显示所有功能）
const paginationLayout = computed(() => {
  if (!props.useComputedTotal) {
    // 简化 layout：显示 sizes、prev、next、jumper（不显示 total 和 pager）
    return "sizes, prev, next, jumper";
  }
  // 完整 layout：显示 total、sizes、prev、pager、next、jumper
  return "total, sizes, prev, pager, next, jumper";
});

// 计算 total 值：如果 useComputedTotal 为 false，设置一个足够大的值以支持跳转功能，不限制 total 值
// 如果 useComputedTotal 为 true，根据当前页数据量判断是否可以翻页
const computedTotal = computed(() => {
  // 如果不需要计算（useComputedTotal 为 false），设置一个足够大的值以支持跳转功能
  // 不限制 total 值，让用户可以跳转到任意页面
  if (!props.useComputedTotal) {
    // 如果没有数据，返回 0，下一页按钮不可用
    if (!props.tableData || props.tableData.length === 0) {
      return 0;
    }

    // 设置一个非常大的值（999999999），不限制 total 值，让用户可以跳转到任意页面
    // 这样即使用户输入 1000000 或更大的页码，也能正常跳转
    // 999999999 / 10 = 99999999 页，足够支持大部分场景
    return 999999999;
  }

  // 如果需要计算（useComputedTotal 为 true），根据当前页数据量判断是否可以翻页
  // 如果有真实的 total 值且大于 0，直接使用
  if (props.pageable.total > 0) {
    return props.pageable.total;
  }

  // 如果没有 total，根据当前页数据量判断
  if (props.tableData && props.tableData.length > 0) {
    // 如果当前页数据量等于 pageSize，说明可能还有下一页
    if (props.tableData.length >= props.pageable.pageSize) {
      // 设置一个足够大的值，确保 next 按钮可用
      return (props.pageable.pageNum + 1) * props.pageable.pageSize;
    } else {
      // 当前页数据量小于 pageSize，说明可能是最后一页
      // 设置一个刚好能显示当前页的值
      return (props.pageable.pageNum - 1) * props.pageable.pageSize + props.tableData.length;
    }
  }

  // 如果没有数据，返回 0
  return 0;
});
</script>

<style scoped>
.pagination-wrapper {
  padding: 20px 0;
  text-align: center;
  background: #fff;
  border-top: 1px solid #ebeef5;
}
</style>
