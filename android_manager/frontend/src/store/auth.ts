import { defineStore } from 'pinia';

/**
 * Pinia Store 定义：认证模块
 * 核心目的：将 Vuex Module 结构转换为 Pinia 的 Composition API Store。
 */
export const useAuthStore = defineStore('auth', {
  // --- 1. State (状态) ---
  state: () => ({
    token: null, // 状态存储访问 token
    user: null,    // 存储用户信息
    loading: false // 增加 loading 状态，以适配组件
  }),

  // --- 2. Getters (Getter) ---
  getters: {
    // 使用箭头函数形式，确保能访问到 state
    
    isAuthenticated: (state) =>{
      // console.log(state)
      return !!state.token
    } ,
    authToken: (state) => state.token,
    user: (state) => state.user,
  },

  // --- 3. Actions (业务逻辑和API调用) ---
  actions: {
    /**
     * 设置用户的认证 Token 和用户信息。
     * @param {object} payload 包含 'accessToken', 'token_type' 和 'userData' 的对象
     */
    loginSuccess({ payload }) {
      // 接收 payload 结构化数据，更安全
      this.token = payload.accessToken;
      this.user = payload.userData;
      this.loading = false;
      console.log('[AuthStore]: 认证状态更新成功。');
    },

    /**
     * 清除所有认证状态（用户主动登出）。
     */
    logout() {
      this.token = null;
      this.user = null;
      this.loading = false;
      console.log('[AuthStore]: 执行用户登出流程，清除所有状态。');
      // Pinia 不需要手动发射事件，状态变更自动触发响应式更新。
    }
  },
});