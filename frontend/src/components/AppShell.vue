<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand-mark">猫</div>
      <h1 class="brand-title">校园流浪猫档案台</h1>
      <p class="brand-subtitle">
        面向第一版核心闭环，先完成上传、建档、记录查询和基础管理壳。
      </p>

      <nav class="nav-list">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-link"
        >
          <span class="nav-label">{{ item.label }}</span>
          <span class="nav-meta">{{ item.meta }}</span>
        </RouterLink>
      </nav>

      <div class="sidebar-note">
        当前默认启用假数据模式，接口层已经按模块拆分，后续对接后端时可以逐个替换。
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
  { to: "/cats", label: "猫档案", meta: "列表" },
  { to: "/discoveries", label: "发现记录", meta: "事件" },
  { to: "/manage", label: "管理页", meta: "基础壳" },
];
</script>
