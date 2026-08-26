<script setup lang="ts">
// 这是一个用于捕获所有未匹配到的路由的通用 404 页面。
</script>

<template>
  <div class="not-found-container">
    <h1>404 - 页面未找到</h1>
    <p>您访问的页面路径不存在，或者该页面尚未发布。404</p>
    <router-link to="/login" class="cta-button">返回首页</router-link>
  </div>
</template>

<style scoped>
.not-found-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  text-align: center;
  padding: 20px;
}

.cta-button {
  margin-top: 30px;
  padding: 10px 20px;
  border: 1px solid #409eff;
  background-color: #409eff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>