<template>
  <div class="dashboard-container">
    <el-card class="dashboard-card">
      <template #header>
        <h2 class="title">DashBoard</h2>
      </template>
      <div class="content">
        <el-table :data="metrics" border stripe style="width: 100%" height="auto">
          <el-table-column prop="metric" label="Metric" />
          <el-table-column prop="value" label="Value" />
          <el-table-column label="Status">
            <template #default="scope">
              <el-tag :type="scope.row.statusType">
                {{ scope.row.statusText }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// TODO: Replace with real data from apiService
const metrics = ref([
  { metric: 'System Uptime', value: '142h 12m', statusText: 'Online', statusType: 'success' },
  { metric: 'Active Users', value: '1,284', statusText: 'Stable', statusType: 'success' },
  { metric: 'Server Load', value: '42%', statusText: 'Normal', statusType: 'warning' },
  { metric: 'Pending Tasks', value: '12', statusText: 'Pending', statusType: 'info' }
]);
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
}

.dashboard-card {
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

:deep(.el-table .el-table-header-wrapper) {
  background-color: var(--border);
}
</style>
