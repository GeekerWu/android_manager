<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <h2 class="title">User Profile</h2>
      </template>
      <div class="content">
        <el-table :data="user_data" border stripe style="width: 100%" :height="600">
          <el-table-column label="Field" prop="field" />
          <el-table-column label="Value" prop="value" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth';

const authStore = useAuthStore();

// Initial dummy data, easily replaceable with authStore.user
const user_data = ref([
  { field: 'Name', value: authStore.user?.username || 'Administrator' },
  { field: 'User Account', value: authStore.user?.username || 'admin' },
  { field: 'Gender', value: 'Male' }
]);
</script>

<style scoped>
.profile-container {
  padding: 24px;
}

.profile-card {
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  box-shadow: var(--shadow);
}

.title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-h);
}

.content {
  margin-top: 20px;
}

:deep(.el-table) {
  background-color: var(--surface);
}
</style>
