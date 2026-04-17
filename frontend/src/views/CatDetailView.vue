<template>
  <div v-if="cat" class="content-grid">
    <section class="hero-card">
      <span class="tag">真实详情数据</span>
      <h3 class="page-title">{{ cat.name || `未命名档案 #${cat.id}` }}</h3>
      <p class="page-kicker">
        首次发现于 {{ formatText(cat.first_seen_location) }}，时间 {{ formatDateTime(cat.first_seen_at) }}
      </p>
      <div class="chip-row" style="margin-top: 16px;">
        <span class="tag">档案 ID {{ cat.id }}</span>
        <span class="tag">健康：{{ formatText(cat.health_status) }}</span>
        <span class="tag">绝育：{{ formatText(cat.sterilization_status) }}</span>
      </div>
    </section>

    <div class="detail-grid">
      <SectionCard title="基础信息" subtitle="直接展示 `GET /api/cats/{id}` 返回字段。">
        <div class="kv">
          <span class="muted">名称</span>
          <strong>{{ formatText(cat.name) }}</strong>
        </div>
        <div class="kv">
          <span class="muted">性别</span>
          <strong>{{ formatText(cat.gender) }}</strong>
        </div>
        <div class="kv">
          <span class="muted">毛色</span>
          <strong>{{ formatText(cat.coat_color) }}</strong>
        </div>
        <div class="kv">
          <span class="muted">年龄阶段</span>
          <strong>{{ formatText(cat.age_stage) }}</strong>
        </div>
        <div class="kv">
          <span class="muted">健康状态</span>
          <strong>{{ formatText(cat.health_status) }}</strong>
        </div>
        <div class="kv">
          <span class="muted">特征描述</span>
          <strong>{{ formatText(cat.distinguishing_features) }}</strong>
        </div>
      </SectionCard>

      <SectionCard title="建档信息" subtitle="用于查看创建和备注信息。">
        <div class="kv">
          <span class="muted">首次发现地点</span>
          <strong>{{ formatText(cat.first_seen_location) }}</strong>
        </div>
        <div class="kv">
          <span class="muted">首次发现时间</span>
          <strong>{{ formatDateTime(cat.first_seen_at) }}</strong>
        </div>
        <div class="kv">
          <span class="muted">创建时间</span>
          <strong>{{ formatDateTime(cat.created_at) }}</strong>
        </div>
        <div class="kv">
          <span class="muted">更新时间</span>
          <strong>{{ formatDateTime(cat.updated_at) }}</strong>
        </div>
        <div class="kv">
          <span class="muted">备注</span>
          <strong>{{ formatText(cat.notes) }}</strong>
        </div>
      </SectionCard>
    </div>

    <div class="detail-grid">
      <SectionCard title="图片记录" subtitle="展示当前档案下的 images。">
        <div v-if="cat.images?.length" class="list-card">
          <article v-for="image in cat.images" :key="image.id" class="record-item">
            <div class="kv">
              <span class="muted">图片 ID</span>
              <strong>{{ image.id }}</strong>
            </div>
            <div class="kv">
              <span class="muted">文件路径</span>
              <strong>{{ formatText(image.file_path) }}</strong>
            </div>
            <div class="kv">
              <span class="muted">裁剪特征图</span>
              <strong>{{ formatText(image.ai_feature_path) }}</strong>
            </div>
            <div class="kv">
              <span class="muted">匹配状态</span>
              <strong>{{ formatText(image.ai_match_status) }}</strong>
            </div>
          </article>
        </div>
        <div v-else class="empty-state">当前档案还没有图片记录。</div>
      </SectionCard>

      <SectionCard title="发现记录" subtitle="展示当前档案下的 sightings。">
        <div v-if="cat.sightings?.length" class="timeline">
          <div v-for="sighting in cat.sightings" :key="sighting.id" class="timeline-item">
            <strong>{{ formatDateTime(sighting.sighted_at) }}</strong>
            <p class="muted" style="margin: 8px 0 4px;">
              地点：{{ formatText(sighting.location_text) }}
            </p>
            <p class="muted" style="margin: 0;">备注：{{ formatText(sighting.notes) }}</p>
          </div>
        </div>
        <div v-else class="empty-state">当前档案还没有发现记录。</div>
      </SectionCard>
    </div>
  </div>

  <section v-else class="panel">
    <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>
    <div v-else class="empty-state">正在加载猫档案详情...</div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import SectionCard from "../components/SectionCard.vue";
import { fetchCatArchiveDetail } from "../api";
import { formatDateTime, formatText } from "../utils/format";

const route = useRoute();
const cat = ref(null);
const errorMessage = ref("");

onMounted(async () => {
  try {
    cat.value = await fetchCatArchiveDetail(route.params.id);
  } catch (error) {
    errorMessage.value = error.message || "猫档案详情加载失败。";
  }
});
</script>
