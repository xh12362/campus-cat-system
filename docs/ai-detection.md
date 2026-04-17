# AI Detection Module

## 当前 AI 服务职责

`ai-service` 负责第一版中的“是否检测到猫”这一层能力，不负责个体身份识别，也不负责复杂相似度检索。

当前职责包括：

- 加载 YOLO 模型并提供独立检测服务
- 接收图片文件或图片路径
- 检测图片中是否存在猫
- 返回统一检测结果：`has_cat`、`confidence`、`detections`
- 基于最佳猫框生成一张裁剪图并保存到 `uploads/cropped/`
- 提供基础健康检查接口

## YOLO 模型文件位置

- 默认模型路径：`/workspace/models/yolov8n.pt`
- 对应代码常量：`YOLO_MODEL_PATH`
- 可通过环境变量覆盖：

```env
YOLO_MODEL_PATH=/workspace/models/yolov8n.pt
```

模型目录约定仍然是根目录下的 `models/`，容器内挂载到 `/workspace/models/`。

## 接口说明

### POST `/api/ai/detect`

该接口用于执行单张图片的猫检测。

### 请求格式

请求类型：`multipart/form-data`

支持两种输入方式，二选一即可：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `file` | file | 否 | 直接上传图片文件 |
| `file_path` | string | 否 | 传入服务器可访问的图片绝对路径 |

说明：

- 至少提供 `file` 或 `file_path` 其中一个
- 当前实现中若同时传入，优先使用 `file`

### 返回格式

当前返回字段含义保持不变：

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
  "cropped_image_path": "/workspace/uploads/cropped/9f9a0d2d0dd64d6c8b6c1a5d6f7c1234.jpg",
  "message": "Cat detected successfully."
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `model_loaded` | boolean | 当前请求是否成功使用已加载模型完成检测 |
| `has_cat` | boolean | 图片中是否检测到猫 |
| `confidence` | number \| null | 当前猫检测结果中的最高置信度；未检测到猫时为 `null` |
| `detections` | array | 所有猫目标框列表 |
| `cropped_image_path` | string \| null | 最佳猫框裁剪图路径；未检测到猫时为 `null` |
| `message` | string | 当前检测结果说明 |

### 检测框结构

`detections` 中每个元素格式如下：

```json
{
  "label": "cat",
  "score": 0.97,
  "bbox": [left, top, right, bottom]
}
```

说明：

- 当前只保留类别为 `cat` 的结果
- `bbox` 使用像素坐标，顺序为 `[left, top, right, bottom]`

## 猫检测流程

当前检测流程如下：

1. 接收 `file` 或 `file_path`
2. 将图片加载为 RGB 格式
3. 懒加载 YOLO 模型并缓存到进程内
4. 运行 YOLO 推理
5. 从所有检测框中筛选类别为 `cat` 的结果
6. 计算最高置信度，生成 `has_cat`、`confidence`、`detections`
7. 选取分数最高的猫框裁剪并保存
8. 返回统一结果结构

## 裁剪图生成逻辑

裁剪图逻辑保持简单稳定：

- 仅在检测到至少一只猫时生成裁剪图
- 从所有猫框中选择 `score` 最高的一个作为最佳框
- 根据最佳框的 `bbox` 裁剪原图
- 裁剪前会对边界做一次钳制，避免越界导致保存失败
- 输出目录为：`/workspace/uploads/cropped/`
- 文件名使用随机 UUID，尽量避免重名覆盖

这意味着：

- 一张图即使检测到多只猫，当前也只生成一张最佳裁剪图
- 当前裁剪图主要用于后续占位能力和人工检查，不代表个体身份识别已经完成

## 当前代码结构

当前 `ai-service/app/server.py` 结构比较集中，职责清晰：

- `get_model()`：加载并缓存 YOLO 模型
- `normalize_image_path()`：统一处理传入路径
- `load_image()`：读取上传文件或本地路径图片
- `run_detection()`：执行 YOLO 推理并过滤猫目标
- `save_best_crop()`：保存最佳检测框裁剪图
- `GET /health`：返回服务与模型状态
- `POST /api/ai/detect`：统一对外检测接口

这一轮没有拆成多模块，主要是为了保持接口稳定，避免在第一版阶段引入额外重构成本。

## 当前局限性

当前版本是第一版检测能力，只保证“发现猫”和“生成候选裁剪图”，局限性包括：

- 只能判断是否有猫，不能识别是哪一只猫
- 不做 embedding 向量提取
- 不做跨图片相似猫匹配
- 不做 ReID 或个体身份建模
- 多猫场景下只保存最高分猫框的裁剪图
- 模型效果依赖当前 YOLO 权重，遮挡、远距离、小目标、夜间图像可能影响结果
- `confidence` 仅代表当前检测分数，不代表个体匹配可信度

## 后续如何扩展到相似猫匹配

后续如果要扩展到“老猫匹配推荐”，建议在不破坏当前接口的前提下分层演进：

1. 保留现有 `/api/ai/detect`，继续作为“是否有猫 + 裁剪图生成”的稳定入口
2. 在裁剪图基础上新增特征提取步骤，生成 embedding 向量
3. 将 embedding 与猫档案历史图片特征做相似度检索
4. 输出候选猫列表和相似度分数，交由后端作为“推荐结果”而非强判定
5. 在积累足够数据后，再考虑更稳定的个体识别模型或 ReID 流程

建议扩展方向：

- 为裁剪图增加特征文件存储路径
- 增加单独的“特征提取 / 相似度检索”模块
- 将“检测”和“匹配”拆成两个独立阶段
- 保持 `has_cat`、`confidence`、`detections` 的现有语义不变，避免影响前后端联调

## 本轮稳定性整理说明

本轮只做了小范围稳定性整理，不改变接口返回字段语义：

- 非图片输入时给出更明确的错误提示
- 路径解析更稳，减少对当前工作目录的依赖
- 裁剪框边界做保护，降低异常输入导致保存失败的概率
- 健康检查增加模型与裁剪目录状态，便于排查环境问题
