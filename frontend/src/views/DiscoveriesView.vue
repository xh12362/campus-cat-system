<template>
  <div class="content-grid">
    <section class="hero-card">
      <div class="section-header">
        <div>
          <h3 class="section-title">发现记录页</h3>
          <p class="section-subtitle">当前直接请求 `GET /api/sightings`，展示真实发现记录。</p>
        </div>
      </div>

      <div class="chip-row">
        <span class="tag">location_text</span>
        <span class="tag">sighted_at</span>
        <span class="tag">cat_profile_id / image_id</span>
      </div>
    </section>

    <SectionCard title="发现记录列表" subtitle="优先按现有返回结构展示可用字段。">
      <div v-if="errorMessage" class="error-banner" style="margin-bottom: 16px;">
        {{ errorMessage }}
      </div>

      <div v-if="loading" class="empty-state">正在加载发现记录...</div>
      <div v-else-if="!records.length" class="empty-state">当前没有发现记录。</div>
      <div v-else class="list-card">
        <article v-for="record in records" :key="record.id" class="record-item">
          <div class="section-header" style="margin-bottom: 12px;">
            <div>
              <h4 class="section-title" style="font-size: 1rem;">发现记录 #{{ record.id }}</h4>
              <p class="section-subtitle">{{ formatDateTime(record.sighted_at) }}</p>
            </div>
            <span class="tag">档案 {{ formatText(record.cat_profile_id) }}</span>
          </div>

          <div class="kv">
            <span class="muted">发现地点</span>
            <strong>{{ formatText(record.location_text) }}</strong>
          </div>
          <div class="kv">
            <span class="muted">图片 ID</span>
            <strong>{{ formatText(record.image_id) }}</strong>
          </div>
          <div class="kv">
            <span class="muted">上报人</span>
            <strong>{{ formatText(record.reported_by) }}</strong>
          </div>
          <div class="kv">
            <span class="muted">备注</span>
            <strong>{{ formatText(record.notes) }}</strong>
          </div>
        </article>
      </div>
    </SectionCard>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import SectionCard from "../components/SectionCard.vue";
import { fetchDiscoveryRecords } from "../api";
import { formatDateTime, formatText } from "../utils/format";

const records = ref([]);
const loading = ref(true);
const errorMessage = ref("");

onMounted(async () => {
  try {
    records.value = await fetchDiscoveryRecords();
  } catch (error) {
    errorMessage.value = error.message || "发现记录加载失败。";
  } finally {
    loading.value = false;
  }
});
</script>
