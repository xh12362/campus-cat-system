export const routes = [
  {
    path: "/",
    redirect: "/upload",
  },
  {
    path: "/upload",
    name: "upload",
    component: () => import("../views/UploadView.vue"),
    meta: {
      title: "上传猫照片",
      description: "提交新发现的猫照片与现场信息，形成后续识别和建档入口。",
    },
  },
  {
    path: "/cats",
    name: "cats",
    component: () => import("../views/CatListView.vue"),
    meta: {
      title: "猫档案列表",
      description: "按校区、状态与更新时间快速筛查现有猫档案。",
    },
  },
  {
    path: "/cats/:id",
    name: "cat-detail",
    component: () => import("../views/CatDetailView.vue"),
    meta: {
      title: "猫档案详情",
      description: "查看单只猫的身份信息、发现记录与管理备注。",
    },
  },
  {
    path: "/discoveries",
    name: "discoveries",
    component: () => import("../views/DiscoveriesView.vue"),
    meta: {
      title: "发现记录",
      description: "查看巡查、投喂点和学生上报带来的发现事件列表。",
    },
  },
  {
    path: "/manage",
    name: "manage",
    component: () => import("../views/ManageView.vue"),
    meta: {
      title: "管理设置",
      description: "预留基础管理入口，便于后续接入字典、人员和系统配置。",
    },
  },
];
