<template>
  <div v-if="cat" class="content-grid">
    <section class="hero-card detail-hero">
      <div class="detail-hero-media">
        <div v-if="galleryImages.length" class="detail-cover-stack">
          <img class="detail-cover-main" :src="galleryImages[0].url" :alt="archiveTitle" />
          <div v-if="galleryImages.length > 1" class="detail-cover-strip">
            <img
              v-for="image in galleryImages.slice(1, 4)"
              :key="image.key"
              class="detail-cover-thumb"
              :src="image.url"
              :alt="archiveTitle"
            />
          </div>
        </div>
        <div v-else class="empty-box detail-cover-empty">
          <div class="empty-box-copy">
            <strong>暂无猫咪主图</strong>
            <span>后续有新照片上传后，这里会展示更完整的图片记录。</span>
          </div>
        </div>
      </div>

      <div class="detail-hero-content">
        <span class="eyebrow">猫咪档案主页</span>
        <h1 class="page-title">{{ archiveTitle }}</h1>
        <p class="page-kicker">
          {{ formatText(cat.first_seen_location, "常见地点待补充") }} ·
          首次记录于 {{ formatDateTime(cat.first_seen_at) }}
        </p>

        <div class="detail-highlight-grid">
          <article class="detail-highlight-card">
            <span>健康状态</span>
            <strong>{{ formatText(cat.health_status, "待补充") }}</strong>
          </article>
          <article class="detail-highlight-card">
            <span>毛色 / 年龄</span>
            <strong>{{ appearanceSummary }}</strong>
          </article>
          <article class="detail-highlight-card">
            <span>最近更新</span>
            <strong>{{ formatDateTime(cat.updated_at) }}</strong>
          </article>
        </div>

        <div class="button-row">
          <RouterLink class="btn btn-secondary" to="/cats">返回档案列表</RouterLink>
          <RouterLink class="btn btn-primary" to="/upload">上传新照片</RouterLink>
        </div>
      </div>
    </section>

    <div class="detail-grid detail-main-grid">
      <SectionCard title="基本资料" subtitle="先看最容易帮助识别这只猫的信息。">
        <div class="info-pairs">
          <div class="info-pair">
            <span>名称</span>
            <strong>{{ archiveTitle }}</strong>
          </div>
          <div class="info-pair">
            <span>性别</span>
            <strong>{{ formatText(cat.gender, "待补充") }}</strong>
          </div>
          <div class="info-pair">
            <span>常见地点</span>
            <strong>{{ formatText(cat.first_seen_location, "待补充") }}</strong>
          </div>
          <div class="info-pair">
            <span>健康状态</span>
            <strong>{{ formatText(cat.health_status, "待补充") }}</strong>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="外观特征" subtitle="用来帮助同学快速辨认是不是同一只猫。">
        <div class="detail-feature-stack">
          <div class="fact-chip">{{ formatText(cat.coat_color, "毛色待补充") }}</div>
          <div class="fact-chip">{{ formatText(cat.age_stage, "年龄阶段待补充") }}</div>
          <div class="info-pair compact">
            <span>外观描述</span>
            <strong>{{ formatText(cat.distinguishing_features, "还没有补充明显特征") }}</strong>
          </div>
          <div class="info-pair compact">
            <span>绝育状态</span>
            <strong>{{ formatText(cat.sterilization_status, "待补充") }}</strong>
          </div>
        </div>
      </SectionCard>
    </div>

    <div class="detail-grid detail-main-grid">
      <SectionCard title="地点与时间" subtitle="帮助了解这只猫最早在哪里被记录，以及最近什么时候有更新。">
        <div class="info-pairs">
          <div class="info-pair">
            <span>首次发现地点</span>
            <strong>{{ formatText(cat.first_seen_location, "待补充") }}</strong>
          </div>
          <div class="info-pair">
            <span>首次发现时间</span>
            <strong>{{ formatDateTime(cat.first_seen_at) }}</strong>
          </div>
          <div class="info-pair">
            <span>档案创建时间</span>
            <strong>{{ formatDateTime(cat.created_at) }}</strong>
          </div>
          <div class="info-pair">
            <span>最近更新时间</span>
            <strong>{{ formatDateTime(cat.updated_at) }}</strong>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="补充说明" subtitle="这里展示更偏描述性的辅助信息。">
        <div class="info-pairs">
          <div class="info-pair">
            <span>备注</span>
            <strong>{{ formatText(cat.notes, "暂无补充备注") }}</strong>
          </div>
          <div class="info-pair">
            <span>图片数量</span>
            <strong>{{ cat.images?.length || 0 }} 张</strong>
          </div>
          <div class="info-pair">
            <span>发现记录数</span>
            <strong>{{ cat.sightings?.length || 0 }} 条</strong>
          </div>
        </div>
      </SectionCard>
    </div>

    <SectionCard title="图片记录" subtitle="优先展示与这只猫相关的照片，方便做人工比对和识别。">
      <div v-if="galleryImages.length" class="detail-gallery">
        <figure v-for="image in galleryImages" :key="image.key" class="detail-gallery-card">
          <img class="detail-gallery-image" :src="image.url" :alt="archiveTitle" />
          <figcaption class="detail-gallery-caption">
            第 {{ image.index + 1 }} 张记录图片
          </figcaption>
        </figure>
      </div>
      <div v-else class="empty-state">当前还没有可展示的图片记录。</div>
    </SectionCard>

    <SectionCard title="发现时间线" subtitle="按发现时间展示这只猫被记录的轨迹。">
      <div v-if="sortedSightings.length" class="timeline detail-timeline">
        <article v-for="sighting in sortedSightings" :key="sighting.id || sighting.sighted_at" class="timeline-item">
          <strong>{{ formatDateTime(sighting.sighted_at) }}</strong>
          <p class="muted timeline-line">{{ formatText(sighting.location_text, "地点待补充") }}</p>
          <p class="muted timeline-line">{{ formatText(sighting.notes, "暂无备注") }}</p>
        </article>
      </div>
      <div v-else class="empty-state">当前还没有发现时间线记录。</div>
    </SectionCard>

    <details class="more-info-panel">
      <summary>更多信息</summary>
      <div class="more-info-content">
        <div class="info-pairs">
          <div class="info-pair">
            <span>档案编号</span>
            <strong>#{{ cat.id }}</strong>
          </div>
          <div class="info-pair">
            <span>内部图片记录数</span>
            <strong>{{ cat.images?.length || 0 }}</strong>
          </div>
          <div class="info-pair">
            <span>内部发现记录数</span>
            <strong>{{ cat.sightings?.length || 0 }}</strong>
          </div>
        </div>
      </div>
    </details>
  </div>

  <section v-else class="panel">
    <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>
    <div v-else class="empty-state">正在加载猫咪档案详情...</div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import SectionCard from "../components/SectionCard.vue";
