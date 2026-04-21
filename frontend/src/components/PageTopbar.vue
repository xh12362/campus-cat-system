<template>
  <header class="topbar">
    <div>
      <p class="page-kicker">校园流浪猫上报与档案查看</p>
      <h2 class="page-title">{{ route.meta?.title || "校园流浪猫档案平台" }}</h2>
      <p class="page-kicker">{{ route.meta?.description }}</p>
    </div>

    <div class="topbar-actions">
      <RouterLink class="btn btn-secondary" to="/cats">查看档案</RouterLink>
      <RouterLink class="btn btn-primary" to="/upload">上传新照片</RouterLink>
    </div>
  </header>
</template>

<script setup>
import { RouterLink, useRoute } from "vue-router";

const route = useRoute();
</script>
