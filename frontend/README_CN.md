# Android Manager - 前端项目

这是一个基于 Vue 3 + TypeScript + Vite 构建的安卓管理系统前端界面。项目采用高度模块化的架构设计，旨在提供清晰的职责划分和高性能的交互体验。

## 🚀 技术栈
- **核心框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由管理**: Vue Router
- **UI 组件库**: Element Plus
- **图标库**: @element-plus/icons-vue

## 🏗 核心架构模式 (Architecture)
项目严格遵循**关注点分离 (Separation of Concerns)** 的三层架构设计，这是本项目的核心开发规范：

1.  **容器层 (Container Layer)**: 职责仅为**骨架**。主要组件（如 `App.vue`, `LayoutContainer.vue`）负责挂载 `<router-view>` 并提供基础布局。它们不包含任何业务逻辑判断。
2.  **路由层 (Routing Layer)**: 负责**流转管理与鉴权 (Guard)**。通过全局前置守卫 (`router/index.js`) 拦截导航，负责判断用户权限并处理跳转逻辑（如未登录用户导向登录页面）。
3.  **业务层 (Service/Store Layer)**: 负责**流程的原子化执行**。具体的业务逻辑（如登录请求、状态更新、表单处理）封装在 `services`、`store` 以及最内层的表现组件中。

## 🔑 认证流规范 (Auth Flow)
整个认证流程遵循以下解耦模式：
**用户触发 (组件) $\rightarrow$ 事件发出 $\rightarrow$ 状态更新 (Pinia Store) $\rightarrow$ 路由守卫感知状态 $\rightarrow$ 自动重定向。**

## 🛠 开发规范
- **图标渲染**: 严禁使用字符串拼接（如 `icon-ep-${item.iconname}`）来动态解析图标组件。这种方式在复杂的 UI 组件（如 `el-menu`）中容易导致组件解析失败。
- **优先使用组件引用**：在 `menuItems` 等数组定义中，应直接从 `@element-plus/icons-vue` 导入组件对象（如 `icon: User`）。
- **动态渲染模式**：在模板中使用 `<component :is="item.icon" />` 直接渲染导入的组件对象，以确保在动态加载和路由跳转时图标始终可见。
- **代码风格**: 优先使用函数式编程，变量命名遵循 `camelCase`（JS/TS）。
- **项目规范**: 修改前必须先理解整体架构，禁止在未确认的情况下进行大规模重构。

## 📂 项目结构概述

*   **`src/`**: 存放所有主要的源代码。
    *   `src/components/`: 包含可复用的 Vue 组件（如 `HelloWorld.vue`）。
    *   `src/assets/`: 存放项目使用的静态资源图片、图标等。
    *   `src/router/`: (推测) 存放 Vue Router 的路由配置。
    *   `src/main.js` 或 `src/App.vue`: 应用的入口文件。
*   **`public/`**: 存放部署时直接访问的静态文件，例如：
    *   `favicon.svg`: 网站图标。
    *   `icons.svg`: 通用图标集。
*   **`src/style.css`**: 项目的全局样式文件。
*   **`package.json`**: 定义项目元数据、依赖项和运行脚本。

## 📦 快速开始

### 1. 环境要求
确保您的开发环境中安装了以下工具：
*   Node.js (推荐使用 LTS 版本)
*   npm 或 yarn

### 2. 安装依赖
进入项目根目录，运行以下命令安装所有项目依赖：
```bash
npm install

3. 运行项目

运行开发模式以启动本地开发服务器。
npm run dev

4. 构建项目

当项目开发完成，需要部署到生产环境时，请运行构建命令：
npm run build