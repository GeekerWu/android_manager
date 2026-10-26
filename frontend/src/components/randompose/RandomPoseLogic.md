# RandomPose 页面逻辑文档 (Draft)

## 1. 页面概览
本页面用于管理和配置机器人的“随机姿态”参数。用户可以在此查看现有的参数列表，添加新的记录，或对现有记录进行单条编辑及批量删除。

## 2. 核心 UI 组件结构
- **Container**: `random-pose-container` 容器，提供基础内边距。
- **Card**: `random-pose-card` 卡片容器，包含标题和操作区域。
- **Action Bar**: 包含“新增记录”和“批量删除”按钮。
- **Data Table**: `el-table` 展示参数列表。
- **Dialog**: 包含 `ParameterForm` 的弹窗，用于新增或编辑数据。

## 3. API 接口规划
- 只考虑用POST，GET请求方式，数据格式用json

| 功能 | 方法 | 路径 (拟定) | 描述 | 数据实例 (JSON) |
| :--- | :--- | :--- | :--- | :--- |
| 查询列表 | `GET` | `/api/randompose/search_randompose` | 获取所有随机姿态参数 | `{"page": 1, "pageSize": 10}` |
| 下拉框数据 | `GET` | `/api/randompose/getdropdown_randompose` | 获取所有电机列表 | `[]` (Response: `[{"id":1, "name":"..."}]`) |
| 新增创建 | `POST` | `/api/randompose/add_randompose` | 创建新记录| `{"servo_id": 5, "servo_desc": "...", "servo_type": "Rotation", "mini_position": -45, "max_position": 45, "random_rate": 0.15, "target_position": 0}` |
| 单条编辑 | `POST` | `/api/randompose/edit_randompose/` | 更新特定记录 | `{"servo_id": 1, "servo_desc": "...", "servo_type": "Rotation", "mini_position": -100, "max_position": 100, "random_rate": 0.6, "target_position": 0}` |
| 批量删除 | `POST` | `/api/randompose/delete_randompose` | 批量移除记录 | `{"ids": [1, 2, 3]}` |

## 4. 业务逻辑流程

### 4.1 初始化加载
- 页面挂载时 (`onMounted`)：
    - 同时请求“下拉框数据”和“查询列表”。
    - 成功后更新 `parameters` 和 `servoOptions`。
    - 失败时在控制台记录错误。

### 4.2 新增记录逻辑
1. **触发**：点击“新增记录”。
2. **准备数据**：计算新的 `servo_id`，初始化 `newRecord` 对象。
3. **展示界面**：显示 `el-dialog` 及其内部的 `ParameterForm`。
4. **提交数据**：
    - 用户提交 $\rightarrow$ 调用“新增创建”接口。
    - 成功 $\rightarrow$ 推送到本地 `parameters` 数组，关闭对话框。

### 4.3 单条编辑逻辑
1. **进入编辑**：点击操作栏“单条编辑”。
    - 设置 `editingId` 为对应行的 `servo_id`。
    - UI 响应：对应行的 `random_rate` 显示为 `el-input`。
2. **保存编辑**：点击“完成”按钮。
    - 调用“单条编辑”接口。
    - 成功 $\rightarrow$ 更新本地 `parameters` 数组，将 `editingId` 置为 `null`。

### 4.4 批量删除逻辑
1. **触发**：勾选多项 $\rightarrow$ 点击“批量删除”。
2. **校验**：检查 `selectedIds` 是否非空。
3. **执行**：
    - 调用“批量删除”接口。
    - 成功 $\rightarrow$ 从本地 `parameters` 数组中过滤掉已删除项，清空 `selectedIds`。

## 5. 状态变量说明
- `parameters`: 存储所有参数记录的响应数组。
- `servoOptions`: 存储用于下拉框选择的电机列表。
- `dialogVisible`: 控制新增/编辑弹窗的可见性。
- `editingId`: 当前处于编辑状态的记录 ID（为 null 时表示无正在编辑的）。
- `selectedIds`: 存储用户在表格中勾选的 ID 列表。
- `newRecord`: 构造用于新增的初始数据对象。

## 6. API 数据实例 (Data Samples)

### 6.1 查询列表 (GET `/api/randompose/search_randompose`)
**请求参数 (Query Params):**
```json
{
  "page": 1,
  "pageSize": 20,
  "servo_id": 1
}
```
**响应数据 (Response Body):**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "servo_id": 1,
      "servo_desc": "Base Joint 1",
      "servo_type": "Rotation",
      "mini_position": -90,
      "max_position": 90,
      "random_rate": 0.50,
      "target_position": 0
    },
    {
      "servo_id": 2,
      "servo_desc": "Base Joint 2",
      "servo_type": "Rotation",
      "mini_position": -90,
      "max_position": 90,
      "random_rate": 0.30,
      "target_position": 0
    },
    {
      "servo_id": 3,
      "servo_desc": "Arm Joint 1",
      "servo_type": "Rotation",
      "mini_position": -45,
      "max_position": 45,
      "random_rate": 0.10,
      "target_position": 0
    }
  ]
}
```

### 6.2 下拉框数据 (GET `/api/randompose/getdropdown_randompose`)
**响应数据 (Response Body):**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    { "id": 1, "name": "Base Joint 1" },
    { "id": 2, "name": "Base Joint 2" },
    { "id": 3, "name": "Arm Joint 1" },
    { "id": 4, "name": "Arm Joint 2" }
  ]
}
```

### 6.3 新增创建 (POST `/api/randompose/add_randompose`)
**请求体 (Request Body):**
```json
{
  "servo_id": 5,
  "servo_desc": "New Joint Record",
  "servo_type": "Rotation",
  "mini_position": -120,
  "max_position": 120,
  "random_rate": 0.25,
  "target_position": 0
}
```
**响应数据 (Response Body):**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "servo_id": 5,
    "servo_desc": "New Joint Record",
    "servo_type": "Rotation",
    "mini_position": -120,
    "max_position": 120,
    "random_rate": 0.25,
    "target_position": 0
  }
}
```

### 6.4 单条编辑 (POST `/api/randompose/edit_randompose/`)
**请求体 (Request Body):**
```json
{
  "servo_id": 1,
  "servo_desc": "Updated Base Joint 1",
  "servo_type": "Rotation",
  "mini_position": -100,
  "max_position": 100,
  "random_rate": 0.75,
  "target_position": 10
}
```
**响应数据 (Response Body):**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "servo_id": 1,
    "servo_desc": "Updated Base Joint 1",
    "servo_type": "Rotation",
    "mini_position": -100,
    "max_position": 100,
    "random_rate": 0.75,
    "target_position": 10
  }
}
```

### 6.5 批量删除 (POST `/api/randompose/delete_randompose`)
**请求体 (Request Body):**
```json
{
  "ids": [1, 3, 5]
}
```
**响应数据 (Response Body):**
```json
{
  "code": 200,
  "message": "success",
  "data": true
}
```
