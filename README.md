# 基于 YOLO 的校园流浪猫识别与档案系统

一个面向校园流浪猫场景的 Web 系统。用户可以上传猫咪照片并填写发现信息，系统进行猫检测、返回相似猫推荐，并支持后续建立或查看猫档案。

## 系统流程

```
上传照片 → CLAHE增强 → YOLOv8m检测 → 裁剪猫图 → ResNet18提取特征 → 相似度匹配 → Top-K推荐 → 用户决定是否建档
```

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + Vite |
| 后端 | FastAPI + SQLAlchemy + PyMySQL |
| AI 服务 | Ultralytics YOLOv8m + OpenCV + PyTorch (ResNet18) |
| 数据库 | MySQL 8 |
| 部署 | Docker Compose |

## 系统结构

```
.
├─ frontend/              # Vue 3 前端 (端口5173)
├─ backend/               # FastAPI 后端 (端口8000)
│  ├─ app/
│  │  ├─ api/routes/      # 路由: cats, sightings, upload
│  │  ├─ models/          # SQLAlchemy 模型
│  │  ├─ schemas/         # Pydantic 校验
│  │  └─ services/        # 业务逻辑与 AI 服务调用
│  └─ tests/              # 后端测试
├─ ai-service/            # AI 检测与推荐服务 (端口8001)
│  └─ app/
│     ├─ server.py        # FastAPI + YOLO 检测接口
│     ├─ sample_matcher.py # ResNet18 特征提取 + 相似匹配
│     └─ sample_catalog.py # 样本目录读取
├─ mysql/
│  ├─ init/               # 建表 SQL
│  └─ migrations/         # 迁移脚本
├─ datasets/              # 样本猫元数据与图片
│  ├─ cat_profiles.csv    # 样本目录 (需手动编辑)
│  └─ north/              # 北区猫图片 (CAT-0001 ~ CAT-0009)
├─ uploads/
│  ├─ original/           # 用户上传原图
│  └─ cropped/            # YOLO 裁剪后的猫图
├─ models/                # YOLO 模型权重
├─ docs/                  # 文档
├─ docker-compose.yml
└─ README.md
```

## 检测能力

| 项目 | 当前版本 |
|------|---------|
| 检测模型 | YOLOv8m (50MB, 自动下载) |
| 低光照增强 | CLAHE 自适应直方图均衡化 |
| 置信度阈值 | 0.25 (可配置) |
| IoU 阈值 | 0.45 (可配置) |

相比早期的 YOLOv8n (6.5MB)，v8m 在检测召回率和精度上有显著提升。CLAHE 预处理让暗光、逆光场景下猫的轮廓更清晰。

## 猫个体识别能力

特征提取采用 **两阶段兜底策略**：

| 优先 | 方法 | 特征维度 | 说明 |
|------|------|---------|------|
| 主选 | ResNet18 (ImageNet) | 512 | 深度语义特征，捕获耳形、面部结构、花纹 |
| 兜底 | 手工特征 | 4176 | 颜色直方图 + 边缘方向 + 64×64 缩略图 |

深度特征对不同光照、姿态变化有很强的鲁棒性，大幅优于纯颜色直方图方法。在 9 只猫 × 57 张样本的测试中，Top-1 识别准确率 100%，正样本与第二名相似度差距稳定在 7-10 个百分点。

## 快速开始

### 1. 准备环境

确保本机已安装 **Docker Desktop**。

### 2. 配置环境变量

```powershell
Copy-Item .env.example .env
```

如果本机已有 MySQL 占用 `3306`，在 `.env` 中调整：

```env
MYSQL_PORT=3307
```

