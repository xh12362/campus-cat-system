# 基于 YOLO 的校园流浪猫识别与档案系统

一个面向校园流浪猫场景的 Web 系统。用户可以上传猫咪照片并填写发现信息，系统会进行猫检测、返回相似猫推荐，并支持后续建立或查看猫档案。

当前仓库已经完成第一阶段可运行闭环，并且针对样本猫映射、上传流程、测试数据清理做了多轮收口。现在的重点不再只是“能跑起来”，而是“能稳定演示、能继续维护、能逐步产品化”。

## 当前状态

当前主链路已经可以跑通：

`上传照片 -> 猫检测 -> 裁剪猫图 -> 相似猫推荐 -> 用户决定是否新增档案 -> 浏览档案`

和早期版本相比，目前有这些关键变化：

- AI 服务已接入样本目录读取和轻量相似匹配
- 相似猫推荐支持稳定返回 Top-K 候选
- 样本编号不再和数据库主键强绑定
- 样本猫通过 `dataset_cat_code` 与数据库档案稳定映射
- 上传时不再默认自动新建档案
- 用户可以先看识别结果和推荐，再决定是否新增档案
- 普通档案列表默认只显示 `real` 数据来源
- 部分测试数据已从当前库中清理

## 已实现能力

### 上传与识别

- 上传猫咪照片
- 填写发现地点、时间、备注
- 调用 AI 服务执行猫检测
- 返回检测结果与裁剪图路径
- 保存图片记录与发现记录

### 相似猫推荐

- AI 服务读取 `datasets/cat_profiles.csv` 和 `datasets/north/`
- 基于轻量图像特征返回相似猫 Top-K
- 返回字段包括：
  - `sample_cat_code`
  - `cat_profile_id`
  - `cat_name`
  - `similarity_score`
  - `reason`

### 档案流程

- 已有档案可继续关联新的发现记录
- 当系统未关联到现有档案时，不再直接自动建档
- 前端提供按钮，由用户决定是否“新增档案”
- 新建档案后，会把本次图片和发现记录正式绑定到新档案

### 数据治理

- `cat_profile` 已支持：
  - `dataset_cat_code`
  - `profile_source`
- 当前使用的数据来源类型：
  - `real`
  - `sample`
  - `test`
- 档案列表默认只展示 `real`
- `sample` 仍可供 AI 推荐映射使用

## 技术栈

### 前端

- Vue 3
- Vite

### 后端

- FastAPI
- SQLAlchemy
- PyMySQL

### AI 服务

- Ultralytics YOLO
- Pillow
- NumPy

### 数据库与部署

- MySQL 8
- Docker Compose

## 系统结构

项目包含 4 个核心服务：

- `frontend`：前端页面，默认端口 `5173`
- `backend`：业务后端，默认端口 `8000`
- `ai-service`：AI 检测与推荐服务，默认端口 `8001`
- `mysql`：数据库服务

目录结构概览：

```text
.
├─ frontend/              # Vue 前端
├─ backend/               # FastAPI 后端
├─ ai-service/            # AI 检测与推荐服务
├─ mysql/
│  ├─ init/               # MySQL 初始化 SQL
│  └─ migrations/         # 数据迁移脚本
├─ datasets/              # 样本猫元数据与样本图片
├─ uploads/
│  ├─ original/           # 原始上传图片
│  └─ cropped/            # 裁剪后的猫图
├─ models/                # YOLO 模型权重
├─ docs/                  # 文档
├─ docker-compose.yml
└─ README.md
```

## 快速开始

### 1. 准备环境

确保本机已安装并启动：

- Docker Desktop

准备 YOLO 模型文件：

```text
models/yolov8n.pt
```

### 2. 配置环境变量

第一次运行前复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

如果本机已有 MySQL 占用 `3306`，可以在 `.env` 中调整：

```env
MYSQL_PORT=3307
```

### 3. 启动服务

在项目根目录执行：

```powershell
docker compose up -d --build
```

### 4. 检查服务健康状态

后端健康检查：

```powershell
Invoke-WebRequest http://localhost:8000/health -UseBasicParsing | Select-Object -ExpandProperty Content
```

AI 服务健康检查：

