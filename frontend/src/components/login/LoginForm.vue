<template>
  <div class="login-form-card">
    <h2 class="form-title">加入我们</h2>
    <p class="form-subtitle">使用您的账号开始体验。</p>

    <div class="form-container">
      <el-form
          :model="formData"
          :rules="rules"
          ref="ruleFormRef"
          label-width="120px"
          class="el-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
              v-model="formData.username"
              placeholder="请输入用户名"
              :disabled="isLoading"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
              v-model="formData.password"
              placeholder="请输入密码"
              type="password"
              :show-password="true"
              :disabled="isLoading"
          />
        </el-form-item>
      </el-form>
    </div>

    <div class="main-action">
      <el-button
        @click="handleLogin"
        :disabled="isLoading"
        class="pill-button"
        :style="{ opacity: isLoading ? 0.6 : 1 }"
      >
        {{ isLoading ? '正在登录...' : '开始使用' }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import type { FormRules } from 'element-plus';
import { loginUser } from '@/services/authService';
import { useAuthStore } from '@/store/auth';

const authStore = useAuthStore();

const formData = reactive<{
  username: string;
  password: string;
}>({
  username: '',
  password: ''
});

const ruleFormRef = ref<any>(null);
const isLoading = ref(false);

const rules: FormRules = reactive({
  username: [
    {
      required: true,
      message: '请输入用户名',
      trigger: 'blur',
    },
  ],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur',
    },
  ],
});

const handleLogin = async () => {
  // 1. 基本数据校验
  if (!formData.username || !formData.password) {
    ElMessage.warning('请填写所有必填字段');
    return;
  }

  try {
    // 2. 执行 Element Plus 表单验证
    if (ruleFormRef.value) {
      const isValid = await ruleFormRef.value.validate();
      if (!isValid) return;
    }

    // 3. 进入请求状态
    isLoading.value = true;

    // 4. 直接调用 API
    const response = await loginUser(formData.username, formData.password);

    // 5. 成功处理
    authStore.loginSuccess({
      accessToken: response.access_token,
      userData: { username: formData.username }
    });

    ElMessage.success('登录成功');
  } catch (error: any) {
    // 6. 统一错误处理
    let errorMessage = '登录失败';

    if (error.message?.includes('[AUTH_ERROR]')) {
      try {
        const msg = JSON.parse(error.message.replace('[AUTH_ERROR] ', ''));
        errorMessage = msg.message || '登录失败';
      } catch {
        errorMessage = '认证失败，请检查账号或密码';
      }
    } else {
      errorMessage = error.message || '系统发生错误';
    }

    console.error('Login Error:', error);
    ElMessage.error(errorMessage);
  } finally {
    // 7. 无论成功失败，最后都要关闭 Loading
    isLoading.value = false;
  }
};
</script>

<style scoped>
.login-form-card {
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.form-title {
  color: #303133;
  margin-bottom: 8px;
  font-size: 1.5rem;
  font-weight: 600;
}

.form-subtitle {
  color: #909399;
  margin-bottom: 30px;
  font-size: 1rem;
}

.form-container {
  flex: 1;
  margin-bottom: 30px;
}

.main-action {
  margin-top: 10px;
}

.pill-button {
  width: 100%;
  height: 48px;
  background-color: #007AFF;
  color: #fff;
  border: none;
  border-radius: 24px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.pill-button:active {
  opacity: 0.8;
}

.el-form {
  margin-bottom: 20px;
}
</style>
