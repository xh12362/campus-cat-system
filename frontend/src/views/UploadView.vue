<template>
  <div class="content-grid upload-flow">
    <section class="hero-card upload-hero">
      <div class="upload-hero-copy">
        <span class="eyebrow">校园流浪猫上报</span>
        <h1 class="page-title">上传一张猫咪照片，快速查看识别结果与相似档案</h1>
        <p class="page-kicker">
          按“上传照片、补充地点和时间、提交识别、查看相似猫”这条流程操作即可。页面只保留对普通用户真正有帮助的信息，
          让你更快完成一次有效上报。
        </p>

        <div class="flow-steps">
          <div class="flow-step">
            <span class="flow-index">1</span>
            <div>
              <strong>上传照片</strong>
              <p>选择现场拍到的猫咪照片，尽量保证主体清晰。</p>
            </div>
          </div>
          <div class="flow-step">
            <span class="flow-index">2</span>
            <div>
              <strong>补充发现信息</strong>
              <p>填写地点、时间和备注，方便后续建档和回查。</p>
            </div>
          </div>
          <div class="flow-step">
            <span class="flow-index">3</span>
            <div>
              <strong>查看结果</strong>
              <p>确认是否检测到猫，并查看最相似的 3 只猫。</p>
            </div>
          </div>
        </div>
      </div>

      <aside class="upload-hero-panel">
        <div class="upload-preview-shell">
          <div class="card-caption">本次待上传照片</div>
          <div v-if="previewUrl" class="preview-box upload-preview-box">
            <img :src="previewUrl" alt="待上传照片预览" />
          </div>
          <div v-else class="empty-box upload-preview-box">
            <div class="empty-box-copy">
              <strong>等待选择照片</strong>
              <span>支持常见图片格式，建议上传单只猫主体清晰的照片。</span>
            </div>
          </div>
        </div>

        <div class="upload-tip-card">
          <div class="metric-label">上传建议</div>
          <ul class="soft-list">
            <li>优先拍摄正面或侧面，避免猫咪过小或过暗。</li>
            <li>地点尽量具体到宿舍楼、食堂、教学楼或广场。</li>
            <li>备注可以写毛色、伤病、佩戴项圈等易识别信息。</li>
          </ul>
        </div>
      </aside>
    </section>

    <div class="upload-layout">
      <SectionCard
        title="上传新发现"
        subtitle="完成这一步后，系统会尝试识别照片中的猫，并推荐可能相似的档案。"
      >
        <form class="form-grid upload-form-grid" @submit.prevent="handleSubmit">
          <label class="field field-full">
            <span class="field-label">上传照片</span>
            <div class="file-drop upload-dropzone">
              <input class="file-input" type="file" accept="image/*" @change="handleFileChange" />
              <div class="file-drop-copy">
                <strong>{{ form.photo ? form.photo.name : "点击选择一张猫咪照片" }}</strong>
                <span class="helper-text">上传后将自动进行识别，并返回相似猫推荐。</span>
              </div>
            </div>
          </label>

          <label class="field">
            <span class="field-label">发现地点</span>
            <input
              v-model="form.locationText"
              class="input"
              placeholder="例如：东区宿舍 8 号楼旁、图书馆南门、第一食堂后侧"
            />
          </label>

          <label class="field">
            <span class="field-label">发现时间</span>
            <input v-model="form.sightedAt" class="input" type="datetime-local" />
          </label>

          <label class="field field-full">
            <span class="field-label">备注</span>
            <textarea
              v-model="form.notes"
              class="textarea"
              placeholder="可以补充毛色、体型、精神状态、是否受伤、是否戴项圈等信息。"
            />
          </label>

          <div v-if="errorMessage" class="field field-full">
            <div class="error-banner">{{ errorMessage }}</div>
          </div>

          <div class="field field-full">
            <div class="button-row">
              <button class="btn btn-primary" type="submit" :disabled="submitting">
                {{ submitting ? "正在上传并识别..." : "上传并查看结果" }}
              </button>
              <button class="btn btn-secondary" type="button" @click="resetForm">清空重填</button>
            </div>
          </div>
        </form>
      </SectionCard>

      <SectionCard
        title="这次会看到什么"
        subtitle="上传完成后，结果会按普通用户最关心的信息呈现，不再默认展示技术字段。"
      >
        <div class="expectation-list">
          <article class="expectation-item">
            <span class="expectation-dot"></span>
            <div>
              <strong>是否检测到猫</strong>
              <p>快速确认这张照片是否识别到了猫咪主体。</p>
            </div>
          </article>
          <article class="expectation-item">
            <span class="expectation-dot"></span>
            <div>
              <strong>是否自动建档</strong>
              <p>告诉你这次是新建档案，还是匹配到了已有猫档案。</p>
            </div>
          </article>
          <article class="expectation-item">
            <span class="expectation-dot"></span>
            <div>
              <strong>最相似的 3 只猫</strong>
              <p>展示封面图、名字、相似度和推荐原因，可直接进入档案页。</p>
            </div>
          </article>
        </div>
      </SectionCard>
    </div>

    <section v-if="uploadResult" class="content-grid upload-result-area">
      <div class="result-status-grid">
        <article class="result-status-card">
          <div class="metric-label">是否检测到猫</div>
          <div class="result-status-value" :class="hasDetectedCat ? 'is-good' : 'is-neutral'">
            {{ hasDetectedCat ? "检测到了猫" : "暂未检测到猫" }}
          </div>
          <p class="section-subtitle">
            {{ detectionSummary(uploadResult.detection) }}
          </p>
        </article>

        <article class="result-status-card">
          <div class="metric-label">是否自动建档</div>
          <div class="result-status-value" :class="uploadResult.cat_profile_id ? 'is-good' : 'is-neutral'">
            {{ uploadResult.profile_created ? "已新建档案" : uploadResult.cat_profile_id ? "已关联已有档案" : "暂未新建档案" }}
          </div>
          <p class="section-subtitle">
            {{ resultSummaryText }}
          </p>
        </article>

        <article class="result-status-card">
          <div class="metric-label">相似猫推荐</div>
          <div class="result-status-value" :class="topRecommendations.length ? 'is-good' : 'is-neutral'">
            {{ topRecommendations.length ? `已找到 ${topRecommendations.length} 只` : "暂无推荐结果" }}
          </div>
          <p class="section-subtitle">
            {{ hasDetectedCat ? "可以继续查看最相似的猫档案。" : "建议换一张更清晰的照片重新上传。" }}
          </p>
        </article>
      </div>

      <div class="result-overview">
        <SectionCard title="上传结果" subtitle="把一次上报最重要的信息收拢到这里，方便你快速做下一步判断。">
          <div class="result-overview-card">
            <div class="result-overview-media">
              <div class="preview-box result-photo-box">
                <img v-if="previewUrl" :src="previewUrl" alt="本次上传照片" />
                <div v-else class="empty-box result-photo-box">
                  <div class="empty-box-copy">
                    <strong>没有可预览的照片</strong>
                  </div>
                </div>
              </div>
            </div>

            <div class="result-overview-body">
              <div class="result-pill-row">
                <span class="tag">{{ hasDetectedCat ? "识别完成" : "未识别到猫" }}</span>
                <span class="tag">{{ uploadResult.profile_created ? "已新建档案" : uploadResult.cat_profile_id ? "已关联档案" : "待用户决定是否建档" }}</span>
                <span class="tag">{{ topRecommendations.length ? "有相似猫推荐" : "暂无相似推荐" }}</span>
              </div>

              <div class="info-pairs">
                <div class="info-pair">
                  <span>发现地点</span>
                  <strong>{{ formatText(uploadResult.sighting?.location_text || form.locationText) }}</strong>
                </div>
                <div class="info-pair">
                  <span>发现时间</span>
                  <strong>{{ formatDateTime(uploadResult.sighting?.sighted_at || form.sightedAt) }}</strong>
                </div>
                <div class="info-pair">
                  <span>识别结论</span>
                  <strong>{{ hasDetectedCat ? "照片中检测到了猫咪主体" : "这张照片暂未检测到猫咪主体" }}</strong>
                </div>
                <div class="info-pair">
                  <span>系统反馈</span>
                  <strong>{{ resultSummaryText }}</strong>
                </div>
              </div>

              <div class="button-row">
                <RouterLink
                  v-if="uploadResult.cat_profile_id"
                  class="btn btn-secondary"
                  :to="`/cats/${uploadResult.cat_profile_id}`"
                >
                  查看本次关联档案
                </RouterLink>
                <button
                  v-if="canCreateProfile"
                  class="btn btn-secondary"
                  type="button"
                  :disabled="creatingProfile"
                  @click="createArchiveFromCurrentUpload"
                >
                  {{ creatingProfile ? "正在新建档案..." : "这不是已有猫，新增档案" }}
                </button>
                <button class="btn btn-primary" type="button" @click="startNextUpload">继续上传下一张</button>
              </div>
            </div>
          </div>
        </SectionCard>
      </div>

      <SectionCard
        title="最相似的 3 只猫"
        subtitle="这些推荐能帮助你判断是不是同一只猫，也方便你直接进入已有档案查看。"
      >
        <div v-if="topRecommendations.length" class="recommendation-grid">
          <article
            v-for="candidate in topRecommendations"
            :key="candidate.cat_profile_id || candidate.sample_cat_code"
            class="recommendation-card"
          >
            <div class="recommendation-media">
              <img
                v-if="candidate.coverUrl && !hiddenCandidateImages[candidate.cat_profile_id]"
                class="recommendation-cover"
                :src="candidate.coverUrl"
                :alt="candidateDisplayName(candidate)"
                @error="hideCandidateImage(candidate.cat_profile_id)"
              />
              <div v-else class="recommendation-cover recommendation-cover-fallback">
                <strong>暂无封面图</strong>
                <span>建议进入档案查看该猫的更多图片记录。</span>
              </div>
            </div>

            <div class="recommendation-body">
              <div class="recommendation-head">
                <div>
                  <h3 class="recommendation-title">{{ candidateDisplayName(candidate) }}</h3>
                  <p class="section-subtitle">{{ candidateSubtitle(candidate) }}</p>
                </div>
                <span class="score-badge">{{ formatScore(candidate.similarity_score) }}</span>
              </div>

              <div class="recommendation-reason">
                <span>推荐原因</span>
                <strong>{{ candidateReason(candidate) }}</strong>
              </div>

              <div v-if="candidate.cat_profile_id" class="button-row">
                <RouterLink class="btn btn-primary" :to="`/cats/${candidate.cat_profile_id}`">
                  查看该猫档案
                </RouterLink>
              </div>
            </div>
          </article>
        </div>
        <div v-else class="empty-state">
          当前没有返回可展示的相似猫推荐。你可以继续上传下一张更清晰的照片，或稍后到档案列表页自行查看。
        </div>
      </SectionCard>

      <details class="more-info-panel">
        <summary>更多信息</summary>
        <div class="more-info-content">
          <div class="info-pairs">
            <div class="info-pair">
              <span>备注</span>
              <strong>{{ formatText(uploadResult.sighting?.notes || form.notes, "未填写备注") }}</strong>
            </div>
            <div class="info-pair">
              <span>识别服务状态</span>
              <strong>{{ formatText(uploadResult.message, "上传完成") }}</strong>
            </div>
            <div class="info-pair">
              <span>推荐数量</span>
              <strong>{{ uploadResult.recommendations?.length || 0 }} 条</strong>
            </div>
          </div>
        </div>
      </details>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import SectionCard from "../components/SectionCard.vue";
