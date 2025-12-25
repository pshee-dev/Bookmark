<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { useRoute } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import { useFeedStore } from '@/stores/feeds'
  import FeedBase from '@/components/feed/FeedBase.vue'

  const route = useRoute()
  const bookId = route.params.bookId

  const feedStore = useFeedStore()
  const { reviewList, reviewCount } = storeToRefs(feedStore)

  onMounted(() => {
    feedStore.fetchReviews(bookId)
  })
</script>

<template>
  <div class="post-list-div">
    <h4 class="count-title">작성된 리뷰 <strong>{{ reviewCount }}</strong>개</h4>
    <ul v-if="reviewCount !== 0">
      <li
        v-for="review in reviewList"
      >
        <FeedBase :feed-type="'review'" :feed="review" :show-profile="true" :show-book-info="false" />
      </li>
    </ul>
    <div v-else class="no-content">작성된 리뷰가 없습니다.</div>
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
