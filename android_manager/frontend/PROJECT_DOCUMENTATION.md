   
  ---🚀 文档交付 (Final Delivery)

  [项目名称] - 技术文档 (Project Documentation)
  版本: 1.0 (Final Blueprint Draft)
  状态: 待 QA 审核 (Ready for Code Implementation)
  创建日期: 2026/08/26
  来源: 架构设计规划 (Architecture Blueprint v1.0)
  
  ---
  🎯 摘要 (Executive Summary)

  本项目是一个基于 Vue 3 和 TypeScript 的单页应用 (SPA)，其核心目标是构建一个健壮、可扩展的用户认证和仪表盘系统。本次重构的关键核心是将所有状态管理从分散的 localStorage 和组件事件，强制提升到 Pinia/Vuex       
  Store，实现单一的、可观察的真相来源 (Single Source of Truth)。

  ---
  📐 I. 架构设计 (Architecture Design)

  🧩 1.1. 组件分层与依赖图 (Component Hierarchy & Dependency Graph)

  （此处需插入专业流程图）
  架构遵循经典的三层分离：容器层 $\rightarrow$ 业务逻辑层 $\rightarrow$ 展示层。
  - 根容器层 (App.vue): 职责：应用的骨架，只负责布局和路由挂载。
  - 控制层 (router/index.js): 职责：作为应用的中央拦截器，它不再自己存储状态，而是询问 Store 状态。
  - 业务层 (Store/Service): 职责：所有状态改变、API调用、业务规则的唯一执行方。
  - 展示层 (Component): 职责：仅负责展示和捕获用户输入，保持纯净。

  🔄 2. 状态控制流 (State Flow State Machine)

  （此部分的状态流图的逻辑，将作为流程图代码嵌入，确保流程的原子性和可追溯性）

  关键流程: 从未登录到Dashboard 激活的整个旅程，状态机流转是整个项目设计的基石，我们必须确保流程图的每一步（特别是触发器和状态变化）都是由Store 驱动的。

  🧱 3. 关键技术模块边界 (Mandatory Modules)

  为了确保代码质量，我们必须硬性划分以下三个边界：

  1. src/store/authStore.ts (Pinia/Vuex Store):
    - 唯一职能: 维护 isAuthenticated, user, token, isLoading。
    - 核心方法: login(payload), logout()。
  2. src/services/apiService.ts (Network Abstraction):
    - 唯一职能: 封装所有 HTTP 通信。任何网络请求必须通过它。
    - 关键实现: 必须实现请求和响应的全局拦截器，用于自动注入 Token 和统一处理 401/500 错误。
  3. src/services/authService.ts (Business Logic):
    - 唯一职能: 封装所有与业务逻辑相关的调用。它调用 ApiService，然后负责根据 API 返回的结果，触发对 AuthStore 的状态更新。

  ---📞 III. API 接口参考 (API Reference)

  (此部分内容保持占位，需要后端补充，结构已定义)

  接口组: 认证服务 (AuthService)
  - Endpoint: /api/v1/auth/login | Method: POST
  - ... (此处应完整填入 API 的所有Schema定义)

  接口组: 仪表盘数据 (DashboardService)
  - Endpoint: /api/v1/dashboard/summary | Method: GET
  - ... (此处应完整填入 API 的所有Schema定义)

  ---🛠️ IV. 代码重构路线图 (Actionable Roadmap)

  ┌───────────┬───────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────┬────────────────────────────┐
  │  优先级   │           模块/文件           │                                    任务描述                                     │      依赖关系/关键点       │
  ├───────────┼───────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────┼────────────────────────────┤
  │ P1 (最高) │ src/store/authStore.ts        │ 建立 Pinia Store，实现所有状态的唯一来源。                                      │ N/A                        │
  ├───────────┼───────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────┼────────────────────────────┤
  │ P1 (最高) │ src/services/apiService.ts    │ 封装网络请求逻辑，实现所有通用拦截器。                                          │ N/A                        │
  ├───────────┼───────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────┼────────────────────────────┤
  │ P1 (最高) │ src/services/authService.ts   │ 实现完整的业务流程，连接 API $\rightarrow$ Store。                              │ 依赖 ApiService, AuthStore │
  ├───────────┼───────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────┼────────────────────────────┤
  │ P2 (中等) │ src/router/index.js           │ 将所有 localStorage 读取替换为 authStore 的状态读取。                           │ 依赖 AuthStore             │
  ├───────────┼───────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────┼────────────────────────────┤
  │ P3 (低)   │ src/components/HelloWorld.vue │ 在 onMounted 钩子中调用 AuthService 来加载初始数据，并处理 Loading/Error 状态。 │ 依赖 AuthService           │
  └───────────┴───────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────┴────────────────────────────┘

