<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand-mark">猫</div>
      <h1 class="brand-title">校园流浪猫档案</h1>
      <p class="brand-subtitle">
        面向真实使用场景的校园公益产品，帮助同学完成猫咪上报、档案查看和持续记录。
      </p>

      <nav class="nav-list">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-link">
          <span class="nav-label">{{ item.label }}</span>
          <span class="nav-meta">{{ item.meta }}</span>
        </RouterLink>
      </nav>

      <div class="sidebar-note">
        如果你刚刚在校园里遇到一只猫，直接从“上传页”开始即可。上传后可以立即看到识别结果和相似猫推荐。
      </div>
    </aside>

    <main class="main-area">
      <PageTopbar />
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from "vue-router";
import PageTopbar from "./PageTopbar.vue";

const navItems = [
  { to: "/upload", label: "上传页", meta: "新上报" },
  { to: "/cats", label: "猫咪档案", meta: "浏览" },
  { to: "/discoveries", label: "发现记录", meta: "事件" },
  { to: "/manage", label: "管理设置", meta: "预留" },
];
</script>
