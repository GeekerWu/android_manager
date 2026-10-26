<template>
  <el-form
    :model="formData"
    :rules="rules"
    ref="formRef"
    label-width="140px"
    :validate-on-rules-change="true"
  >
    <el-row :gutter="20">
      <!-- 第一行：ID 和 Description -->
      <el-col :span="8">
        <el-form-item label="Servo ID" prop="servo_id">
          <el-input v-model.number="formData.servo_id" placeholder="Enter ID" />
        </el-form-item>
      </el-col>
      <el-col :span="16">
        <el-form-item label="Description" prop="servo_desc">
          <el-select
            v-model="formData.servo_desc"
            filterable
            clearable
            placeholder="Select a servo"
            :loading="loading"
            @change="handleServoChange"
            style="width: 100%"
          >
            <el-option
              v-for="item in servoOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 第二行：Type, Min, Max -->
      <el-col :span="8">
        <el-form-item label="Type" prop="servo_type">
          <el-select v-model="formData.servo_type" placeholder="Select Type" style="width: 100%">
            <el-option label="SCS" value="scs" />
            <el-option label="STS" value="sts" />
            <el-option label="Other" value="Other" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Min Position" prop="mini_position">
          <el-input v-model.number="formData.mini_position" placeholder="e.g. -90" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Max Position" prop="max_position">
          <el-input v-model.number="formData.max_position" placeholder="e.g. 90" />
        </el-form-item>
      </el-col>
    </el-row>

    <div style="margin-top: 32px; display: flex; justify-content: flex-end; gap: 12px;">
      <el-button @click="cancel">取消</el-button>
      <el-button type="primary" @click="submitForm">提交</el-button>
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';

interface ParameterData {
  servo_id: number;
  servo_desc: string;
  servo_type: string;
  mini_position: number;
  max_position: number;
  random_rate: number;
  target_position: number;
}

const props = defineProps<{
  initialData?: ParameterData;
  title?: string;
}>();

const emit = defineEmits(['submit', 'cancel']);

const formRef = ref();
const loading = ref(false);

// 下拉框数据源
const servoOptions = ref<{ id: number, name: string }[]>([]);

const formData = reactive<ParameterData>({
  servo_id: 0,
  servo_desc: '',
  servo_type: 'scs',
  mini_position: 0,
  max_position: 0,
  random_rate: 0.00,
  target_position: 0,
});

const rules = {
  servo_id: [{ required: true, message: 'Required', trigger: 'blur' }],
  servo_desc: [{ required: true, message: 'Please select a servo', trigger: 'change' }],
  servo_type: [{ required: true, message: 'Required', trigger: 'change' }],
  mini_position: [{ required: true, message: 'Required', trigger: 'blur' }],
  max_position: [{ required: true, message: 'Required', trigger: 'blur' }],
};

// Initialize form data
onMounted(async () => {
  if (props.initialData) {
    Object.assign(formData, props.initialData);
  }

  // 加载电机列表用于下拉框
  await fetchServoOptions();
});

// 模拟获取所有电机列表
const fetchServoOptions = async () => {
  loading.value = true;
  try {
    // TODO: Replace with real API call: fetch('/api/servos')
    setTimeout(() => {
      servoOptions.value = [
        { id: 1, name: 'Base Joint 1' },
        { id: 2, name: 'Base Joint 2' },
        { id: 3, name: 'Arm Joint 1' },
        { id: 4, name: 'Arm Joint 2' },
      ];
      loading.value = false;
    }, 500);
  } catch (e) {
    loading.value = false;
    console.error("Failed to fetch servo options", e);
  }
};

// 当下拉框选择电机时触发
const handleServoChange = async (val: number) => {
  if (!val) return;

  loading.value = true;
  try {
    // TODO: 模拟根据电机 ID 获取该电机的默认/关联参数
    // TODO: Replace with real API call: fetch(`/api/servos/${val}`)
    setTimeout(() => {
      // 模拟从后台获取到的数据填充到表单
      formData.mini_position = -90;
      formData.max_position = 90;
      formData.target_position = 0;
      formData.random_rate = 0.00;
      loading.value = false;
    }, 500);
  } catch (e) {
    loading.value = false;
    console.error("Failed to fetch servo details", e);
  }
};

const submitForm = async () => {
  if (!formRef.value) return;
  await formRef.value.validate((valid) => {
    if (valid === 'success') {
      emit('submit', { ...formData });
    }
  });
};

const cancel = () => {
  emit('cancel');
};
</script>
