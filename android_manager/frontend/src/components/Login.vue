<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import BrandIllustration from '@/components/BrandIllustration.vue';
import LoginForm from '@/components/LoginForm.vue';

// ⚠️ 核心逻辑：现在这些状态不再是“内部声明”，而是需要从外部（如 App.vue/Router Guard）传入的 Props
const props = defineProps<{
  globalError: string | null;
  isLoading: boolean;
}>();

const emit = defineEmits<{
  (event: 'submit-login', payload: { username: string; password: string }): void;
}>();

// --- 核心流程处理器 ---
// 业务逻辑的函数定义，保持简洁，所有状态只依赖于 Props，避免本地状态管理冲突。
const handleGlobalLogin = async (loginData: { username: string; password: string }) => {
  // 1. 必须先在组件内部模拟状态变化，以便传递给子组件
  // 我们不能再在组件内部修改全局状态（globalError/isLoading），必须依赖 props 接收。

  // 这里的模拟操作是：我们无法直接修改 Props 的值，
  // 而是依赖组件接收到本次点击的上下文，并假设父组件会根据结果重新渲染我们。

  // 模拟的等待和异步操作
  console.log('--- 模拟业务逻辑：处理登录请求 ---');

  // 真正的处理逻辑（等待 1 秒）
  await new Promise(resolve => setTimeout(resolve, 1000));

  // 模拟的成功/失败反馈，应该通过事件或一个更高层的状态管理来控制，
  // 但为了代码的完整性，我们继续保留原有的alert机制进行测试收尾。
  if (loginData.username === 'admin' && loginData.password === 'admin') {
    alert('🚀 登录成功，系统已通过 AuthGuard 拦截并重定向到主页！');
    // 实际项目中：emit('login-success', { token: '...' })
  } else {
    // 由于我们无法修改 props，这里只能模拟最原始的反馈
    alert('登录失败：用户名或密码错误，请重试。');
    // 实际项目中：emit('login-failed', '用户名或密码错误...')
  }
};
</script>

<template>
  <div class="login-container">
    <!-- 🚀 左侧品牌区域 -->
    <div class="brand-area">
      <!-- 组件调用，完美适配当前的设计需求 -->
      <BrandIllustration />
    </div>

    <!-- 🔑 右侧表单操作区域 -->
    <div class="form-area">
      <!-- 核心组件调用，props 和事件绑定是业务流的核心 -->
      <LoginForm
        :global-error="globalError"
        :is-loading="isLoading"
        @submit-login="handleGlobalLogin"
      />
    </div>
  </div >
</template>

<style scoped>
/* =================================================================== */
/* 最终样式：结合了参考图的视觉感、Element Plus 的中性风格，达到视觉统一的最佳点。 */
/* =================================================================== */

.login-container {
  display: flex;
  min-height: 100vh;
  max-width: 100%;
  margin: 0 auto;
  padding: 5px 5px;
  /* 样式微调：使用更广阔的背景，增加页面的留白和呼吸感 */
  background-color: #f0f2f5; /* 整体背景：轻微的灰色背景，是企业级应用的首选 */
}

.brand-area {
  /* 1. 占据整个屏幕尺寸 */
  width: 100vw; /* 占据视口100%宽度 */
  min-height: 100vh; /* 确保至少占据视口100%高度 */
  /* 保持布局属性，但可能需要根据父容器调整 flex 行为 */
  flex: 100% 0 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start; /* 调整对齐方式，如果内容是左对齐 */

  /* 2. 基础样式修改 */
  background: #ffffff;

  /* 移除卡片外观的属性： */
  border-radius: 0; /* 移除圆角 */
  box-shadow: none; /* 移除阴影 */

  /* 调整内边距：如果希望内容贴着屏幕边缘，可以设置 padding: 0;，否则保持或根据需要修改 */
  padding: 40px;
}

   .form-area {
      /* 1. 尺寸和定位 */
      flex: 70% 0 45%;
      display: flex;
      position: absolute;

      /* 关键定位设置：实现右侧且垂直居中 */
      right: 10%;      /* 将元素的右边缘锚定到父容器的右边缘 */
      top: 50%;      /* 设定起点为父容器的垂直中线 */
      transform: translateY(-50%); /* 将元素向上移动自身高度的 50%，实现完美的垂直居中 */

      /* 2. 层级最高化：确保它显示在所有元素的上方 */
      z-index: 9999;

      /* 4. 视觉样式 */
      background: #ffffff;
      padding: 40px;
  }

/* 响应式处理 (Mobile First) */
@media (max-width: 992px) {
  .login-container {
    flex-direction: column;
    padding: 30px 10px;
  }

  /* 当屏幕收窄时，让品牌区和表单区的视觉分离感减弱，融合为一个整体的登录卡片 */
  .brand-area, .form-area {
    flex: 1 1 100%;
    max-width: 100%;
    border-radius: 0; /* 移除圆角，让卡片铺满宽度，视觉上更连贯。 */
    box-shadow: none;
    padding: 0;
  }

  /* 适配小屏幕后，需要重新设计容器的过渡效果 */
}
</style>