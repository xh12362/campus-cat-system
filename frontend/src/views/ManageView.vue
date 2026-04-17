<template>
  <div class="content-grid">
    <section class="hero-card">
      <span class="tag">基础管理壳</span>
      <h3 class="page-title">管理页预留区</h3>
      <p class="page-kicker">
        当前先搭建管理页的总览、字典配置和待办区，方便后续逐步接入管理员、校区、状态字典等功能。
      </p>
    </section>

    <div class="metric-grid">
      <article class="metric-card">
        <div class="metric-label">当前猫档案</div>
        <div class="metric-value">{{ summary.metrics.totalCats }}</div>
        <div class="metric-trend">可扩展到校区维度</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">发现记录</div>
        <div class="metric-value">{{ summary.metrics.activeRecords }}</div>
        <div class="metric-trend">适合加时间筛选</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">待复核事项</div>
        <div class="metric-value">{{ summary.metrics.pendingReview }}</div>
        <div class="metric-trend">后续可接审批流</div>
      </article>
    </div>

    <div class="manage-grid">
      <SectionCard title="校区分布" subtitle="预留字典与配置数据展示区。">
        <div class="archive-grid">
          <div v-for="campus in summary.campuses" :key="campus.name" class="archive-card">
            <div class="card-caption">{{ campus.name }}</div>
            <div class="metric-value" style="font-size: 1.8rem;">{{ campus.count }}</div>
            <div class="helper-text">已建档猫只</div>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="近期管理动作" subtitle="作为后续后台设置页的占位。">
        <div class="timeline">
          <div v-for="item in summary.recentActions" :key="item" class="timeline-item">
            <strong>{{ item }}</strong>
          </div>
        </div>
      </SectionCard>
    </div>

    <SectionCard title="预留模块" subtitle="这些区域后续可逐个替换成真实业务页面。">
      <div class="archive-grid">
        <div class="archive-card">
          <strong>校区字典</strong>
          <p class="muted">维护发现地点、校区楼栋、投喂点等基础数据。</p>
        </div>
        <div class="archive-card">
          <strong>状态字典</strong>
          <p class="muted">统一“观察中 / 稳定活动 / 需关注”等状态来源。</p>
        </div>
        <div class="archive-card">
          <strong>人员配置</strong>
          <p class="muted">后续接入管理员、志愿者和巡查角色。</p>
        </div>
      </div>
    </SectionCard>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import SectionCard from "../components/SectionCard.vue";
import { fetchManagementSummary } from "../api";

const summary = ref({
  metrics: {
    totalCats: 0,
    activeRecords: 0,
    pendingReview: 0,
  },
  campuses: [],
  recentActions: [],
});

onMounted(async () => {
  summary.value = await fetchManagementSummary();
});
</script>
