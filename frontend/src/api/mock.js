const catArchives = [
  {
    id: "cat-001",
    name: "小虎斑",
    campus: "东区宿舍",
    status: "稳定活动",
    gender: "母",
    ageStage: "成猫",
    furPattern: "棕色虎斑",
    firstSeenAt: "2026-03-11 18:20",
    lastSeenAt: "2026-04-16 07:40",
    caretaker: "学生志愿队",
    description: "耳尖略圆，鼻梁偏深色，常在 8 号楼投喂点附近活动。",
    note: "已完成基础体况观察，后续建议补充绝育信息。",
    avatar:
      "https://images.unsplash.com/photo-1519052537078-e6302a4968d4?auto=format&fit=crop&w=600&q=80",
    tags: ["高频出现", "投喂点A", "夜间活跃"],
  },
  {
    id: "cat-002",
    name: "奶油点点",
    campus: "图书馆北门",
    status: "观察中",
    gender: "公",
    ageStage: "幼猫",
    furPattern: "白底橘斑",
    firstSeenAt: "2026-04-02 12:05",
    lastSeenAt: "2026-04-15 19:10",
    caretaker: "保卫处巡查",
    description: "体型较小，行动灵活，对人警惕。",
    note: "近两周出现频次增加，建议继续记录成长情况。",
    avatar:
      "https://images.unsplash.com/photo-1574158622682-e40e69881006?auto=format&fit=crop&w=600&q=80",
    tags: ["新发现", "幼猫", "需持续跟踪"],
  },
  {
    id: "cat-003",
    name: "煤球",
    campus: "食堂后巷",
    status: "需关注",
    gender: "未知",
    ageStage: "成猫",
    furPattern: "黑色短毛",
    firstSeenAt: "2026-02-19 21:00",
    lastSeenAt: "2026-04-14 22:18",
    caretaker: "后勤老师",
    description: "毛色纯黑，右耳似有旧伤痕，近期出现进食减少反馈。",
    note: "建议优先安排复查和近距离拍摄。",
    avatar:
      "https://images.unsplash.com/photo-1511044568932-338cba0ad803?auto=format&fit=crop&w=600&q=80",
    tags: ["夜巡", "旧伤", "复查优先"],
  },
];

const discoveryRecords = [
  {
    id: "rec-101",
    catId: "cat-001",
    catName: "小虎斑",
    campus: "东区宿舍",
    finder: "宿管阿姨",
    method: "巡查发现",
    foundAt: "2026-04-16 07:40",
    health: "精神状态良好",
    note: "在投喂点短暂停留，进食正常。",
  },
  {
    id: "rec-102",
    catId: "cat-002",
    catName: "奶油点点",
    campus: "图书馆北门",
    finder: "学生上报",
    method: "移动端上传",
    foundAt: "2026-04-15 19:10",
    health: "体型偏瘦",
    note: "傍晚出现在草坪边缘，对人保持距离。",
  },
  {
    id: "rec-103",
    catId: "cat-003",
    catName: "煤球",
    campus: "食堂后巷",
    finder: "后勤老师",
    method: "投喂点记录",
    foundAt: "2026-04-14 22:18",
    health: "食欲下降",
    note: "连续两次记录到进食减少，建议复查。",
  },
];

const managementSummary = {
  metrics: {
    totalCats: 23,
    activeRecords: 86,
    pendingReview: 4,
  },
  campuses: [
    { name: "东区宿舍", count: 8 },
    { name: "图书馆周边", count: 5 },
    { name: "食堂后巷", count: 6 },
    { name: "操场西侧", count: 4 },
  ],
  recentActions: [
    "补充上传字段校验规则",
    "预留管理员、志愿者角色配置入口",
    "后续对接校区字典与状态字典接口",
  ],
};

function wait(ms = 180) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

export async function getMockCats() {
  await wait();
  return catArchives;
}

export async function getMockCatById(id) {
  await wait();
  return catArchives.find((item) => item.id === id) || catArchives[0];
}

export async function getMockDiscoveries() {
  await wait();
  return discoveryRecords;
}

export async function getMockManagementSummary() {
  await wait();
  return managementSummary;
}

export async function submitMockUpload(payload) {
  await wait(320);
  return {
    id: `upload-${Date.now()}`,
    message: "假数据上传成功，后续可直接替换为真实接口调用。",
    payload,
  };
}