import { createProfileFromUpload, fetchCatArchiveDetail, submitCatUpload } from "../api";
import {
  detectionSummary,
  formatDateTime,
  formatScore,
  formatText,
  resolveAssetUrl,
} from "../utils/format";

const submitting = ref(false);
const creatingProfile = ref(false);
const previewUrl = ref("");
const errorMessage = ref("");
const uploadResult = ref(null);
const candidateProfiles = ref({});
const hiddenCandidateImages = ref({});

const initialForm = () => ({
  photo: null,
  locationText: "东区宿舍 8 号楼旁",
  sightedAt: new Date().toISOString().slice(0, 16),
  notes: "",
});

const form = reactive(initialForm());

const hasDetectedCat = computed(() => Boolean(uploadResult.value?.detection?.has_cat));

const recommendationCards = computed(() => {
  const recommendations = uploadResult.value?.recommendations || [];
  return recommendations.map((item) => {
    const profile = item.cat_profile_id ? candidateProfiles.value[item.cat_profile_id] : null;
    const coverPath =
      item.cover_image || profile?.images?.[0]?.file_path || profile?.images?.[0]?.ai_feature_path || "";

    return {
      ...item,
      cat_name: item.cat_name || profile?.name || "",
      first_seen_location: profile?.first_seen_location || "",
      coat_color: profile?.coat_color || "",
      age_stage: profile?.age_stage || "",
      coverUrl: resolveAssetUrl(coverPath),
    };
  });
});