```powershell
Invoke-WebRequest http://localhost:8001/health -UseBasicParsing | Select-Object -ExpandProperty Content
```

正常情况下：

- `backend` 会返回数据库连接正常
- `ai-service` 会返回样本目录状态
- 当前样本统计应识别到 `9` 只样本猫、`57` 张样本图

## 常用访问地址

- 前端：<http://localhost:5173>
- 上传页：<http://localhost:5173/upload>
- 档案列表：<http://localhost:5173/cats>
- 后端健康检查：<http://localhost:8000/health>
- AI 服务健康检查：<http://localhost:8001/health>

## 关键接口

### `POST /api/upload`

上传一张照片并返回：

- 检测结果
- 相似猫推荐
- 图片记录
- 发现记录

注意：

- 当前版本上传后**不会直接自动建档**
- 如果未关联已有档案，返回里会保留 `cat_profile_id = null`
- 由用户在前端结果页点击按钮后，才进入新建档案流程

### `POST /api/upload/create-profile`

根据一次已经保存的上传记录，正式新建档案并绑定：

- 图片记录
- 发现记录
- 新档案

这是当前“由用户决定是否新增档案”的关键接口。

### `POST /api/ai/detect`

执行猫检测，返回：

- `has_cat`
- `confidence`
- `detections`
- `cropped_image_path`
- `message`

### `POST /api/ai/recommend`

根据裁剪猫图返回相似猫推荐，返回候选包含：

- `sample_cat_code`
- `cat_name`
- `similarity_score`
- `reason`

后端会把 `sample_cat_code` 映射到数据库中的真实 `cat_profile_id`。

## 当前推荐映射规则

当前版本已经避免了“样本编号直接占用数据库主键”的问题。

现在的规则是：

- AI 服务返回稳定样本编号，例如 `CAT-0001`
- 数据库中的样本档案保存 `dataset_cat_code`
- 后端根据 `dataset_cat_code` 查找真实档案
- 返回给前端的是映射后的 `cat_profile_id`

这意味着：

- 样本编号稳定
- 数据库主键不再被样本强占
- 现有真实档案不会再被样本导入覆盖

## 当前前端流程

建议按下面的产品路径理解当前系统：

1. 进入上传页
2. 上传猫咪照片并填写地点、时间、备注
3. 查看识别结果与相似猫推荐
4. 如果不是已有猫，由用户点击“新增档案”
5. 在档案列表中浏览真实档案
6. 进入单只猫详情页查看历史记录和图片

## 测试与验证

### 后端回归测试

在项目根目录执行：

```powershell
docker compose exec backend python -m unittest discover -s tests -p "test_*.py" -v
```

当前已覆盖的重点包括：

- AI 推荐成功分支
- AI 推荐失败 fallback 分支
- 上传后不再自动建档
- 由上传结果手动创建档案
- `real/sample/test` 可见性约束

### 前端构建验证

```powershell
cd frontend
npm run build
```

## 当前已知限制

当前版本仍然有这些限制：

- 猫检测仍然依赖通用轻量模型 `yolov8n.pt`
- 某些图片在逆光、远景、遮挡、夜间场景下可能识别不出来
- 相似猫推荐仍属于第一版轻量策略，不是专门训练的个体识别模型
- 样本档案目前不一定都补齐了封面图
- 前端虽然已经开始产品化，但整体结构仍处于持续优化阶段

## 下一步建议

后续建议优先推进：

1. 完成前端五页面统一重构
2. 进一步完善 `profile_source` 数据治理
3. 为样本档案补齐封面图
4. 优化“未检测到猫”时的容错与提示
5. 升级检测模型或调整阈值与裁剪策略
6. 拆分管理页与普通用户页

## 文档

更多说明见 `docs/`：

- `docs/api.md`
- `docs/database.md`
- `docs/ai-detection.md`
- `docs/integration-notes.md`
- `docs/requirements-v1.md`

## 开发说明

如果你准备继续开发，建议顺序如下：

1. 先确认 `frontend`、`backend`、`ai-service`、`mysql` 都正常运行
2. 先跑健康检查
3. 再跑后端回归测试
4. 然后用真实图片做一次上传冒烟验证
5. 最后再继续开发前端或数据治理相关功能
