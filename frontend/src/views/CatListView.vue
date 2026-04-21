<template>
  <div class="content-grid">
    <section class="hero-card archive-hero">
      <div>
        <span class="eyebrow">猫咪档案库</span>
        <h1 class="page-title">浏览校园里已经记录过的流浪猫档案</h1>
        <p class="page-kicker">
          档案列表改成更适合普通用户查看的卡片式布局。你可以按名字、地点、毛色或健康状态快速筛选，
          再进入详情页查看单只猫的完整记录。
        </p>
      </div>

      <div class="hero-actions">
        <RouterLink class="btn btn-primary" to="/upload">上传新照片</RouterLink>
      </div>
    </section>

    <section class="panel archive-filter-panel">
      <div class="section-header">
        <div>
          <h3 class="section-title">查找猫咪</h3>
          <p class="section-subtitle">输入你记得的信息，快速定位某只常见猫咪。</p>
        </div>
      </div>

      <div class="form-grid archive-filter-grid">
        <label class="field">
          <span class="field-label">关键词</span>
          <input
            v-model="keyword"
            class="input"
            placeholder="搜索猫名、常见地点、毛色、特征或备注"
          />
        </label>
        <label class="field">
          <span class="field-label">健康状态</span>
          <input
            v-model="healthFilter"
            class="input"
            placeholder="例如：良好、待观察、需帮助"
          />
        </label>
      </div>
    </section>

    <div class="metric-grid">
      <article class="metric-card">
        <div class="metric-label">当前档案数</div>
        <div class="metric-value">{{ archives.length }}</div>
        <div class="metric-trend">已收录在档的猫咪</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">已有名称</div>
        <div class="metric-value">{{ namedCount }}</div>
        <div class="metric-trend">更方便被同学识别和记住</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">最近更新时间</div>
        <div class="metric-value archive-latest-time">{{ latestUpdatedAt }}</div>
        <div class="helper-text">方便查看近期有新记录的猫咪</div>
      </article>
    </div>

    <section class="panel">
      <div class="section-header">
        <div>
          <h3 class="section-title">档案卡片</h3>
          <p class="section-subtitle">优先看图片和关键信息，而不是内部字段和数据表。</p>
        </div>
        <span class="tag">共 {{ filteredArchives.length }} 条结果</span>
      </div>

      <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>
      <div v-else-if="loading" class="empty-state">正在加载猫咪档案...</div>
      <div v-else-if="!filteredArchives.length" class="empty-state">
        没有找到符合条件的猫咪档案，试试换个关键词，或者先去上传页新增一条发现。
      </div>
      <div v-else class="archive-card-grid">
        <article v-for="cat in filteredArchives" :key="cat.id" class="archive-browser-card">
          <div class="archive-browser-media">
            <img
              v-if="coverImage(cat)"
              class="archive-browser-cover"
              :src="coverImage(cat)"
              :alt="archiveTitle(cat)"
            />
            <div v-else class="archive-browser-cover archive-browser-cover-fallback">
              <strong>暂无封面图</strong>
              <span>这只猫的图片记录还在持续补充中。</span>
            </div>
          </div>

          <div class="archive-browser-body">
            <div class="archive-browser-head">
              <div>
                <h3 class="archive-browser-title">{{ archiveTitle(cat) }}</h3>
                <p class="section-subtitle">{{ formatText(cat.first_seen_location, "常见地点待补充") }}</p>
              </div>
              <span class="health-badge" :class="healthBadgeClass(cat.health_status)">
                {{ healthLabel(cat.health_status) }}
              </span>
            </div>

            <div class="archive-browser-facts">
              <div class="fact-chip">{{ formatText(cat.coat_color, "毛色待补充") }}</div>
              <div class="fact-chip">{{ formatText(cat.age_stage, "年龄阶段待补充") }}</div>
            </div>

            <div class="archive-browser-meta">
              <div class="info-pair compact">
                <span>外观印象</span>
                <strong>{{ formatText(cat.distinguishing_features, "还没有补充明显特征") }}</strong>
              </div>
              <div class="info-pair compact">
                <span>最近更新</span>
                <strong>{{ formatDateTime(cat.updated_at) }}</strong>
              </div>
            </div>

            <div class="button-row">
              <RouterLink class="btn btn-secondary" :to="`/cats/${cat.id}`">查看详情</RouterLink>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { fetchCatArchives } from "../api";
import { formatDateTime, formatText, resolveAssetUrl } from "../utils/format";

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
      cat.notes,
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

function archiveTitle(cat) {
  return cat.name || `未命名猫咪 #${cat.id}`;
}

function coverImage(cat) {
  const coverPath = cat.images?.[0]?.file_path || cat.images?.[0]?.ai_feature_path || "";
  return resolveAssetUrl(coverPath);
}

function healthLabel(status) {
  return formatText(status, "状态待补充");
}

function healthBadgeClass(status) {
  const text = (status || "").toLowerCase();

  if (text.includes("伤") || text.includes("病") || text.includes("异常") || text.includes("需")) {
    return "health-badge-alert";
  }

  if (text.includes("观察") || text.includes("恢复") || text.includes("待")) {
    return "health-badge-watch";
  }

  return "health-badge-good";
}

onMounted(async () => {
  try {
    archives.value = await fetchCatArchives();
  } catch (error) {
    errorMessage.value = error.message || "猫咪档案加载失败。";
  } finally {
    loading.value = false;
  }
});
</script>
