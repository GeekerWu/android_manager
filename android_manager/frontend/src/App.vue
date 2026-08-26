<template>
    <div id="app">
        <!-- 核心逻辑调整：如果当前路由是 /login，我们不信任 <router-view>，而是手动展示 <Login /> 组件，以符合当前需求。
        否则，我们恢复使用标准路由渲染。 -->
        <template v-if="currentPath === '/login'">
            <Login />
        </template>
        <router-view v-else />
    </div >
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Login from '@/components/login/Login.vue'; // 确保 Login 组件在这里被导入

// 核心变量：获取当前路由的路径
const route = useRoute();
const currentPath = computed(() => route.path);

// 注意：这个手动判断绕过了路由守卫的控制，只为满足当前App.vue内部需要显式加载Login的硬性要求。
</script>

<style>
#app {
    /* 这是一个全局作用域，用于覆盖基础样式 */
}
</style>