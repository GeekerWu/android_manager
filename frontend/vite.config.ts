import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// vite.config.ts
// 此文件用于配置 Vite 构建工具的行为。
// 所有的开发和构建设置都在这里定义。

// https://vite.dev/config/
export default defineConfig({
  // plugins: 插件数组，引入项目使用的构建插件。
  plugins: [vue()],

  // resolve: 解析器配置，用于设置路径别名。
  resolve: {
    alias: {
      // @ 别名指向 src 目录，方便在代码中全局引用 '@/components/...'
      '@': path.resolve(import.meta.dirname, './src')
    }
  },

  // server: 开发服务器配置。
  server: {
    // port: 设置开发服务器运行的端口号。
    // 在这里修改 port 的值，即可更改开发环境访问的端口。
    port: 8088
  }
})