完整环境变量说明见 [环境变量](#环境变量) 章节。

### 3. 启动服务

```powershell
docker compose up -d --build
```

首次启动时自动下载：
- `yolov8m.pt` (~50MB) — YOLO 检测模型
- `resnet18-f37072fd.pth` (~45MB) — 特征提取模型（首次请求时下载到容器缓存）

### 4. 检查健康状态

```powershell
# 后端健康检查
curl http://localhost:8000/health

# AI 服务健康检查
curl http://localhost:8001/health
```

正常响应示例（AI 服务）：

```json
{
  "service": "ai-service",
  "status": "ok",
  "model_path": "/workspace/models/yolov8m.pt",
  "dataset": {
    "sample_cat_count": 9,
    "sample_image_count": 57
  }
}
```

### 5. 访问

| 地址 | 说明 |
|------|------|
| http://localhost:5173 | 前端首页 |
| http://localhost:5173/upload | 上传页 |
| http://localhost:5173/cats | 档案列表 |
| http://localhost:8000/health | 后端健康检查 |
| http://localhost:8001/health | AI 服务健康检查 |

## 核心接口

### `POST /api/upload`

上传照片 → 检测猫 → 返回相似推荐。不会自动建档，由用户决定。

### `POST /api/upload/create-profile`

根据已有上传记录新建档案并绑定图片和发现记录。

### `POST /api/ai/detect`

执行猫检测，返回 `has_cat`、`confidence`、裁剪图路径等。

### `POST /api/ai/recommend`

根据裁剪图返回 Top-K 相似猫候选。

## 如何增加新猫

在 `datasets/` 下添加新猫的资料，无需重启服务：

### 1. 准备图片

每只猫建议 10-15 张不同角度、不同光线的照片：

```
datasets/north/CAT-0010-大橘/
  ├── 001.jpeg
  ├── 002.jpeg
  └── 003.jpeg
```

### 2. 编辑 CSV 目录

编辑 `datasets/cat_profiles.csv`，追加一行：

```csv
CAT-0010,北区,大橘,大橘,橘白,北区食堂附近,公,否,在读,标准橘白头部橘色,亲人贪吃,2026,,,,datasets/north/CAT-0010-大橘
```

CSV 各列说明：

| 列 | 说明 | 必填 |
|----|------|------|
| cat_code | 唯一编号 (CAT-XXXX) | 是 |
| area | 活动区域 | 是 |
| cat_name | 名字 | 推荐 |
| alias | 别名 | 可选 |
| color | 毛色描述 | 可选 |
| location | 常出没地点 | 可选 |
| sex | 性别 | 可选 |
| sterilized | 绝育状态 | 可选 |
| status | 生存状态 | 可选 |
| appearance | 外貌特征 | 可选 |
| personality | 性格描述 | 可选 |
| first_seen | 首次发现时间 | 可选 |
| social_relation | 社交关系 | 可选 |
| remark | 备注 | 可选 |
| source_article | 来源文章 | 可选 |
| image_folder | 图片文件夹路径 | **是** |

### 3. 重启刷新缓存

```powershell
docker compose restart ai-service
```

首次加载时会计算所有样本的 DNN 特征并缓存，后续请求秒级响应。随着样本库增大，建议每只猫照片数保持均衡，避免类别 imbalance 影响匹配。

## 环境变量

所有配置通过 `.env` 文件设置：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `FRONTEND_PORT` | `5173` | 前端端口 |
| `BACKEND_PORT` | `8000` | 后端端口 |
| `AI_SERVICE_PORT` | `8001` | AI 服务端口 |
| `MYSQL_PORT` | `3306` | MySQL 端口 |
| `YOLO_MODEL_PATH` | `/workspace/models/yolov8m.pt` | YOLO 模型路径 |
| `DATASET_ROOT` | `/workspace/datasets` | 样本数据集根目录 |
| `DETECTION_CONF` | `0.25` | 检测置信度阈值 |
| `DETECTION_IOU` | `0.45` | NMS 的 IoU 阈值 |
| `CLAHE_ENABLED` | `true` | 低光照增强开关 |

## 测试

```powershell
docker compose exec backend python -m unittest discover -s tests -p "test_*.py" -v
```

## 已实现能力

### 上传与检测
- 上传猫咪照片 + 地点/时间/备注
- CLAHE 低光照增强
- YOLOv8m 猫检测 + 自适应阈值
- 返回检测结果与裁剪图路径
- 保存图片与发现记录

### 猫个体识别
- ResNet18 深度特征提取 (512-d)
- 手工特征降级兜底 (4176-d)
- 特征方法锁定确保维度一致性
- 返回 Top-K 相似猫候选

### 档案管理
- 上传后不自动建档，由用户决定
- 已有档案可继续关联新发现
- 支持 real / sample / test 数据来源分类
- 档案列表默认只显示 real 数据

## 当前限制

- 检测模型对极端姿态、严重遮挡场景仍有漏检
- 特征提取仅使用 ImageNet 预训练（未在猫数据集上微调）
- 样本数据集规模有限（9 只猫），制约识别上限
- 首次加载样本时需要下载 ResNet18 权重（约 45MB，缓存后不重复下载）
- Docker 环境可能存在 SSL 下载问题，模型文件可手动下载后映射进容器
