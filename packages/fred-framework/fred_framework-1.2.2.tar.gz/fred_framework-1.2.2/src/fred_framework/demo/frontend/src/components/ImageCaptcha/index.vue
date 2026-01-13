<template>
  <el-form-item prop="captcha">
    <el-input maxlength="4" placeholder="验证码" v-model="captcha" style="width: 50%; margin-right: 20px; font-size: 14px">
      <template #prefix>
        <el-icon :size="14"><Picture /></el-icon>
      </template>
    </el-input>
    <div class="captcha-container" style="margin-top: 12px">
      <img :src="captchaSrc" alt="验证码" @click="refreshCaptcha" :style="{ width, height }" />
    </div>
  </el-form-item>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { getImageCaptcha } from "@/api/modules/login";

const props = defineProps({
  width: {
    type: String,
    default: "120px"
  },
  height: {
    type: String,
    default: "40px"
  },
  captchaCode: {
    type: String,
    default: ""
  }
});

const emit = defineEmits(["update:captcha"]); // 定义一个事件，用于传递 captcha_code

const captchaSrc = ref("");
const captcha = ref(props.captchaCode); // 初始化 captcha_code

// 监听 captcha_code 的变化，并通过 emit 通知父组件
watch(captcha, newVal => {
  emit("update:captcha", newVal);
});

// 刷新验证码的方法
const refreshCaptcha = async () => {
  try {
    const res = await getImageCaptcha();
    // 直接从响应中获取 Blob 数据
    if (res instanceof Blob) {
      captchaSrc.value = URL.createObjectURL(res);
    }
    captcha.value = ""; // 清空输入框中的验证码
    emit("update:captcha", ""); // 同步清空父组件中的 captcha_code
  } catch (err) {
    console.error("获取验证码失败", err);
  }
};
// 清空验证码输入框
const clearCaptcha = () => {
  captcha.value = "";
  emit("update:captcha", ""); // 更新v-model绑定的值
};

// 暴露 refreshCaptcha 方法给父组件
defineExpose({
  refreshCaptcha,
  clearCaptcha
});

// 初始化验证码
refreshCaptcha();
</script>
