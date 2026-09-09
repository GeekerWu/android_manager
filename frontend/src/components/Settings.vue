<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <h2 class="title">Settings</h2>
      </template>
      <div class="content">
        <el-table :data="settings" border stripe style="width: 100%">
          <el-table-column label="Configuration Item" prop="item" />
          <el-table-column label="Status" prop="status" />
          <el-table-column label="Action" width="150">
            <template #default="scope">
              <el-button size="small" @click="handleAction(scope.row.item)">
                {{ scope.row.action_text }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
const settings = [
  { item: 'Display Mode', status: 'Light / Dark / Auto', action_text: 'Change' },
  { item: 'Notifications', status: 'Enabled', action_text: 'Toggle' },
  { item: 'Privacy Level', status: 'Public', action_text: 'Adjust' },
  { item: 'Data Sync', status: 'Active', action_text: 'Sync Now' }
];

const handleAction = (item) => {
  console.log('Action for:', item);
};
</script>

<style scoped>
.settings-container {
  padding: 24px;
}

.settings-card {
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
