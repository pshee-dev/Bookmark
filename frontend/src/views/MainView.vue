<script setup>
  import MainVisual from '@/components/main/MainVisual.vue'
  import MainBookList from '@/components/main/MainBookList.vue'
  import MainLibraryList from '@/components/main/MainLibraryList.vue'
  import MainFeedList from '@/components/main/MainFeedList.vue'

</script>

<template>
  <MainVisual />
  <div class="bg-container">
    <MainBookList />
    <MainLibraryList />
    <MainFeedList />
  </div>
</template>

<style scoped>
.bg-container {
  margin-top: 80px;
}
</style>