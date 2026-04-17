<template>
  <div class="content-grid">
    <section class="hero-card">
      <div class="section-header">
        <div>
          <h3 class="section-title">猫档案列表</h3>
          <p class="section-subtitle">当前直接请求 `GET /api/cats`，按真实字段展示档案概览。</p>
        </div>
        <RouterLink class="btn btn-primary" to="/upload">上传新发现</RouterLink>
      </div>

      <div class="form-grid">
        <label class="field">
          <span class="field-label">搜索关键词</span>
          <input
            v-model="keyword"
            class="input"
            placeholder="搜索名称、地点、毛色、健康状态"
          />
        </label>
        <label class="field">
          <span class="field-label">健康状态</span>
          <input
            v-model="healthFilter"
            class="input"
            placeholder="如：待观察、良好、待复查"
          />
        </label>
      </div>
    </section>

    <div class="metric-grid">
      <article class="metric-card">
        <div class="metric-label">档案总数</div>
        <div class="metric-value">{{ archives.length }}</div>
        <div class="metric-trend">真实接口数据</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">已填写名称</div>
        <div class="metric-value">{{ namedCount }}</div>
        <div class="metric-trend">后续可继续补全资料</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">最近更新时间</div>
        <div class="metric-value" style="font-size: 1.15rem;">{{ latestUpdatedAt }}</div>
        <div class="helper-text">来自 `updated_at`</div>
      </article>
    </div>

    <section class="table-card">
      <div class="section-header">
        <div>
          <h3 class="section-title">档案明细</h3>
          <p class="section-subtitle">以后端返回字段为准，不额外假设业务状态。</p>
        </div>
      </div>

      <div v-if="errorMessage" class="error-banner" style="margin-bottom: 16px;">
        {{ errorMessage }}
      </div>

      <div v-if="loading" class="empty-state">正在加载猫档案...</div>
      <div v-else-if="!filteredArchives.length" class="empty-state">当前没有可展示的猫档案。</div>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>档案</th>
              <th>首次发现地点</th>
              <th>毛色 / 年龄</th>
              <th>健康状态</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cat in filteredArchives" :key="cat.id">
              <td>
                <div>
                  <strong>{{ cat.name || `未命名档案 #${cat.id}` }}</strong>
                  <div class="muted">ID：{{ cat.id }} · 性别：{{ formatText(cat.gender) }}</div>
                </div>
              </td>
              <td>{{ formatText(cat.first_seen_location) }}</td>
              <td>
                {{ formatText(cat.coat_color) }} / {{ formatText(cat.age_stage) }}
              </td>
              <td>{{ formatText(cat.health_status) }}</td>
              <td>{{ formatDateTime(cat.updated_at) }}</td>
              <td>
                <RouterLink class="btn btn-secondary" :to="`/cats/${cat.id}`">查看详情</RouterLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { fetchCatArchives } from "../api";
import { formatDateTime, formatText } from "../utils/format";

const archives = ref([]);
const loading = ref(true);
const errorMessage = ref("");
const keyword = ref("");
const healthFilter = ref("");

const filteredArchives = computed(() => {
  return archives.value.filter((cat) => {
    const haystack = [
      cat.name,
      cat.first_seen_location,
      cat.coat_color,
      cat.health_status,
      cat.distinguishing_features,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    const matchesKeyword = !keyword.value || haystack.includes(keyword.value.toLowerCase());
    const matchesHealth =
      !healthFilter.value ||
      (cat.health_status || "").toLowerCase().includes(healthFilter.value.toLowerCase());
    return matchesKeyword && matchesHealth;
  });
});

const namedCount = computed(() => archives.value.filter((item) => item.name).length);

const latestUpdatedAt = computed(() => {
  if (!archives.value.length) {
    return "--";
  }

  const sorted = [...archives.value].sort(
    (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime(),
  );
  return formatDateTime(sorted[0].updated_at);
});

onMounted(async () => {
  try {
    archives.value = await fetchCatArchives();
  } catch (error) {
    errorMessage.value = error.message || "猫档案加载失败。";
  } finally {
    loading.value = false;
  }
});
</script>
