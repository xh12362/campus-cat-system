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
      title: "上传猫咪照片",
      description: "提交新发现的猫咪照片与现场信息，快速查看识别结果和相似猫推荐。",
    },
  },
  {
    path: "/cats",
    name: "cats",
    component: () => import("../views/CatListView.vue"),
    meta: {
      title: "猫咪档案列表",
      description: "浏览校园里已建档的流浪猫，按地点、状态和外观快速找到目标猫咪。",
    },
  },
  {
    path: "/cats/:id",
    name: "cat-detail",
    component: () => import("../views/CatDetailView.vue"),
    meta: {
      title: "猫咪档案详情",
      description: "查看单只猫的图片、基本资料、活动地点和发现时间线。",
    },
  },
  {
    path: "/discoveries",
    name: "discoveries",
    component: () => import("../views/DiscoveriesView.vue"),
    meta: {
      title: "发现记录",
      description: "查看系统中已记录的发现事件，便于后续扩展巡查和上报能力。",
    },
  },
  {
    path: "/manage",
    name: "manage",
    component: () => import("../views/ManageView.vue"),
    meta: {
      title: "管理设置",
      description: "预留给后续管理能力使用，不影响当前上报与档案主流程。",
    },
  },
];
