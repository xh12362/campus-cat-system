# 猫资料整理说明

这个目录用于整理后续“识别是哪一只猫”所需的真实样本数据。

## 当前结构

- `cat_profiles.csv`：猫档案主表，一只猫一条记录
- `north/`：北区猫图片样本

## 已整理样本

### CAT-0001 笑猫（笑笑）

- 区域：北区
- 毛色：纯橘
- 性别：母
- 绝育：已绝育（2022-05-15）
- 活动地点：北区校医院对面的草坪小路
- 图片目录：`datasets/north/CAT-0001-Xiaoxiao`
- 图片数量：11 张
- 说明：已人工清理无效图片，并统一顺序重命名

### CAT-0002 薄荷

- 区域：北区
- 毛色：橘白
- 性别：公
- 绝育：已绝育
- 活动地点：北区竹林小路
- 图片目录：`datasets/north/CAT-0002-Bohe`
- 图片数量：11 张
- 说明：由 `test.docx` 当前版本提取

### CAT-0003 桔子灯

- 区域：北区
- 毛色：玳瑁
- 性别：母
- 绝育：已绝育（2025-05-09）
- 活动地点：北区礼堂附近
- 图片目录：`datasets/north/CAT-0003-JuziDeng`
- 图片数量：8 张
- 说明：由 `test.docx` 当前版本提取

### CAT-0004 虎皮卷

- 区域：北区
- 毛色：橘猫
- 性别：公
- 绝育：未绝育
- 活动地点：礼堂附近
- 图片目录：`datasets/north/CAT-0004-HupiJuan`
- 图片数量：3 张
- 说明：由 `test.docx` 当前版本提取

### CAT-0005 四喜

- 区域：北区
- 毛色：白猫
- 性别：母
- 绝育：已绝育（2025-10-19）
- 活动地点：北区红房子附近草地
- 图片目录：`datasets/north/CAT-0005-Sixi`
- 图片数量：4 张
- 说明：由 `test.docx` 当前版本提取

### CAT-0006 脚底黑

- 区域：北区
- 毛色：狸花
- 性别：公
- 绝育：未绝育
- 活动地点：北区礼堂附近
- 图片目录：`datasets/north/CAT-0006-Jiaodihei`
- 图片数量：3 张
- 说明：由 `test.docx` 当前版本提取

### CAT-0007 三色球

- 区域：北区
- 毛色：三花
- 性别：母
- 绝育：已绝育（2025-03-11）
- 活动地点：北区礼堂附近
- 图片目录：`datasets/north/CAT-0007-Sanseqiu`
- 图片数量：10 张
- 说明：由 `test.docx` 当前版本提取

### CAT-0008 喇叭

- 区域：北区
- 毛色：纯色橘猫
- 性别：公
- 绝育：已绝育（2024-06-27）
- 活动地点：北十二、北十一等宿舍
- 图片目录：`datasets/north/CAT-0008-Laba`
- 图片数量：3 张
- 说明：由 `test.docx` 当前版本提取

### CAT-0009 话梅

- 区域：北区
- 毛色：狸花
- 性别：公
- 绝育：已绝育（2025-12-01）
- 活动地点：北区礼堂附近、北区宿舍区
- 图片目录：`datasets/north/CAT-0009-Huamei`
- 图片数量：4 张
- 说明：由 `test.docx` 当前版本提取

## 后续整理规则

建议继续按以下方式追加：

1. 一篇文章对应一只猫
2. 每只猫一个文件夹
3. 新猫按 `CAT-0002`、`CAT-0003` 继续编号
4. 每整理一只猫，就在 `cat_profiles.csv` 增加一行

## 建议字段

`cat_code, area, cat_name, alias, color, location, sex, sterilized, status, appearance, personality, first_seen, social_relation, remark, source_article, image_folder`
