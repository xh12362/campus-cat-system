<template>
  <span class="badge" :class="badgeClass">{{ label }}</span>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  status: {
    type: String,
    default: "观察中",
  },
});

const statusClassMap = {
  稳定活动: "badge-safe",
  已绝育: "badge-safe",
  观察中: "badge-watch",
  待复查: "badge-watch",
  需关注: "badge-alert",
};

const badgeClass = computed(() => statusClassMap[props.status] || "badge-watch");
const label = computed(() => props.status);
</script>
