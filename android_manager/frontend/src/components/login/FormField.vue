<script setup lang="ts">
import { computed } from 'vue';

// 定义组件的 props
defineProps<{
  modelValue: string; // 当前绑定的值
  labelKey: string; // 用于显示标签的Key (例如 '用户名')
  placeholderKey: string; // 占位符的Key
  errorMessage: string | null; // 错误提示信息
  type: 'text' | 'password' | 'email'; // 输入框类型
  disabled: boolean; // 是否禁用
}>();

// 定义组件发出的事件
const emit = defineEmits(['update:modelValue', 'blur']);

// 计算属性：用于判断是否需要显示标签浮动效果
const isFocused = computed(() => false); // 这是一个简化，实际需要复杂的焦点管理
const isError = computed(() => !!props.errorMessage);

// 触发外部的 input 事件，并向上层组件触发更新
const emitValue = (event: Event) => {
  const target = event.target as HTMLInputElement;
  // 触发 v-model 的底层机制
  emit('update:modelValue', target.value);
};
</script>

<template>
  <div class="form-group">
    <!-- 标签区域 -->
    <label class="form-label">
      <!-- 浮动标签逻辑：当值改变或焦点时，label 应该向上移动 -->
      <span class="label-text">{{ labelKey }}</span>
      <!-- 可以在这里处理浮动标签的视觉逻辑 -->
    </label>

    <!-- 输入框容器，用来包裹输入框和错误信息 -->
    <div class="input-wrapper">
        <input
            :type="type"
            :value="modelValue"
            :placeholder="placeholderKey"
            :disabled="disabled"
            @input="emitValue($event)"
            @blur="$emit('blur')"
        />
        <!-- 错误消息 -->
        <p v-if="errorMessage && typeof errorMessage === 'string'" class="error-message">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<style scoped>
/* 整个组容器 */
.form-group {
    margin-bottom: 25px;
}

/* 标签样式 */
.form-label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #333;
}

/* 输入框的容器和浮动标签的实现是复杂的，这里提供基础骨架，实现真正的浮动标签需要更复杂的 ::after/::before 伪元素处理。
   这里我先采用增强了阴影和圆角的普通样式作为替代。 */
.input-wrapper input {
    width: 100%;
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-sizing: border-box;
    font-size: 16px;
    transition: border-color 0.2s, box-shadow 0.2s;
}

/* 聚焦时的样式增强（提升专业感） */
.input-wrapper input:focus:not(:disabled) {
    border-color: #42b883; /* 品牌主色 */
    box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.2); /* 焦点高亮阴影 */
    outline: none;
}

/* 禁用状态 */
.input-wrapper input:disabled {
    background-color: #eee;
    cursor: not-allowed;
}

/* 错误提示 */
.error-message {
    color: #e74c3c;
    font-size: 0.85em;
    margin-top: 5px;
}
</style>