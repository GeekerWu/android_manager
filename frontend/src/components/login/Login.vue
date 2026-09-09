<script setup lang="ts">
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';
import { loginUser } from '@/services/authService';

const authStore = useAuthStore();
const router = useRouter();

const isLoading = ref(false);
const globalError = ref<string | null>(null);

const formData = reactive<{
  username: string;
  password: string;
}>({
  username: '',
  password: ''
});

const rules = reactive({
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
  if (!formData.username || !formData.password) {
    ElMessage.warning('请填写所有必填字段');
    return;
  }

  isLoading.value = true;
  globalError.value = null;

  try {
    // 1. Call the API service to login
    const response = await loginUser(formData.username, formData.password);

    // 2. Update the auth store with the response data
    await authStore.loginSuccess({
      payload: {
        accessToken: response.access_token,
        token_type: response.token_type,
        userData: { username: formData.username }
      }
    });

    // 3. Redirect to the dashboard specifically
    router.push('/dashboard');
  } catch (error: any) {
    console.error('Login failed:', error);
    if (error.message?.includes('[AUTH_ERROR]')) {
      try {
        const msg = JSON.parse(error.message.replace('[AUTH_ERROR] ', ''));
        globalError.value = msg.message || '认证失败，请检查账号或密码';
      } catch {
        globalError.value = '认证失败，请检查账号或密码';
      }
    } else {
      globalError.value = error.message || '登录失败，请检查账号信息。';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="title">加入我们</h2>
      <p class="subtitle">使用您的账号开始体验。</p>

      <el-form
        :model="formData"
        :rules="rules"
        ref="ruleFormRef"
        label-width="120px"
        @submit.native="handleLogin"
        class="form-content"
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

      <div v-if="globalError" class="error-message">{{ globalError }}</div>

      <div class="actions">
        <el-button
          type="primary"
          :disabled="isLoading"
          @click="handleLogin"
          class="main-btn"
        >
          {{ isLoading ? '登录中...' : '开始使用' }}
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
}

.title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #303133;
}

.subtitle {
  color: #909399;
  margin-bottom: 40px;
  font-size: 14px;
}

.form-content {
  margin-bottom: 32px;
}

.error-message {
  color: #f56c6c;
  font-size: 12px;
  margin-bottom: 16px;
  text-align: center;
}

.actions {
  margin-top: 10px;
}

.main-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 24px;
  border: none;
}

:deep(.el-input__inner) {
  padding: 12px 16px;
  border-radius: 8px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
}
</style>
