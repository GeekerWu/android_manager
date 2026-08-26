import { createRouter, createWebHistory } from 'vue-router';
import DashBoard from '@/components/DashBoard.vue';
import Login from '@/components/login/Login.vue';
import NotFoundComponent from '@/components/NotFound.vue';
// 🌟 关键：直接导入 Pinia 的 Store Hook
import { useAuthStore } from '@/store/auth';
import { computed } from 'vue';

const routes = [
  {
    path: '/dashboard',
    name: 'DashBoard',
    component: DashBoard,
    meta: { requiresAuth: true } // 首页需要认证
  },
  {
    path: '/login',
    name: 'Login',
    component: Login, // 登录页不需要认证
    meta: { requiresAuth: false } // 登录页不需要认证
  },
  // 增加一个匹配所有路径的 404 兜底路由
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundComponent,
    meta: { requiresAuth: false }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes: routes
});

// --- 🚀 核心逻辑：全局前置守卫 (Router Guard) ---
router.beforeEach((to, from) => {
  // 1. 状态获取：使用 useAuthStore() 访问 Store，确保获取的是当前上下文的 Store 实例。
  const store = useAuthStore();
  // 🌟 修复：使用 Store 定义的 getter 属性 isAuthenticated 来获取认证状态。
  const isAuthenticated = computed(() => store.isAuthenticated);

  const requiresAuth = to.meta.requiresAuth;

  // 2. 权限守卫：检查是否需要认证
  if (requiresAuth && !isAuthenticated.value) {
    console.warn(`[Router Guard] 访问 "${to.path}" 需要认证，但未认证。重定向到 /login 组件，原始目标: ${encodeURIComponent(to.fullPath)}`);
    // 🚨 修复：根据业务要求，未认证用户重定向到 /login 组件，并携带原始目标路径。
    return { path: '/login', query: { redirect: to.fullPath } };
  }

  // 3. 保护登录页：如果已认证，则禁止访问 /login
  if (to.path === '/login' && isAuthenticated.value) {
    console.warn(`[Router Guard] 用户已认证，禁止访问 /login。重定向到 /dashboard。`);
    return { path: '/dashboard', query: { is_authenticated: 'true', redirect: to.fullPath } };
  }

  // 认证成功或不需要认证，允许通过。
  return true;
});

export { router };