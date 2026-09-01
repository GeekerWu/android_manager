import { createApp } from 'vue';
import App from './App.vue';
import { router } from './router';
import * as ElementPlus from 'element-plus';
import 'element-plus/dist/index.css'
import { ElMessage } from 'element-plus';
import { createPinia } from 'pinia'; // ✅ 使用 Pinia
import { useAuthStore } from './store/auth'; // ✅ 假设 Store 文件结构

// 1. 初始化 Pinia
const pinia = createPinia();

// 2. 创建并使用应用实例
const app = createApp(App);

// 3. 挂载依赖
app.use(pinia);
app.use(router);
app.use(ElementPlus);

// 4. 全局挂载属性
app.config.globalProperties.$message = ElMessage;

// 5. ⭐ 核心补丁：监听 Store 变化以同步路由状态 ⭐
app.mixin({
  mounted() {
    // 获取 Store 实例，利用 Pinia 的 reactivity system
    const authStore = useAuthStore();

    // 监听 Store 中的认证状态变化。
    // 任何修改 Token 或用户信息的 action 都会触发此监听器。
    authStore.$subscribe((mutation, state) => {
      // 假设 auth 模块的 action 更改的类型是 'setAuthStatus'
      // 并且状态包含一个 'isLoggedIn' 的布尔值
      if (mutation.payload && mutation.payload.type === 'setAuthStatus') {
        console.warn("[Main.ts Listener] 检测到认证状态改变，强制路由重评估。");

        // 强制重新导航到当前路由，从而触发 router/index.js 中的 before/afterEach 守卫重新执行状态检查。
        const currentRoute = this.$route;
        if (currentRoute.fullPath) {
          this.$router.push(currentRoute.fullPath, { replace: true });
        }
      }
    });
  }
});

// 6. 挂载应用到 DOM 元素
app.mount('#app');