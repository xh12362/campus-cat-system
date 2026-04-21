# Database And Sample Profile Integration

## 数据库

- 数据库名：`campus_cat`
- 引擎：MySQL 8
- 字符集：`utf8mb4`

## 现有核心表

### user

存放上传者或维护人员的基础信息。

### cat_profile

猫档案主表。第一版中：

- 自动建档仍然写入这张表
- 已知样本猫也建议导入到这张表
- 第一版相似匹配返回的 `cat_profile_id` 应尽量与这张表中的 `id` 对齐

字段重点：

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `name` | 猫名称 |
| `gender` | 性别 |
| `coat_color` | 毛色 |
| `first_seen_at` | 首次发现时间 |
| `first_seen_location` | 首次发现地点 |
| `distinguishing_features` | 外观特征 |
| `notes` | 补充说明 |

### cat_image

存放上传原图与 AI 相关路径。

字段重点：

| 字段 | 说明 |
| --- | --- |
| `file_path` | 原图路径 |
| `ai_feature_path` | 当前用于保存裁剪图路径 |
| `ai_match_status` | 当前 AI 匹配状态 |

### cat_sighting

存放一次发现记录。

## 第一版样本数据接入方案

第一版没有新增复杂特征表，而是先采用“文件样本 + 数据库档案对齐”的方案。

样本来源：

- `datasets/cat_profiles.csv`
- `datasets/north/<每只猫样本目录>/`

接入规则：

1. `cat_profiles.csv` 作为已知猫样本主表
2. `CAT-0001` 这类 `cat_code` 解析为稳定 id，例如 `1`
3. 样本猫建议导入数据库 `cat_profile`
4. AI 推荐接口返回的 `cat_profile_id` 使用上述稳定 id
5. 后端拿到候选后，可以直接用于现有推荐结果结构

## 为什么第一版不强制新增 `cat_feature` 表

这一版目标是“先有稳定可用的推荐结果”，因此优先做：

- 样本目录读取
- 样本图片轻量特征提取
- 进程内缓存
- Top-K 推荐返回

暂时不做：

- 复杂特征持久化表
- 训练数据版本管理
- embedding 在线更新流程
- 大规模向量检索索引

这能让第一版更快跑通，也不会明显扩大后端业务复杂度。

## 样本档案导入脚本

新增脚本：

`backend/scripts/import_dataset_profiles.py`

作用：

- 读取 `datasets/cat_profiles.csv`
- 将 `CAT-000x` 转换成 `cat_profile.id = x`
- 将样本猫基础信息写入或更新到 `cat_profile`

建议运行方式：

```powershell
cd backend
python scripts/import_dataset_profiles.py
```

说明：

- 脚本会按 `id` 做更新或插入
- 适合作为初始化样本档案的方式
- 这样 AI 推荐返回的 `cat_profile_id` 与数据库档案能保持稳定一致

## 上传到推荐的链路

当前链路如下：

1. 用户上传原图
2. 后端调用 `/api/ai/detect`
3. AI 服务生成 `cropped_image_path`
4. 后端将裁剪图路径传给 `/api/ai/recommend`
5. AI 服务基于 `datasets/` 返回 Top-K 候选
6. 后端将候选结果放入 `recommendations`

## 第一版推荐结果结构

后端保持以下候选结构：

```json
{
  "cat_profile_id": 1,
  "cat_name": "笑笑",
  "similarity_score": 0.8231,
  "reason": "Visual similarity matched dataset sample CAT-0001 using 11 reference image(s); best reference: 003.jpeg."
}
```

## 后续可扩展方向

当第一版推荐稳定后，可再考虑新增：

- `cat_feature`：缓存每张样本图或每只猫的特征向量
- `feature_version`：特征版本
- `feature_source`：来源图片或裁剪图路径
- `updated_at`：特征更新时间

但这些属于下一阶段优化，不是当前第一版上线的必需条件。