const topRecommendations = computed(() => recommendationCards.value.slice(0, 3));

const canCreateProfile = computed(() => {
  return Boolean(
    uploadResult.value &&
      !uploadResult.value.cat_profile_id &&
      uploadResult.value.image?.id &&
      uploadResult.value.sighting?.id,
  );
});

const resultSummaryText = computed(() => {
  if (!uploadResult.value) {
    return "";
  }

  if (uploadResult.value.profile_created) {
    return "系统已根据这次上传为你新建档案。";
  }

  if (uploadResult.value.cat_profile_id) {
    return "系统将这次发现关联到了已有档案。";
  }

  return "这次上传已记录完成。你可以先查看推荐结果，再决定是否新建档案。";
});

function revokePreview() {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
}

function handleFileChange(event) {
  const [file] = event.target.files || [];
  if (!file) {
    return;
  }

  revokePreview();
  form.photo = file;
  previewUrl.value = URL.createObjectURL(file);
}

function hideCandidateImage(candidateKey) {
  hiddenCandidateImages.value = {
    ...hiddenCandidateImages.value,
    [candidateKey]: true,
  };
}

function candidateDisplayName(candidate) {
  return candidate.cat_name || `未命名猫档案 #${candidate.cat_profile_id}`;
}

function candidateSubtitle(candidate) {
  const location = formatText(candidate.first_seen_location, "常见地点待补充");
  const appearance = [candidate.coat_color, candidate.age_stage].filter(Boolean).join(" / ");
  return appearance ? `${location} · ${appearance}` : location;
}

