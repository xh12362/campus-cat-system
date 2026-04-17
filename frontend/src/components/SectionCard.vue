<template>
  <section class="panel">
    <div v-if="title || subtitle || $slots.action" class="section-header">
      <div>
        <h3 v-if="title" class="section-title">{{ title }}</h3>
        <p v-if="subtitle" class="section-subtitle">{{ subtitle }}</p>
      </div>

      <slot name="action" />
    </div>

    <slot />
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: "",
  },
  subtitle: {
    type: String,
    default: "",
  },
});
</script>
