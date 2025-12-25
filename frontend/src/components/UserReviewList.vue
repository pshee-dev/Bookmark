<script setup>
  import { computed, ref, watch } from 'vue'
  import { useRoute } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import axios from 'axios'
  import { useAccountStore } from '@/stores/accounts'
  import { useErrorStore } from '@/stores/errors'
  import { useCommentStore } from '@/stores/comments'
  import FeedBase from '@/components/feed/FeedBase.vue'

  const API_URL = import.meta.env.VITE_API_URL

  const route = useRoute()

  const accountStore = useAccountStore()
  const errorStore = useErrorStore()
  const commentStore = useCommentStore()
  const { token } = storeToRefs(accountStore)
  const { comments, targetId, targetType } = storeToRefs(commentStore)

  const username = computed(() => route.params.username)
  const profileId = ref(null)
  const reviewList = ref([])
  const reviewCount = ref(0)
  const reviewPage = ref(1)
  const hasMore = ref(false)
  const isLoading = ref(false)

  const resetListState = () => {
    reviewList.value = []
    reviewCount.value = 0
    reviewPage.value = 1
    hasMore.value = false
  }

  const fetchProfileId = async () => {
    if (!token.value || !username.value) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/profile/`,
        {
          params: {
            username: username.value,
          },
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )
      profileId.value = res.data?.id ?? null
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }

  const fetchReviews = async ({ page = 1, append = false } = {}) => {
    if (!profileId.value || !token.value) return
    if (isLoading.value) return
    isLoading.value = true
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/${profileId.value}/reviews/`,
        {
          params: {
            page,
            page_size: 6,
            'sort-direction': 'desc',
            'sort-field': 'created_at',
          },
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )
      const results = res.data?.results ?? []
      reviewList.value = append ? [...reviewList.value, ...results] : results
      reviewCount.value = res.data?.count ?? 0
      hasMore.value = Boolean(res.data?.next)
      reviewPage.value = page
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  const loadMore = () => {
    fetchReviews({ page: reviewPage.value + 1, append: true })
  }

  const updateCommentsCount = (id, count) => {
    const target = reviewList.value.find((entry) => entry.id === id)
    if (target) {
      target.comments_count = count
    }
  }

  const refreshForUser = async () => {
    if (!token.value || !username.value) return
    resetListState()
    await fetchProfileId()
    await fetchReviews()
  }

  watch([username, token], () => {
    refreshForUser()
  }, { immediate: true })

  watch([comments, targetId, targetType], ([nextComments, nextId, nextType]) => {
    if (nextType !== 'review' || !nextId) return
    updateCommentsCount(nextId, nextComments?.length ?? 0)
  })
</script>

<template>
  <div class="tab-body">
    <h4 class="count-title">작성된 리뷰 <strong>{{ reviewCount }}</strong>개</h4>

    <div v-if="isLoading && reviewList.length === 0" class="no-content">로딩중</div>
    <div v-else-if="reviewList.length === 0" class="no-content">작성된 리뷰가 없습니다.</div>

    <ul v-else class="post-list">
      <li
        v-for="item in reviewList"
        :key="item.id"
        class="post-card"
      >
        <FeedBase :feed-type="'review'" :feed="item" :show-profile="false" :show-book-info="true" />
      </li>
    </ul>

    <button
      v-if="hasMore"
      class="btn-more"
      type="button"
      :disabled="isLoading"
      @click.stop="loadMore"
    >
      더 보기<img src="@/assets/images/common/icon_arrow_down.png" alt="더보기 버튼">
    </button>
  </div>
</template>

<style scoped>
  .tab-body {
    padding-top: 30px;
  }

  .count-title {
    font-size: 18px;
    margin-bottom: 24px;
  }

  .count-title strong {
    font-weight: 800;
  }

  .post-list {
    display: flex;
    flex-direction: column;
    gap: 18px;
  }

  .post-card {
    list-style: none;
  }
</style>
