<template>
  <div class="content-grid">
    <section class="hero-card hero-grid">
      <div>
        <span class="tag">真实联调</span>
        <h3 class="page-title">上传猫照片并查看识别结果</h3>
        <p class="page-kicker">
          现在直接调用后端 `POST /api/upload`，上传成功后会展示检测结果、图片记录、发现记录和推荐匹配信息。
        </p>
        <div class="chip-row" style="margin-top: 16px;">
          <span class="tag">图片 + 地点必填</span>
          <span class="tag">展示 detection / image / sighting</span>
          <span class="tag">优先按后端真实结构渲染</span>
        </div>
      </div>

      <div class="metric-grid" style="grid-template-columns: 1fr;">
        <article class="metric-card">
          <div class="metric-label">当前接口</div>
          <div class="metric-value" style="font-size: 1.2rem;">POST /api/upload</div>
          <div class="metric-trend">已切真实上传</div>
        </article>
        <article class="metric-card">
          <div class="metric-label">结果展示</div>
          <div class="metric-value" style="font-size: 1.2rem;">8 个关键信息</div>
          <div class="helper-text">检测、推荐、建档、记录都会显示</div>
        </article>
      </div>
    </section>

    <div class="two-column">
      <SectionCard title="上传表单" subtitle="按后端要求提交图片、地点与附加信息。">
        <form class="form-grid" @submit.prevent="handleSubmit">
          <label class="field field-full">
            <span class="field-label">猫照片</span>
            <div class="file-drop">
              <input type="file" accept="image/*" @change="handleFileChange" />
              <div>
                <strong>{{ form.photo ? form.photo.name : "选择一张待识别图片" }}</strong>
                <span class="helper-text">后端字段名为 `photo`，会以 multipart/form-data 提交。</span>
              </div>
            </div>
          </label>

          <label class="field">
            <span class="field-label">发现地点</span>
            <input
              v-model="form.locationText"
              class="input"
              placeholder="如：东区宿舍 8 号楼旁"
            />
          </label>

          <label class="field">
            <span class="field-label">发现时间</span>
            <input v-model="form.sightedAt" class="input" type="datetime-local" />
          </label>

          <label class="field">
            <span class="field-label">已有猫档案 ID</span>
            <input
              v-model="form.catProfileId"
              class="input"
              type="number"
              min="1"
              placeholder="可选，不填则后端自动建档"
            />
          </label>

          <label class="field">
            <span class="field-label">上传人 ID</span>
            <input
              v-model="form.uploadedBy"
              class="input"
              type="number"
              min="1"
              placeholder="可选"
            />
          </label>

          <label class="field field-full">
            <span class="field-label">现场备注</span>
            <textarea
              v-model="form.notes"
              class="textarea"
              placeholder="记录毛色、状态、现场情况等。"
            />
          </label>

          <div v-if="errorMessage" class="field field-full">
            <div class="error-banner">{{ errorMessage }}</div>
          </div>

          <div class="field field-full">
            <div class="button-row">
              <button class="btn btn-primary" type="submit" :disabled="submitting">
                {{ submitting ? "上传中..." : "提交上传" }}
              </button>
              <button class="btn btn-secondary" type="button" @click="resetForm">重置表单</button>
            </div>
          </div>
        </form>
      </SectionCard>

      <div class="content-grid">
        <SectionCard title="图片预览" subtitle="本地预览仅用于上传前确认。">
          <div v-if="previewUrl" class="preview-box">
            <img :src="previewUrl" alt="上传预览" />
          </div>
          <div v-else class="empty-box">等待选择图片</div>
        </SectionCard>

        <SectionCard title="上传状态" subtitle="显示本次上传是否成功及基础回包状态。">
          <div v-if="uploadResult" class="info-block">
            <strong>{{ uploadResult.message }}</strong>
            <p class="muted">猫档案 ID：{{ uploadResult.cat_profile_id }}</p>
            <p class="muted" style="margin-bottom: 0;">
              {{ uploadResult.profile_created ? "本次由后端自动建档" : "本次关联已有档案" }}
            </p>
          </div>
          <div v-else class="empty-state">上传成功后，这里会出现服务端返回的处理结果。</div>
        </SectionCard>
      </div>
    </div>

    <div v-if="uploadResult" class="content-grid">
      <div class="metric-grid">
        <article class="metric-card">
          <div class="metric-label">是否检测到猫</div>
          <div class="metric-value" style="font-size: 1.4rem;">
            {{ uploadResult.detection?.has_cat ? "是" : "否" }}
          </div>
          <div class="metric-trend">{{ detectionSummary(uploadResult.detection) }}</div>
        </article>
        <article class="metric-card">
          <div class="metric-label">检测置信度</div>
          <div class="metric-value">{{ formatScore(uploadResult.detection?.confidence) }}</div>
          <div class="helper-text">后端 detection.confidence</div>
        </article>
        <article class="metric-card">
          <div class="metric-label">推荐匹配数</div>
          <div class="metric-value">{{ uploadResult.recommendations?.length || 0 }}</div>
          <div class="metric-trend">
            {{ uploadResult.profile_created ? "已自动建档" : "关联既有档案" }}
          </div>
        </article>
      </div>

      <div class="detail-grid">
        <SectionCard title="检测结果" subtitle="展示 detection 返回的核心信息。">
          <div class="kv">
            <span class="muted">检测状态</span>
            <strong>{{ detectionSummary(uploadResult.detection) }}</strong>
          </div>
          <div class="kv">
            <span class="muted">模型已加载</span>
            <strong>{{ uploadResult.detection?.model_loaded ? "是" : "否" }}</strong>
          </div>
          <div class="kv">
            <span class="muted">裁剪图路径</span>
            <strong>{{ formatText(uploadResult.detection?.cropped_image_path) }}</strong>
          </div>
          <div class="kv">
            <span class="muted">检测框数量</span>
            <strong>{{ uploadResult.detection?.detections?.length || 0 }}</strong>
          </div>

          <div
            v-if="uploadResult.detection?.detections?.length"
            class="list-card"
            style="margin-top: 16px;"
          >
            <article
              v-for="(item, index) in uploadResult.detection.detections"
              :key="`${item.label}-${index}`"
              class="record-item"
            >
              <strong>{{ item.label }}</strong>
              <p class="muted">置信度：{{ formatScore(item.score) }}</p>
              <p class="muted" style="margin-bottom: 0;">检测框：{{ item.bbox.join(", ") }}</p>
            </article>
          </div>
        </SectionCard>

        <SectionCard title="图片与发现记录" subtitle="展示 image 和 sighting 实际写入结果。">
          <div class="kv">
            <span class="muted">图片保存路径</span>
            <strong>{{ formatText(uploadResult.image?.file_path) }}</strong>
          </div>
          <div class="kv">
            <span class="muted">原始文件名</span>
            <strong>{{ formatText(uploadResult.image?.original_filename) }}</strong>
          </div>
          <div class="kv">
            <span class="muted">图片大小</span>
            <strong>{{ formatText(uploadResult.image?.file_size, "--") }} bytes</strong>
          </div>
          <div class="kv">
            <span class="muted">发现地点</span>
            <strong>{{ formatText(uploadResult.sighting?.location_text) }}</strong>
          </div>
          <div class="kv">
            <span class="muted">发现时间</span>
            <strong>{{ formatDateTime(uploadResult.sighting?.sighted_at) }}</strong>
          </div>
          <div class="kv">
            <span class="muted">自动建档</span>
            <strong>{{ uploadResult.profile_created ? "是" : "否" }}</strong>
          </div>
        </SectionCard>
      </div>

      <SectionCard title="推荐匹配结果" subtitle="按后端 recommendations 原样展示。">
        <div v-if="uploadResult.recommendations?.length" class="list-card">
          <article
            v-for="item in uploadResult.recommendations"
            :key="`${item.cat_profile_id}-${item.reason}`"
            class="record-item"
          >
            <div class="section-header" style="margin-bottom: 10px;">
              <div>
                <h4 class="section-title" style="font-size: 1rem;">
                  {{ item.cat_name || `档案 #${item.cat_profile_id}` }}
                </h4>
                <p class="section-subtitle">档案 ID：{{ item.cat_profile_id }}</p>
              </div>
              <span class="tag">{{ formatScore(item.similarity_score) }}</span>
            </div>
            <p class="muted" style="margin: 0;">{{ item.reason }}</p>
          </article>
        </div>
        <div v-else class="empty-state">当前没有返回推荐匹配结果。</div>
      </SectionCard>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, reactive, ref } from "vue";
