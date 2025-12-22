<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { useRoute } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import { useFeedStore } from '@/stores/feeds'
  import FeedBase from '@/components/feed/FeedBase.vue'

  const route = useRoute()
  const bookId = route.params.bookId

  const feedStore = useFeedStore()
  const { galfyList, galfyCount } = storeToRefs(feedStore)

  onMounted(() => {
    feedStore.fetchGalfies(bookId)
  })
</script>

<template>
  <div class="post-list-div">
    <h4 class="count-title">작성된 갈피 <strong>{{ galfyCount }}</strong>개</h4>
    <ul v-if="galfyCount !== 0">
      <li
        v-for="galfy in galfyList"
      >
        <FeedBase :feed-type="'galfy'" :feed="galfy"/>
      </li>
    </ul>
    <div v-else class="no-content">작성된 갈피가 없습니다.</div>
  </div>
</template>

<style scoped>
  .post-list-div {
    padding: 50px 30px 0;
  }

  .count-title {
    font-size: 18px;
    margin-bottom: 30px;
  }

  .count-title strong {
    font-weight: 800;
  }
</style>