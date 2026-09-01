# 🏆 最终项目架构蓝图：[项目名称] 技术文档生成缓存 (Architecture Blueprint v1.0)

**缓存目的:** 存储整个项目架构分析和文档规划的最高层级概览，确保所有后续文档撰写和代码重构都锚定在这一份权威的、经用户批准的蓝图上。

---

## 🏛️ 第一部分：项目架构蓝图 (The Blueprint)

### 🧩 架构分层与依赖图 (Component Hierarchy & Dependency Graph)

**总览:** 采用标准的 Vue 3 单页应用（SPA）架构，组件依赖关系层层递进，数据流通过状态管理中心化控制。

**层级关系:**
1.  **根容器层 (`App.vue`):** 负责全局布局和应用生命周期的初始化调用。
2.  **路由与控制层 (`router/index.js`):** 负责路由拦截和状态校验的“门卫”。
3.  **页面容器层 (`Login.vue`, `DashboardContainer.vue`):** 负责根据路由和状态，组织和编排业务组件。
4.  **业务逻辑层 (Service/Store):** 抽象出所有核心业务能力（如 Auth、API 调用）。
5.  **展示层 (Presentation):** 纯展示和输入，无业务逻辑，只负责展现和触发事件。

**核心依赖流:**
`Router Guard` $\xrightarrow{\text{reads state from}}$ `AuthStore` $\rightarrow$ `AuthService` $\xrightarrow{\text{calls}}$ `ApiService` $\rightarrow$ `Component` 渲染。

### 🌊 状态流图：用户完整生命周期 (State Machine)
（用户从未登录 $\rightarrow$ Dashboard）

1.  **[State: Unauthenticated]** $\xrightarrow{\text{Trigger: Access Protected Route}}$
2.  **[Action: Router Guard Check]** $\xrightarrow{\text{Condition: !Token in Store}}$
3.  **[Transition: Redirect]** $\rightarrow$ 强制跳转到 `/login`。
4.  **[State: Login Form View]** $\xrightarrow{\text{Trigger: Submit Credentials}}$
5.  **[Action: Call AuthService.login()]** $\rightarrow$ API 调用 $\rightarrow$ 成功 $\rightarrow$ `localStorage` 写入 Token $\rightarrow$ **Store 更新状态**。
6.  **[State: Authenticated]** $\xrightarrow{\text{Trigger: Router Guard Re-check}}$
7.  **[Transition: Route Change]** $\rightarrow$ 渲染 `/home` (Dashboard)。
8.  **[State: Dashboard Active]** $\xrightarrow{\text{Trigger: Component Mount/Data Refresh}}$ **调用 ApiService** $\rightarrow$ 获取数据 $\rightarrow$ 渲染。

### 🧱 关键技术模块边界定义 (Mandatory Modules)

为解耦状态管理，必须拆分出以下三个独立的、高内聚的模块：

1.  **`src/store/authStore.ts` (Pinia/Vuex Store):**
    *   **职责:** 维护 `isAuthenticated`, `user`, `token`, `isLoading` 等全局状态。
    *   **核心方法:** `login(payload)`, `logout()`, `checkStatus()`.
2.  **`src/services/apiService.ts` (Network Abstraction):**
    *   **职责:** 封装所有 HTTP 通信，处理通用拦截器（Token注入、全局错误捕获）。
3.  **`src/services/authService.ts` (Business Logic):**
    *   **职责:** 包含与后端直接对话的业务逻辑（如执行一次完整的登录验证，它负责调用 `ApiService`，并将结果写入 `AuthStore`）。

---
## 📘 第二部分：最终文档撰写大纲 (Drafting Outline)

根据上述架构，推荐的文档结构如下：

**[文档总标题]: [项目名称] 技术文档**

### 🌐 I. 项目概述与上手指南 (Getting Started)
*   **A. 项目目标:** 描述项目解决的核心业务痛点。
*   **B. 技术选型与依赖:** 详细解释 Vue 3, Vite, Pinia, Element Plus 的选用理由。
*   **C. 环境搭建:** 步骤列表（Step-by-step guide）。

### 📐 II. 架构设计 (Architecture Design)
*   **A. 组件分层模型:** 详细图解，说明哪个组件负责哪个业务块。
*   **B. 状态控制流:** 详细描述 State Machine，并用流程图（流程图代码）展示用户旅程。
*   **C. 边界划分原则:** 阐述“为什么我们必须将 Auth 逻辑移到 Store/Service 层”。

### 📞 III. API 接口参考 (API Reference)
*   **目标:** 这是一个必须填满的章节。
*   **内容:** 必须按组分类 (e.g., `Auth Group`, `User Group`)，包含所有 API 的 Endpoint, Method, Request Body Schema, Response Schema。

---
**⚠️ 最终结论与待办事项 (Action Items)**
1.  **核心修改点:** 将所有 `localStorage` 操作替换为 **Store 状态读写**。
2.  **下一步:** 我已为您生成了完善的蓝图和文档大纲。请您审阅此文件，确认架构模型无误。确认后，我将进入 **【阶段 3: 文档初稿撰写】**。