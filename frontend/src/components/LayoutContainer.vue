<template>
  <el-container class="layout-container">
    <el-aside :class="{ 'sidebar-mini': isCollapsed }" class="sidebar">
      <div class="logo-area">
         <el-icon :size="40">
            <icon-ep-menu />
          </el-icon>
        <h2 class="logo">{{ isCollapsed ? 'A' : 'APP LOGO' }}</h2>
        <el-button
          type="primary"
          circle
          @click="handleToggle"
          class="toggle-btn"
        >
          <span v-if="!isCollapsed">◀</span>
          <span v-else>▶</span>
        </el-button>
      </div>
      <el-menu
        :default-options="{ activeKey: 'dashboard' }"
        class="nav-menu"
        :collapse-transition="false"
        :default-active="activeKey"
        @toggle="handleToggle"
        @select="handleNavSelect"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.index"
          :index="item.index"
        >
          <template #title>
            <!-- <el-icon :size="20"><icon-ep-edit /></el-icon> -->
            <!-- {{item.iconname}} -->
            <!-- {{item.icon}} -->
            <el-icon>
               <component class="icons" :is="item.icon" ></component>
            </el-icon>
            <span v-if="!isCollapsed" class="nav-text">{{ item.label }}</span>
          </template>
        </el-menu-item>
      </el-menu>
      <div class="logout-area">
        <el-button type="danger" class="logout-btn" @click="handleLogout">
          <el-icon><CircleClose /></el-icon>
          <span v-if="!isCollapsed" class="nav-text">Logout</span>
        </el-button>
      </div>
    </el-aside>
    <el-main class="content-area">
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';
import {ElIcon} from 'element-plus';
import {User,CircleClose,Setting,Camera,Document} from '@element-plus/icons-vue';

const authStore = useAuthStore();
const router = useRouter();

const isCollapsed = ref(false);
const activeKey = ref('dashboard');

let menuItems = [
  { index: 'dashboard', label: 'Dashboard', icon:Document},
  { index: 'profile', label: 'Profile', icon:User },
  { index: 'settings', label: 'Settings', icon:Setting },
  { index: 'camera', label: 'Camera', icon:Camera},
];

const handleToggle = () => {
  isCollapsed.value = !isCollapsed.value;
  if (window.innerWidth < 768) {
    isCollapsed.value = true;
  }
};

const handleNavSelect = (key) => {
  const routes = {
    dashboard: '/dashboard',
    profile: '/profile',
    settings: '/settings',
    camera: '/camera',
  };

  if (routes[key]) {
    router.push(routes[key]);
  }
  activeKey.value = key;
};

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
html, body {
  margin: 0 !important;
  padding: 0 !important;
  height: 100% !important;
  width: 100% !important;
  overflow: hidden;
}

.layout-container {
  height: 100vh;
  width: 100vw;
  margin: 0 !important;
  padding: 0 !important;
  display: flex;
  flex-direction: row;
}

.sidebar {
  width: 240px;
  background-color: #1e293b !important;
  color: #f8fafc;
  padding: 20px 12px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-right: 1px solid #0f172a;
  flex-shrink: 0;
}

.sidebar.sidebar-mini {
  width: 70px;
  padding: 12px 8px;
}

.logo-area {
  margin-bottom: 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 20px;
  border-bottom: 1px solid #334155;
}

.logo {
  font-size: 1.25rem;
  font-weight: 900;
  margin: 0;
  color: #38bdf8;
  white-space: nowrap;
}

.toggle-btn {
  background-color: #334155;
  border: 1px solid #475569;
  color: white;
  margin-left: 10px;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.nav-menu {
  flex: 1;
  border: none !important;
  background: #1e293b !important;
}

.nav-menu :deep(.el-menu-item) {
  color: #ffffff !important;
  font-weight: bold !important;
  font-size: 16px;
  padding: 14px 16px;
  border-radius: 8px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  background: transparent !important;
}

.nav-menu :deep(.el-menu-item:hover) {
  background-color: #334155 !important;
  color: white !important;
}

.nav-menu :deep(.el-menu-item.active) {
  background-color: #cfd8e4 !important;
  color: white !important;
}

.nav-icon {
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-text {
  white-space: nowrap;
}

.content-area {
  background-color: var(--bg);
  padding: 0 !important;
  height: 100%;
  flex: 1;
  overflow-y: auto;
}

.logout-area {
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid #334155;
}

.logout-btn {
  width: 100%;
  border-radius: 8px;
  font-weight: bold !important;
  margin-top: 10px;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.el-main) {
  padding: 0 !important;
  margin: 0 !important;
  height: 100%;
}
</style>
