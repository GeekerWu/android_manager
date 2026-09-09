import { defineStore } from 'pinia';

/**
 * Pinia Store 定义：认证模块
 */
export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    user: null,
    loading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    authToken: (state) => state.token,
    userData: (state) => state.user,
  },

  actions: {
    /**
     * 设置用户的认证 Token 和用户信息。
     */
    async loginSuccess({ payload }) {
      try {
        this.loading = true;
        // In a real app, you'd call your API here.
        // For now, we simulate a successful API response.
        this.token = payload.accessToken;
        this.user = payload.userData;
        this.loading = false;
        console.log('[AuthStore]: 认证状态更新成功。');

        // 修复：$subscribe 的 mutation 必须是一个函数
        this.$subscribe((mutation, state) => {
          if (mutation.type === 'setAuthStatus') {
            console.log('[AuthStore]: 状态订阅触发:', mutation.payload);
            // 这里可以处理路由跳转等副作用
          }
        });
      } catch (error) {
        this.loading = false;
        console.error('[AuthStore]: 登录失败', error);
        throw error;
      }
    },

    /**
     * 清除所有认证状态。
     */
    logout() {
      this.token = null;
      this.user = null;
      this.loading = false;
      console.log('[AuthStore]: 执行用户登出流程。');

      this.$subscribe((mutation, state) => {
        if (mutation.type === 'setAuthStatus') {
          console.log('[AuthStore]: 状态订阅触发:', mutation.payload);
        }
      });
    }
  },
});