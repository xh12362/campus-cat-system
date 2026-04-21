# AI Detection And Matching

## 当前 AI 服务职责

`ai-service` 负责两类能力：

- 猫检测：判断图片中是否有猫，并返回检测框
- 相似猫推荐：基于裁剪猫图，从 `datasets/` 里的已知样本中返回 Top-K 候选猫

当前服务仍然只处理猫，不扩展到其他动物，也不在这一版加入复杂训练流程、embedding 训练或个体 ReID 模型。

## 模型与样本位置

### YOLO 模型

- 默认模型文件：`/workspace/models/yolov8n.pt`
- 环境变量：`YOLO_MODEL_PATH`

### 已知猫样本

- 样本主表：`/workspace/datasets/cat_profiles.csv`
- 样本图片目录：`/workspace/datasets/north/`

目录组织约定：

```text
datasets/
├─ cat_profiles.csv
└─ north/
   ├─ CAT-0001-Xiaoxiao/
   │  ├─ 001.jpeg
   │  ├─ 002.jpeg
   │  └─ ...
   ├─ CAT-0002-Bohe/
   └─ ...
```

说明：

- `cat_profiles.csv` 提供样本猫的元数据
- 每只猫对应一个图片目录
- `cat_profiles.csv` 中的 `image_folder` 字段指定该猫的样本图片目录
- 第一版默认将 `CAT-0001` 映射为 `cat_profile_id = 1`

## 检测接口

### POST `/api/ai/detect`

用途：

- 读取上传文件或本地图片路径
- 用 YOLO 检测是否存在猫
- 返回统一检测结果
- 如检测到猫，则基于最高分框生成裁剪图

请求方式：

- `multipart/form-data`
- 支持字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `file` | file | 否 | 直接上传图片 |
| `file_path` | string | 否 | 传入 AI 服务可访问的图片路径 |

至少提供 `file` 或 `file_path` 其中一个。

返回结构保持不变：

```json
{
  "model_loaded": true,
  "has_cat": true,
  "confidence": 0.97,
  "detections": [
    {
      "label": "cat",
      "score": 0.97,
      "bbox": [15, 22, 188, 210]
    }
  ],
  "cropped_image_path": "/workspace/uploads/cropped/example.jpg",
  "message": "Cat detected successfully."
}
```

字段说明：

| 字段 | 说明 |
| --- | --- |
| `has_cat` | 是否检测到猫 |
| `confidence` | 当前猫检测结果中的最高置信度 |
| `detections` | 所有猫检测框 |
| `cropped_image_path` | 最佳猫框裁剪图路径 |

## 猫检测流程

当前流程：

1. 接收原图文件或原图路径
2. 加载为 RGB 图片
3. 使用缓存后的 YOLO 模型执行推理
4. 过滤类别为 `cat` 的检测框
5. 计算最高分作为 `confidence`
6. 选取最佳猫框生成裁剪图
7. 返回检测结果

## 裁剪图生成逻辑

- 只在检测到至少一只猫时生成裁剪图
- 从所有猫框中选择 `score` 最高的一只
- 使用该检测框裁剪原图
- 裁剪前会对坐标做边界保护，避免越界
- 裁剪图保存到：`uploads/cropped/`
- 文件名使用随机 UUID，避免覆盖

## 相似猫推荐接口

### POST `/api/ai/recommend`

用途：

- 输入：新上传图片对应的裁剪猫图路径
- 输出：基于 `datasets/` 样本计算出的 Top-K 候选猫

请求体：

```json
{
  "cropped_image_path": "/workspace/uploads/cropped/example.jpg",
  "top_k": 5
}
```

返回体：

```json
{
  "query_image_path": "/workspace/uploads/cropped/example.jpg",
  "top_k": 5,
  "candidates": [
    {
      "cat_profile_id": 1,
      "cat_name": "笑笑",
      "similarity_score": 0.8231,
      "reason": "Visual similarity matched dataset sample CAT-0001 using 11 reference image(s); best reference: 003.jpeg."
    }
  ]
}
```

候选字段说明：

| 字段 | 说明 |
| --- | --- |
| `cat_profile_id` | 由样本 `CAT-000x` 映射出的稳定档案 id |
| `cat_name` | 样本猫名称 |
| `similarity_score` | 第一版视觉相似度分数，范围接近 `0.0 ~ 1.0` |
| `reason` | 候选产生原因说明 |

## 第一版相似匹配实现方式

第一版目标是“可运行、有候选结果”，不追求训练级精度。

当前实现策略：

- 读取 `cat_profiles.csv`
- 读取每只猫的样本图片目录
- 为每张样本图提取轻量视觉特征
- 为每只猫聚合样本图特征
- 对新上传裁剪图提取同样特征
- 使用余弦相似度对所有样本猫排序
- 返回 Top-K 结果

当前特征主要由以下信息组成：

- RGB 颜色统计
- HSV 颜色分布直方图
- 灰度缩略图特征

说明：

- 这是无训练、无标注微调的第一版方案
- 优先保证系统能稳定返回候选，而不是追求最终识别准确率

## 当前代码结构

AI 服务现在分为三层：

- `app/server.py`
  - 提供 `/api/ai/detect`
  - 提供 `/api/ai/recommend`
  - 提供 `/health`
- `app/sample_catalog.py`
  - 负责读取 `cat_profiles.csv`
  - 负责组织样本目录与样本图片
  - 负责生成样本摘要信息
- `app/sample_matcher.py`
  - 负责提取图片特征
  - 负责构建样本索引
  - 负责生成 Top-K 推荐结果

## 当前局限性

- 仍然不是个体身份识别模型
- 仍然没有训练流程和在线学习
- `similarity_score` 只代表第一版视觉相似度，不代表最终身份确认概率
- 样本量较少时，结果容易受角度、光照、遮挡影响
- 多只外观相近的狸花或橘猫之间，误匹配概率会更高
- 当前推荐依赖裁剪图质量，若检测框偏移，推荐质量会下降

## 后续如何扩展到更强的相似猫匹配

后续建议的演进方向：

1. 保留现有 `/api/ai/detect`，继续作为稳定检测入口
2. 保留现有 `/api/ai/recommend`，继续作为后端可调用的推荐入口
3. 后续引入更稳定的 embedding 提取模型
4. 为每张样本图缓存独立特征向量
5. 逐步引入人工确认后的真匹配数据，迭代更强的相似度策略
6. 在不破坏现有字段语义的前提下，增加更丰富的匹配解释信息
