import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/components/HelloWorld.vue'; // 假设首页使用这个组件
import Login from '@/components/Login.vue'; // 我们刚刚创建的登录组件

// --- 模拟认证状态检查 ---
// 这是一个简化的模拟函数，实际项目中应依赖Pinia/Vuex
const checkAuthStatus = () => {
  // 检查 LocalStorage 或全局 store 中是否有有效的 Token
  const token = localStorage.getItem('authToken');
  return !!token; // 存在 Token 即视为已登录
};

// --- 创建路由历史和实例 ---
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: false} // 首页需要认证
  },
  {
    path: '/login',
    name: 'Login',
    component: Login, // 新添加的登录组件
    meta: { requiresAuth: false } // 登录页不需要认证
  },
  // ... 其他路由
];

// --- 创建路由实例 ---
const router = createRouter({
  history: createWebHistory(),
  routes
});

// --- 核心逻辑：全局前置守卫 (Router Guard) ---
router.beforeEach((to, from, next) => {
  const requiresAuth = to.meta.requiresAuth;
  const isAuthenticated = checkAuthStatus();

  // 1. 检查是否需要认证
  if (requiresAuth && !isAuthenticated) {
    // 未认证，并且目标页面需要认证 -> 重定向到登录页
    console.warn('未登录用户尝试访问受保护路由，重定向到 /login');
    next({ name: 'Login' });
  } else if (to.name === 'Login' && isAuthenticated) {
    // 用户已经登录，但尝试访问登录页 -> 重定向到首页
    console.info('已登录用户访问登录页，重定向到主页');
    next({ name: 'Home' });
  } else {
    // 否则，正常前进
    next();
  }
});

export default router;