import { fetchCatArchiveDetail } from "../api";
import { formatDateTime, formatText, resolveAssetUrl } from "../utils/format";

const route = useRoute();
const cat = ref(null);
const errorMessage = ref("");

const archiveTitle = computed(() => {
  if (!cat.value) {
    return "";
  }

  return cat.value.name || `未命名猫咪 #${cat.value.id}`;
});

const appearanceSummary = computed(() => {
  if (!cat.value) {
    return "--";
  }

  return [formatText(cat.value.coat_color, ""), formatText(cat.value.age_stage, "")]
    .filter(Boolean)
    .join(" / ") || "待补充";
});

const galleryImages = computed(() => {
  const images = cat.value?.images || [];
  return images
    .map((image, index) => ({
      key: image.id || `${index}-${image.file_path || image.ai_feature_path}`,
      index,
      url: resolveAssetUrl(image.file_path || image.ai_feature_path || ""),
    }))
    .filter((image) => image.url);
});

const sortedSightings = computed(() => {
  const sightings = [...(cat.value?.sightings || [])];
  return sightings.sort((a, b) => new Date(b.sighted_at).getTime() - new Date(a.sighted_at).getTime());
});

onMounted(async () => {
  try {
    cat.value = await fetchCatArchiveDetail(route.params.id);
  } catch (error) {
    errorMessage.value = error.message || "猫咪档案详情加载失败。";
  }
});
</script>
