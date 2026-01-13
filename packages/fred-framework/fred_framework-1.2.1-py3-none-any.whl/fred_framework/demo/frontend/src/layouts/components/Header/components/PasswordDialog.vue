<template>
  <el-dialog v-model="dialogVisible" title="修改密码" width="500px" draggable>
    <el-form :model="form" :rules="rules" ref="passwordForm">
      <el-form-item label="旧密码" prop="oldPassword">
        <el-input type="password" v-model="form.oldPassword" autocomplete="off"></el-input>
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input type="password" v-model="form.newPassword" autocomplete="off"></el-input>
      </el-form-item>
      <el-form-item label="重复密码" prop="repPassword">
        <el-input type="password" v-model="form.repPassword" autocomplete="off"></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm()">确认</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { updatePassword } from "@/api/modules/admin";
import md5 from "md5";
import { FormInstance } from "element-plus";

const passwordForm = ref<FormInstance | null>(null);
const form = reactive({
  oldPassword: "",
  newPassword: "",
  repPassword: ""
});

const validatePassCheck = (rule: any, value: string, callback: any) => {
  if (value !== form.newPassword) {
    callback(new Error("两次输入的密码不一致!"));
  } else {
    callback();
  }
};

const rules = reactive({
  oldPassword: [{ required: true, message: "请输入旧密码", trigger: "blur" }],
  newPassword: [{ required: true, message: "请输入新密码", trigger: "blur" }],
  repPassword: [{ validator: validatePassCheck, trigger: "blur" }]
});

const submitForm = () => {
  // 检查 passwordForm 是否存在
  if (!passwordForm.value) {
    console.error("表单未正确挂载");
    return;
  }

  passwordForm.value.validate((valid: boolean) => {
    if (valid) {
      updatePassword({
        oldPassword: md5(form.oldPassword),
        newPassword: md5(form.newPassword),
        repPassword: md5(form.repPassword)
      })
        .then(() => {
          // 根据返回结果进行处理dialogVisible.value = false;
        })
        .catch(error => {
          console.error("更新密码失败:", error);
        });
    } else {
    }
  });
};

const dialogVisible = ref(false);
const openDialog = () => {
  dialogVisible.value = true;
};

defineExpose({ openDialog });
</script>
