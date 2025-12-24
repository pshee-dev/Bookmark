<script setup>
  import { computed } from 'vue'
  import { useRoute } from 'vue-router'
  import { useLibraryStore } from '@/stores/libraries'
  import { storeToRefs } from 'pinia'
  import GalfyForm from '@/components/feed/GalfyForm.vue'

  const route = useRoute()
  const createType = route.meta.type

  const libraryStore = useLibraryStore()

</script>

<template>
  <div class="bg-container">
    <h1 class="page-title">갈피 작성</h1>
    <div class="container-box">
      <GalfyForm />
    </div>
  </div>
</template>

<style scoped>

</style>