import SectionCard from "../components/SectionCard.vue";
import { submitCatUpload } from "../api";
import {
  detectionSummary,
  formatDateTime,
  formatScore,
  formatText,
} from "../utils/format";

const submitting = ref(false);
const previewUrl = ref("");
const errorMessage = ref("");
const uploadResult = ref(null);

const initialForm = () => ({
  photo: null,
  locationText: "东区宿舍 8 号楼旁",
  sightedAt: new Date().toISOString().slice(0, 16),
  notes: "",
  catProfileId: "",
  uploadedBy: "",
});

const form = reactive(initialForm());

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

async function handleSubmit() {
  errorMessage.value = "";

  if (!form.photo) {
    errorMessage.value = "请先选择一张猫照片。";
    return;
  }

  if (!form.locationText.trim()) {
    errorMessage.value = "请填写发现地点。";
    return;
  }

  submitting.value = true;

  try {
    uploadResult.value = await submitCatUpload({
      photo: form.photo,
      locationText: form.locationText.trim(),
      sightedAt: form.sightedAt ? new Date(form.sightedAt).toISOString() : "",
      notes: form.notes.trim(),
      catProfileId: form.catProfileId,
      uploadedBy: form.uploadedBy,
    });
  } catch (error) {
    errorMessage.value = error.message || "上传失败，请稍后重试。";
  } finally {
    submitting.value = false;
  }
}

function resetForm() {
  Object.assign(form, initialForm());
  errorMessage.value = "";
  uploadResult.value = null;
  revokePreview();
  previewUrl.value = "";
}

onBeforeUnmount(() => {
  revokePreview();
});
</script>
