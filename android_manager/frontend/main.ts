import { createApp } from 'vue';
import App from './App.vue';
import { router } from './router'; // ✅ 修正：改为命名导入
import * as ElementPlus from 'element-plus';
import 'element-plus/dist/index.css'
import { ElMessage } from 'element-plus';
import { createStore } from 'vuex';

// 1. 核心修正：使用全局实例的方式创建 Vuex Store
const store = createStore({
  modules: {
    auth: require('./store/auth') // ✅ 关键修正：使用 require() 来加载模块
  }
});

// 2. 挂载依赖
const app = createApp(App);

// 3. 顺序调整：确保 Store 依赖被正确挂载
app.use(router);
app.use(ElementPlus);
app.use(store);
app.config.globalProperties.$message = ElMessage;

// ======================================================================
// ⭐ 核心补丁：在全局挂载 Store 变更事件监听 (连接器) ⭐
// ----------------------------------------------------------------------
app.mixin({
  mounted() {
    const router = this.$router;
    // 假设项目中存在一个全局可用的 EventBus/emitter
    const emitter = this.$emitter || this.$globalEventBus;
    if (emitter) {
        // 监听 'auth-changed' 事件。这是从 store.ts 发出的信号。
        emitter.on('auth-changed', () => {
            console.warn("[Main.ts Listener] 检测到认证状态改变，强制路由重评估。");
            // 强制重新导航到当前路由，触发 before/afterEach 守卫重新执行状态检查。
            if (router.currentRoute.value) {
                router.push(router.currentRoute.value.fullPath, { replace: true });
            }
        });
    } else {
        console.error("[Main.ts Listener] 无法找到全局事件发射器 (EventBus) 来监听 'auth-changed'。状态同步可能失效。");
    }
  }
});
// ---------------------------------------------------------------------
// ======================================================================


// 4. 挂载应用到 DOM 元素
app.mount('#app');