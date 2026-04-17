# 基于 YOLO 的校园流浪猫智能识别与档案管理系统

一个面向校园流浪猫管理场景的 Web 系统。用户上传随手拍照片后，系统会自动检测图片中是否存在猫，生成检测结果与裁剪图，并保存图片记录、发现记录和猫档案信息。

当前仓库已经完成第一版核心闭环：

`上传图片 -> YOLO 检测 -> 裁剪猫图 -> 保存记录 -> 自动建档 -> 返回结果`

## 项目简介

传统校园流浪猫管理通常依赖人工观察和零散记录，容易出现信息不统一、追踪困难、历史数据缺失等问题。本项目尝试通过图像识别和档案化管理，把“发现一只猫”变成可记录、可查询、可持续维护的数据流程。

第一版聚焦于验证系统主链路，不追求一步做全，而是先把最重要的能力做成：

- 上传猫照片
- 自动检测图片中是否有猫
- 生成检测框、置信度和裁剪图
- 自动创建猫档案或关联已有档案
- 保存图片记录和发现记录
- 在前端展示真实上传结果

## 第一版已实现功能

- 前端、后端、MySQL、AI 服务已全部跑通
- 前端上传页已接入真实接口
- `POST /api/upload` 已支持图片上传和地点信息提交
- YOLO 猫检测已接入，支持 `POST /api/ai/detect`
- 检测成功后自动生成裁剪图
- 上传后自动创建新猫档案
- 图片记录和发现记录会自动关联到对应档案
- 猫档案列表、猫详情、发现记录已切到真实接口
- AI 模块、需求文档、联调文档、接口文档、数据库文档已补齐

## 当前效果

系统当前可以完成以下流程：

1. 用户上传一张校园流浪猫图片，并填写发现地点
2. 后端保存原图到 `uploads/original/`
3. AI 服务使用 `yolov8n.pt` 检测图片中的猫
4. 生成检测框、置信度和裁剪图到 `uploads/cropped/`
5. 若未指定 `cat_profile_id`，系统自动创建新的猫档案
6. 保存图片记录与发现记录，并返回结构化结果给前端

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
- OpenCV
- Pillow

### 数据库与部署

- MySQL 8
- Docker Compose

## 系统架构

项目由 4 个核心服务组成：

- `frontend`：前端页面，默认端口 `5173`
- `backend`：业务后端，默认端口 `8000`
- `ai-service`：AI 检测服务，默认端口 `8001`
- `mysql`：数据库服务，容器端口 `3306`

上传链路如下：

`前端上传 -> backend 保存图片 -> backend 调用 ai-service -> YOLO 检测 -> 返回 detection -> 写入数据库 -> 前端展示结果`

## 项目结构

```text
.
├─ frontend/              # Vue 前端
├─ backend/               # FastAPI 后端
├─ ai-service/            # YOLO 检测服务
├─ mysql/
│  └─ init/               # MySQL 初始化脚本
├─ uploads/
│  ├─ original/           # 原始上传图片
│  └─ cropped/            # 裁剪后的猫图
├─ models/                # YOLO 模型权重目录
├─ docs/                  # 项目文档
├─ .env.example
├─ docker-compose.yml
└─ README.md
```

## 运行前准备

### 1. 安装 Docker

请先安装并启动 Docker Desktop。

### 2. 准备 YOLO 模型文件

将模型权重文件放到：

```text
models/yolov8n.pt
```

默认使用的模型路径由环境变量控制：

```env
YOLO_MODEL_PATH=/workspace/models/yolov8n.pt
```

### 3. 准备环境变量

首次运行前复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

说明：

- 如果本机已经有 MySQL 占用了 `3306`，可以把 `.env` 中的 `MYSQL_PORT` 改成别的端口
- 本项目当前示例环境使用的是：

```env
MYSQL_PORT=3307
```

## 快速启动

在项目根目录执行：

```powershell
docker compose up --build
```

如果只想后台启动：

```powershell
docker compose up -d --build
```

## 访问地址

- 前端首页：[http://localhost:5173](http://localhost:5173)
- 后端健康检查：[http://localhost:8000/health](http://localhost:8000/health)
- AI 健康检查：[http://localhost:8001/health](http://localhost:8001/health)

## 关键接口

### 上传接口

```http
POST /api/upload
```

表单参数示例：

- `photo`：图片文件
- `location_text`：发现地点
- `notes`：备注，可选
- `cat_profile_id`：已有档案 ID，可选

### AI 检测接口

```http
POST /api/ai/detect
```

返回结果包含：

- `has_cat`
- `confidence`
- `detections`
- `cropped_image_path`
- `message`

## 示例返回

上传成功后的后端返回示例：

```json
{
  "message": "Upload completed successfully.",
  "profile_created": true,
  "cat_profile_id": 3,
  "detection": {
    "has_cat": true,
    "confidence": 0.8598529696464539,
    "detections": [
      {
        "label": "cat",
        "score": 0.8598529696464539,
        "bbox": [245, 429, 1077, 1380]
      }
    ],
    "cropped_image_path": "/workspace/uploads/cropped/example.jpg",
    "message": "Cat detected successfully."
  }
}
```

## 文档说明

项目文档位于 `docs/`，当前已包含：

- `docs/requirements-v1.md`：第一版需求说明
- `docs/integration-notes.md`：联调记录
- `docs/api.md`：接口文档
- `docs/database.md`：数据库说明
- `docs/ai-detection.md`：AI 模块说明

## 当前限制

当前第一版仍有一些明确限制：

- 相似猫匹配仍为占位逻辑，尚未实现真正的个体识别
- 轨迹分析、认领、猫舍管理等扩展功能尚未进入第一版
- 当前主要面向“流浪猫”场景，未扩展到其他动物

## 后续计划

下一阶段建议优先推进：

- 真实相似猫匹配
- 前端图片展示优化
- 档案信息完善
- 活动轨迹与统计分析
- 更完整的管理端功能

## 开发说明

如果你准备继续开发，建议顺序如下：

1. 先确认 `frontend`、`backend`、`ai-service`、`mysql` 都已正常运行
2. 上传一张测试猫图，确认主链路正常
3. 再继续扩展自动建档、相似匹配和前端展示

## 许可证

当前仓库未单独声明许可证，如需开源发布，建议补充 `LICENSE` 文件。
