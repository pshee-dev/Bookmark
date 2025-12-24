<script setup>
  import { computed, ref, watch } from 'vue'
  import { useRoute } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import axios from 'axios'
  import { useAccountStore } from '@/stores/accounts'
  import { useErrorStore } from '@/stores/errors'
  import ReviewForm from '@/components/feed/ReviewForm.vue'

  const route = useRoute()
  const errorStore = useErrorStore()
  const accountStore = useAccountStore()
  const { token } = storeToRefs(accountStore)

  const API_URL = import.meta.env.VITE_API_URL
  const reviewId = computed(() => route.params.reviewId)
  const review = ref(null)

  const fetchReviewDetail = async (id) => {
    if (!id) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/reviews/${id}/`,
        token.value
          ? { headers: { Authorization: `Token ${token.value}` } }
          : {}
      )
      review.value = res.data
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }

  watch(
    () => reviewId.value,
    (id) => {
      fetchReviewDetail(id)
    },
    { immediate: true }
  )
</script>

<template>
  <div class="bg-container">
    <h1 class="page-title">리뷰 수정</h1>
    <div class="container-box">
      <ReviewForm mode="update" :initial-value="review" />
    </div>
  </div>
</template>

<style scoped>

</style>
