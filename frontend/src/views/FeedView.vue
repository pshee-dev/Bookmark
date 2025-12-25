<script setup>
  import { computed } from 'vue'
  import { useRoute } from 'vue-router'

  const route = useRoute()

  const activeTab = computed(() => {
    return route.name === 'feedReviewList' ? 'review' : 'galfy'
  })
</script>

<template>
  <div class="bg-container feed-page">
    <h1 class="page-title">피드 전체 보기</h1>
    <div class="container-box">
      <ul class="tab-menu">
        <li>
          <RouterLink
            :to="{ name: 'feedGalfyList' }"
            :class="{ 'router-link-active': activeTab === 'galfy' }"
          >
            갈피
          </RouterLink>
        </li>
        <li>
          <RouterLink
            :to="{ name: 'feedReviewList' }"
            :class="{ 'router-link-active': activeTab === 'review' }"
          >
            리뷰
          </RouterLink>
        </li>
      </ul>

      <RouterView />
    </div>
  </div>
</template>

<style scoped>
  .feed-page {
    padding-bottom: 120px;
  }
</style>