function candidateReason(candidate) {
  if (candidate.reason) {
    return candidate.reason;
  }

  if (candidate.coat_color || candidate.age_stage) {
    return `外观特征与已建档猫较接近，尤其是${[candidate.coat_color, candidate.age_stage]
      .filter(Boolean)
      .join("、")}。`;
  }

  return "系统判断这只猫与当前照片中的猫外观相似度较高。";
}

async function loadCandidateProfiles(recommendations) {
  const ids = [...new Set((recommendations || []).map((item) => item.cat_profile_id).filter(Boolean))];

  if (!ids.length) {
    candidateProfiles.value = {};
    return;
  }

  const results = await Promise.allSettled(ids.map((id) => fetchCatArchiveDetail(id)));
  const profileMap = {};

  results.forEach((result, index) => {
    if (result.status === "fulfilled") {
      profileMap[ids[index]] = result.value;
    }
  });

  candidateProfiles.value = profileMap;
}

async function handleSubmit() {
  errorMessage.value = "";

  if (!form.photo) {
    errorMessage.value = "请先选择一张猫咪照片。";
    return;
  }

  if (!form.locationText.trim()) {
    errorMessage.value = "请填写发现地点。";
    return;
  }

  submitting.value = true;
  hiddenCandidateImages.value = {};

  try {
    const response = await submitCatUpload({
      photo: form.photo,
      locationText: form.locationText.trim(),
      sightedAt: form.sightedAt ? new Date(form.sightedAt).toISOString() : "",
      notes: form.notes.trim(),
    });

    uploadResult.value = response;
    await loadCandidateProfiles(response.recommendations);
  } catch (error) {
    errorMessage.value = error.message || "上传失败，请稍后重试。";
  } finally {
    submitting.value = false;
  }
}

async function createArchiveFromCurrentUpload() {
  if (!canCreateProfile.value || creatingProfile.value) {
    return;
  }

  creatingProfile.value = true;
  errorMessage.value = "";

  try {
    const response = await createProfileFromUpload({
      imageId: uploadResult.value.image.id,
      sightingId: uploadResult.value.sighting.id,
    });

    uploadResult.value = {
      ...uploadResult.value,
      message: response.message,
      cat_profile_id: response.cat_profile_id,
      profile_created: response.profile_created,
      image: response.image,
      sighting: response.sighting,
    };
    await loadCandidateProfiles(uploadResult.value.recommendations);
  } catch (error) {
    errorMessage.value = error.message || "新建档案失败，请稍后重试。";
  } finally {
    creatingProfile.value = false;
  }
}

function startNextUpload() {
  const keepLocation = form.locationText;
  const nextSightedAt = new Date().toISOString().slice(0, 16);
  uploadResult.value = null;
  candidateProfiles.value = {};
  hiddenCandidateImages.value = {};
  errorMessage.value = "";
  form.photo = null;
  form.notes = "";
  form.sightedAt = nextSightedAt;
  form.locationText = keepLocation;
  revokePreview();
  previewUrl.value = "";
}

function resetForm() {
  Object.assign(form, initialForm());
  errorMessage.value = "";
  uploadResult.value = null;
  candidateProfiles.value = {};
  hiddenCandidateImages.value = {};
  revokePreview();
  previewUrl.value = "";
}

onBeforeUnmount(() => {
  revokePreview();
});
</script>
