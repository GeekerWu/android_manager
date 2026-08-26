 <template>
    <div class="login-form-card">
      <!-- 标题和说明 -->
      <h2 class="form-title">🔑 用户登录</h2>
      <p class="form-subtitle">请输入您的账号和密码以继续使用应用。</p>

      <!-- Element Plus 表单 -->
      <el-form
          ref="loginFormRef"
          :model="formData"
          :rules="rules"
          @submit.native="handleLogin"
          class="el-form"
      >
        <!-- 用户名输入字段 -->
        <el-form-item label="用户名" prop="username" @blur="validateUsername">
          <el-input
              v-model="formData.username"
              placeholder="请输入用户名"
              show-message
          />
        </el-form-item>

        <!-- 密码输入字段 -->
        <el-form-item label="密码" prop="password">
          <el-input
              v-model="formData.password"
              placeholder="请输入密码"
              show-message
              type="password"
              :show-password="true"
              :disabled="isLoading"
          />
        </el-form-item>
      </el-form>

      <!-- 提交按钮 -->
      <el-button
          type="primary"
          :loading="isLoading"
          @click="handleLogin"
          class="login-button"
          style="margin-top: 30px; width: 100%"
      >
        {{ isLoading ? '登录中...' : '登录' }}
      </el-button>

      <!-- 全局错误提示 -->
      <div v-if="globalError" class="global-error">
        <el-alert
          title="登录失败"
          type="danger"
          :summary="globalError"
          show-collapse
        />
      </div>

      <!-- 辅助链接 -->
      <div class="footer-links">
        <a href="#" @click.prevent="() => {
          ElMessageBox.alert('功能还没实现 admin/admin', 'Warning', {
                              // if you want to disable its autofocus
                              // autofocus: false,
                              confirmButtonText: 'OK',
                              callback: (action: Action) => {
                                ElMessage({
                                  type: 'info',
                                  message: `action: ${action}`,
                                })
                              },
                            })
        }">忘记密码？</a>
      </div>
    </div>
  </template>

  <script setup lang="ts">
  import { reactive, ref } from 'vue';
  import { ElButton, ElInput, ElMessage ,ElMessageBox  } from 'element-plus'
  import type { Action } from 'element-plus'

  // 1. 定义 Props 和 Emits (API 定义层)
  const props = defineProps<{
    globalError: string | null;
    isLoading: boolean;
  }>();

  const emit = defineEmits<{
    (event: 'submit-login', payload: { username: string; password: string }): void;
  }>();

  // 2. 声明响应式状态 (State Management)
  const formData = reactive({
    username: '',
    password: ''
  });

  // 3. 声明本地错误状态
  const usernameError = ref<string | null>(null);
  const passwordError = ref<string | null>(null);

  // 4. 校验函数 (Business Logic)
  const validateUsername = (): boolean => {
    if (formData.username.length < 4) {
      usernameError.value = '用户名长度至少需要 4 个字符';
      return false;
    }
    usernameError.value = null;
    return true;
  };

  const validatePassword = (): boolean => {
    if (formData.password.length < 4) {
      passwordError.value = '密码长度至少需要 4 个字符';
      return false;
    }
    passwordError.value = null;
    return true;
  };

  // 5. 核心事件处理器 (Event Handler)
  const handleLogin = (event: Event) => {
    event.preventDefault();

    // *** 打印日志：用户点击，开始处理 ***
    console.log('✅ 用户点击了登录按钮，尝试提交表单。');

    // 校验
    const isUsernameValid = validateUsername();
    const isPasswordValid = validatePassword();

    if (!isUsernameValid || !isPasswordValid) {
      // ****** 最终修复点：主动抛出全局警告提示 ******
      var errmsg =""
      if(!isUsernameValid){
         errmsg = errmsg+usernameError.value
      } 
      if(!isPasswordValid){
         errmsg =errmsg+passwordError.value
      }
      
      
      ElMessage.warning('⚠️ 登录校验失败：请检查所有表单字段是否都已填写且符合要求。'+errmsg);
      return; // 阻止事件发射，流程结束
    }

    // 校验通过，触发父组件事件
    emit('submit-login', { username: formData.username, password: formData.password });
  };
  </script>

  <style scoped>
  /* =================================================================== */
  /* 最终样式：结合了参考图的视觉感、Element Plus 的中性风格，达到视觉统一的最佳点。 */
  /* =================================================================== */

  .login-form-card {
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  }

  .form-title {
    color: #303133;
    margin-bottom: 8px;
  }

  .form-subtitle {
    color: #909399;
    margin-bottom: 30px;
  }

  .el-form {
    margin-bottom: 30px;
  }

  .global-error {
    margin-top: 20px;
  }
  </style>