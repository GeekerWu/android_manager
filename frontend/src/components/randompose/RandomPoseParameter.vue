<template>
  <div class="random-pose-container">
    <el-card class="random-pose-card">
      <template #header>
        <h2 class="title">Random Pose Parameter</h2>
      </template>
      <div class="content">
        <div class="action-bar">
          <el-button type="primary" @click="handleCreate">新增记录</el-button>
          <el-button type="danger" :disabled="!selectedIds.length" @click="handleBatchDelete">批量删除</el-button>
        </div>
        <el-table
          :data="parameters"
          border
          stripe
          style="width: 100%"
          height="auto"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="servo_id" label="Servo ID" width="100" />
          <el-table-column prop="servo_desc" label="Description" />
          <el-table-column prop="servo_type" label="Type" />
          <el-table-column prop="mini_position" label="Min Position" />
          <el-table-column prop="max_position" label="Max Position" />
          <el-table-column prop="random_rate" label="Random Rate" width="150">
            <template #default="scope">
              <el-input
                v-if="editingId === scope.row.servo_id"
                v-model.number="scope.row.random_rate"
                size="small"
                @blur="editingId = null"
                @keyup.enter="editingId = null"
                @keyup.tab="editingId = null"
                style="width: 100%"
              />
              <span v-else>{{ scope.row.random_rate.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="target_position" label="Target Position" />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="scope">
              <el-button 
                :type="editingId === scope.row.servo_id ? 'danger' : 'warning'"
                :icon="editingId === scope.row.servo_id ? Lock : Edit"
                size="med"
                @click="toggleEdit(scope.row.servo_id)"
              >
                {{ editingId === scope.row.servo_id ? '完成' : '单条编辑' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-dialog
        v-model="dialogVisible"
        :title="dialogTitle"
        width="800px"
        :close-on-click-outside="false"
        destroy-on-close
      >
        <ParameterForm
          :initialData="newRecord"
          @submit="handleCreateSubmit"
          @cancel="handleClose"
        />
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import {Edit, Lock} from '@element-plus/icons-vue';
import ParameterForm from './ParameterForm.vue';

interface RandomPoseParameter {
  servo_id: number;
  servo_desc: string;
  servo_type: string;
  mini_position: number;
  max_position: number;
  random_rate: number;
  target_position: number;
}

const parameters = ref<RandomPoseParameter[]>([]);
const servoOptions = ref<{ id: number, name: string }[]>([]);

const dialogVisible = ref(false);
const dialogTitle = ref('新增记录');
const editingId = ref<number | null>(null);
const selectedIds = ref<number[]>([]);

const newRecord = ref<RandomPoseParameter>({
  servo_id: 0,
  servo_desc: '',
  servo_type: 'Rotation',
  mini_position: 0,
  max_position: 0,
  random_rate: 0.00,
  target_position: 0,
});

// --- 数据请求逻辑 ---

const fetchData = async () => {
  try {
    // 1. 获取所有电机列表供下拉框使用
    // TODO: Replace with real API call: fetch('/api/servos')
    setTimeout(() => {
      servoOptions.value = [
        { id: 1, name: 'Base Joint 1' },
        { id: 2, name: 'Base Joint 2' },
        { id: 3, name: 'Arm Joint 1' },
        { id: 4, name: 'Arm Joint 2' },
      ];
    }, 300);

    // 2. 获取当前页面所有的参数列表
    // TODO: Replace with real API call: fetch('/api/random-pose')
    setTimeout(() => {
      parameters.value = [
        { servo_id: 1, servo_desc: 'Base Joint 1', servo_type: 'Rotation', mini_position: -90, max_position: 90, random_rate: 0.50, target_position: 0 },
        { servo_id: 2, servo_desc: 'Base Joint 2', servo_type: 'Rotation', mini_position: -90, max_position: 90, random_rate: 0.30, target_position: 0 },
        { servo_id: 3, servo_desc: 'Arm Joint 1', servo_type: 'Rotation', mini_position: -45, max_position: 45, random_rate: 0.10, target_position: 0 },
        { servo_id: 4, servo_desc: 'Arm Joint 2', servo_type: 'Rotation', mini_position: -45, max_position: 45, random_rate: 0.10, target_position: 0 },
      ];
    }, 600);
  } catch (e) {
    console.error("Failed to fetch initial data", e);
  }
};

onMounted(() => {
  fetchData();
});

// --- 交互逻辑 ---

const handleSelectionChange = (selection: any[]) => {
  selectedIds.value = selection.map(item => item.servo_id);
};

const handleCreate = () => {
  newRecord.value = {
    servo_id: parameters.value.length > 0 ? Math.max(...parameters.value.map(p => p.servo_id)) + 1 : 1,
    servo_desc: '',
    servo_type: 'Rotation',
    mini_position: 0,
    max_position: 0,
    random_rate: 0.00,
    target_position: 0,
  };
  dialogVisible.value = true;
};

const handleCreateSubmit = (data: RandomPoseParameter) => {
  // TODO: Replace with real API call: POST /api/random-pose
  parameters.value.push(data);
  dialogVisible.value = false;
};

const handleClose = () => {
  dialogVisible.value = false;
};

// --- 编辑逻辑 ---
const toggleEdit = (id: number) => {
  if (editingId.value === id) {
    editingId.value = null;
  } else {
    editingId.value = id;
  }
};

const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) return;

  // TODO: Replace with real API call: DELETE /api/random-pose/batch
  console.log('Request to Delete IDs:', selectedIds.value);

  // 模拟成功逻辑
  parameters.value = parameters.value.filter(p => !selectedIds.value.includes(p.servo_id));
  selectedIds.value = [];
};
</script>

<style scoped>
.random-pose-container {
  padding: 24px;
}

.random-pose-card {
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

.action-bar {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}

:deep(.el-table) {
  background-color: var(--surface);
}

:deep(.el-table .el-table-header-wrapper) {
  background-color: var(--border);
}
</style>
