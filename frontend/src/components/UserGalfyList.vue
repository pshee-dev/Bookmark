<script setup>
  import { onMounted, ref, watch } from 'vue'
  import { storeToRefs } from 'pinia'
  import axios from 'axios'
  import { useAccountStore } from '@/stores/accounts'
  import { useErrorStore } from '@/stores/errors'
  import { useCommentStore } from '@/stores/comments'
  import FeedBase from '@/components/feed/FeedBase.vue'

  const API_URL = import.meta.env.VITE_API_URL

  const accountStore = useAccountStore()
  const errorStore = useErrorStore()
  const commentStore = useCommentStore()
  const { user, token } = storeToRefs(accountStore)
  const { comments, targetId, targetType } = storeToRefs(commentStore)

  const galfyList = ref([])
  const galfyCount = ref(0)
  const galfyPage = ref(1)
  const hasMore = ref(false)
  const isLoading = ref(false)

  const fetchGalfies = async ({ page = 1, append = false } = {}) => {
    if (!user.value?.id || !token.value) return
    if (isLoading.value) return
    isLoading.value = true
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/${user.value.id}/galfies/`,
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
      galfyList.value = append ? [...galfyList.value, ...results] : results
      galfyCount.value = res.data?.count ?? 0
      hasMore.value = Boolean(res.data?.next)
      galfyPage.value = page
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  const loadMore = () => {
    fetchGalfies({ page: galfyPage.value + 1, append: true })
  }

  const updateCommentsCount = (id, count) => {
    const target = galfyList.value.find((entry) => entry.id === id)
    if (target) {
      target.comments_count = count
    }
  }

  onMounted(() => {
    fetchGalfies()
  })

  watch([comments, targetId, targetType], ([nextComments, nextId, nextType]) => {
    if (nextType !== 'galfy' || !nextId) return
    updateCommentsCount(nextId, nextComments?.length ?? 0)
  })
</script>

<template>
  <div class="tab-body">
    <h4 class="count-title">작성된 갈피 <strong>{{ galfyCount }}</strong>개</h4>

    <div v-if="isLoading && galfyList.length === 0" class="no-content">로딩중</div>
    <div v-else-if="galfyList.length === 0" class="no-content">작성된 갈피가 없습니다.</div>

    <ul v-else class="post-list">
      <li
        v-for="item in galfyList"
        :key="item.id"
        class="post-card"
      >
        <FeedBase :feed-type="'galfy'" :feed="item" :show-profile="false" :show-book-info="true" />
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
