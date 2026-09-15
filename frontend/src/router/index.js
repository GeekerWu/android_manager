import { createRouter, createWebHistory } from 'vue-router';
import DashBoard from '@/components/DashBoard.vue';
import Login from '@/components/login/Login.vue';
import NotFoundComponent from '@/components/NotFound.vue';
import UserProfile from '@/components/UserProfile.vue';
import Settings from '@/components/Settings.vue';
import Camera from '@/components/Camera.vue';
import LayoutContainer from '@/components/LayoutContainer.vue';
import { useAuthStore } from '@/store/auth';
import { computed } from 'vue';

const routes = [
  {
    path: '/',
    component: LayoutContainer,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'DashBoard',
        component: DashBoard,
      },
      {
        path: 'profile',
        name: 'Profile',
        component: UserProfile,
      },
      {
        path: 'settings',
        name: 'Settings',
        component: Settings,
      },
      {
        path: 'camera',
        name: 'Camera',
        component: Camera,
      },
  {
    path: 'onnxruntime',
    name: 'OnnxRuntime',
    component: () => import('@/components/OnnxRuntime.vue'),
  },
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
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

router.beforeEach((to, from) => {
  const store = useAuthStore();
  const isAuthenticated = computed(() => store.isAuthenticated);
  const requiresAuth = to.meta.requiresAuth;

  if (requiresAuth && !isAuthenticated.value) {
    return { path: '/login', query: { redirect: to.fullPath } };
  }

  if (to.path === '/login' && isAuthenticated.value) {
    return { path: '/dashboard', query: { redirect: to.fullPath } };
  }

  return true;
});

export { router };