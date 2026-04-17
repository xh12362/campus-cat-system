import { createRouter, createWebHistory } from "vue-router";
import { routes } from "./routes";

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

router.afterEach((to) => {
  const appTitle = "校园流浪猫智能识别与档案管理系统";
  document.title = to.meta?.title ? `${to.meta.title} | ${appTitle}` : appTitle;
});

export default router;
