/**
 * src/services/apiService.ts
 * 描述: 所有与后端API的通信的唯一抽象层。所有网络请求必须通过此服务。
 * 遵循拦截器模式，实现Token自动注入和全局错误捕获。
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

/**
 * 初始化并配置所有的网络请求实例。
 * @returns {AxiosInstance} 配置完成的 Axios 实例。
 */
export const apiService: AxiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001', // 从环境变量获取，提供本地默认值 fallback

    timeout: 15000, // 15秒超时
    headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
});

/**
 * 全局请求拦截器 (Request Interceptor)
 * 目的: 确保所有请求都携带有效的 Token。
 * @param {AxiosRequestConfig} config - 请求配置对象
 */
apiService.interceptors.request.use(
    (config) => {
        // ⚠️ 模拟逻辑: 在真实的 Pinia/Vuex环境下，我们应该从 Store 获取 Token。
        // 这里暂时使用 localStorage 进行模拟，直到Store层完善。
        const token = localStorage.getItem('authToken');

        if (token) {
            console.log("[ApiService] 拦截器: 成功注入 Token 到请求头。");
            // 实际操作：配置请求头
            config.headers = {
                ...config.headers,
                'Authorization': `Bearer ${token}`
            };
        } else {
            console.warn("[ApiService] 警告: 请求缺乏 Token，可能导致认证失败。");
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

/**
 * 全局响应拦截器 (Response Interceptor)
 * 目的: 统一处理所有后端返回的通用错误码。
 * @param {AxiosResponse<any>} response - 服务器成功响应的数据。
 * @param {AxiosInstance} apiService - 当前的 Axios 实例。
 */
apiService.interceptors.response.use(
    (response) => {
        console.log("[ApiService] 拦截器: 请求成功，返回数据。");
        return response.data; // 返回数据体，供上层业务逻辑使用
    },
    (error) => {
        // ⚠️ 核心错误处理逻辑：这是最关键的审计点。
        if (error.response) {
            const status = error.response.status;
            console.error(`[ApiService] 响应错误: ${status}`, error.response.data);

            if (status === 401) {
                console.warn("--- 🛑 发现 401 错误，强制执行全局登出流程 (Logout)。 ---");
                // 实际操作: 触发一个全局的登出状态变更事件或调用 Store 的 logout 方法。
            }
            // 统一抛出错误，让上层业务逻辑捕获，避免崩溃。
            return Promise.reject(error.response.data);
        } else if (error.request) {
            // 网络错误
            console.error("[ApiService] 网络错误: 未收到响应。", error.message);
            throw new Error("网络连接失败，请检查网络环境。");
        } else {
            // 其他错误
            throw new Error(`发生未知错误: ${error.message}`);
        }
    }
);

// 导出类型和实例
export { apiService };