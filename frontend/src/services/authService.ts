import axios, { AxiosError } from 'axios';


// 💡 修正：根据实际 API 返回结构，AuthResponse 只包含 Token 相关的字段。
interface AuthResponse {
  access_token: string;
  token_type: string;
  // 完整的后端响应体结构，如果有其他字段（如 expires_in），也应该在这里定义。
}

/**
 * 使用提供的凭证执行登录 API 请求。
 *
 * @param username 用户名
 * @param password 密码
 * @returns Promise<AuthResponse>：如果成功则解析为包含 Token 的响应体；否则，Promise 会被 reject。
 */
export const loginUser = async (username: string, password: string): Promise<AuthResponse> => {
  const API_URL = `${import.meta.env.VITE_API_BASE_URL}/login`;
  // const API_URL = `http://localhost:8001/login`;

  // 模拟表单提交的结构化参数
  const formData = {
    grant_type: 'password',
    username: username,
    password: password,
    scope: '',
    client_id: '',
    client_secret: '',
  };

  const config = {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  };
  console.log('formData',formData)
  try {
    // 构造表单数据体
    const body = new URLSearchParams();
    for (const key in formData) {
        if (Object.prototype.hasOwnProperty.call(formData, key)) {
            body.append(key, String(formData[key]));
        }
    }

    // 发送请求
    const response = await axios.post(API_URL, body.toString(), config);

    // 检查响应状态码
    if (response.status === 200 && response.data) {
        // ✅ 修正：直接返回后端响应体，并进行类型断言。
        return response.data as unknown as AuthResponse;
    } else {
        // 状态码正常但数据结构错误，抛出业务错误
        throw new Error(response.data?.message || '登录请求成功，但返回数据格式不正确。');
    }

  } catch (error) {
    // 捕获网络错误、超时或4xx/5xx状态码错误
    if (axios.isAxiosError(error)) {
        // 尝试从错误响应中提取更具体的业务错误信息
        const errorDetails = error.response?.data || { message: '无法连接到登录服务。' };

        // 抛出包含清晰上下文的错误，让调用方可以区分是业务错误还是网络错误
        const authError = new Error(`[AUTH_ERROR] ${JSON.stringify(errorDetails)}`);
        (authError as any).isNetworkError = true; // 标记为网络错误，供上层逻辑判断
        throw authError;

    } else if (error instanceof Error) {
        // 捕获自定义抛出的业务错误 (例如: 格式错误)
        throw error;
    } else {
        // 捕获其他意外错误
        throw new Error('发生未知系统错误。');
    }
  }
}