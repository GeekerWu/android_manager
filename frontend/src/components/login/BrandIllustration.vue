<template>
  <div class="brand-illustration-panel">
    <!-- Logo组件：使用导入的变量 (LogoSvg)，确保路径正确打包 -->
    <div class="logo-container">
      <img :src="LogoSvg" alt="品牌Logo" class="brand-logo">
    </div>

    <!-- 品牌宣传口号 -->
    <h1 class="brand-slogan">{{ SLOGAN }}</h1>
    <p class="brand-description">
      我们致力于构建一个用户友好、流程透明、极具扩展性的管理前端解决方案，让每一次交互都充满确定性。
    </p>
  </div>
</template>

<script setup lang="ts">
// 核心修复：使用 ES Modules 的 import 语法导入资源，让 Vite/Webpack 自动处理路径和资源哈希。
import LogoSvg from '@/assets/logo.svg';

// 假设Logo的图片路径和Slogan是常量，便于修改
const SLOGAN = "赋能你的业务，让工作更高效。";

// 这是一个展示品牌的组件，它负责承载所有的视觉信息，但不参与业务逻辑。
// 它的核心价值在于构建“品牌感”和“专业感”。
</script>

<style scoped>
/* 样式核心：保持现有样式，因为它已经很好地配合了整体设计 */
.brand-illustration-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  background-color: #ffffff;
  padding: 20% 10%;
}

.brand-logo {
  width: 150px;
  height: auto;
  margin-bottom: 20px;
}

.brand-slogan {
  font-size: 3.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 15px;
  line-height: 1.2;
}

.brand-description {
  font-size: 1.1rem;
  color: #7f8c8d;
  max-width: 700px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .brand-slogan {
    font-size: 2.5rem;
  }
  .brand-description {
    font-size: 1rem;
  }
}
</style>