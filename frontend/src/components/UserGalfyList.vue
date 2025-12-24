<script setup>
  import { onMounted, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import axios from 'axios'
  import { useAccountStore } from '@/stores/accounts'
  import { useErrorStore } from '@/stores/errors'
  import { useFeedStore } from '@/stores/feeds'
  import { useCommentStore } from '@/stores/comments'
  import iconLike from '@/assets/images/common/icon_like.png'
  import iconLikeActive from '@/assets/images/common/icon_likes_active.png'

  const API_URL = import.meta.env.VITE_API_URL

  const router = useRouter()

  const accountStore = useAccountStore()
  const errorStore = useErrorStore()
  const feedStore = useFeedStore()
  const commentStore = useCommentStore()
  const { user, token } = storeToRefs(accountStore)
  const { comments, targetId, targetType } = storeToRefs(commentStore)

  const galfyList = ref([])
  const galfyCount = ref(0)
  const galfyPage = ref(1)
  const hasMore = ref(false)
  const isLoading = ref(false)

  const formatDate = (value) => {
    return value ? value.slice(0, 10) : ''
  }

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

  const goDetail = (item) => {
    if (!item?.id || !item?.user?.username) return
    router.push({ name: 'galfy', params: { username: item.user.username, galfyId: item.id } })
  }

  const toggleLike = async (item) => {
    if (!item?.id) return
    const res = await feedStore.actionLikes('galfy', item.id)
    if (!res) return
    item.likes_count = res.like_count
    item.is_liked = res.is_liked
  }

  const openComments = (item) => {
    if (!item?.id) return
    commentStore.openComments({ type: 'galfy', id: item.id })
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
        @click.stop="goDetail(item)"
      >
        <div class="post-header">
          <p class="post-title">P. {{ item.page_number }}</p>
          <span class="post-date">{{ formatDate(item.created_at) }}</span>
        </div>

        <p class="post-content">{{ item.content }}</p>

        <div class="book-info">
          <div class="book-thumb">
            <img
              v-if="item.book?.thumbnail"
              :src="item.book.thumbnail"
              :alt="item.book.title"
            >
            <img v-else src="@/assets/images/no_img_bookcover.jpg" alt="no-image">
          </div>
          <div class="book-meta">
            <p class="book-title">{{ item.book?.title }}</p>
            <p v-if="item.book?.author" class="book-author">{{ item.book.author }}</p>
            <p v-if="item.book?.publisher" class="book-publisher">{{ item.book.publisher }}</p>
          </div>
        </div>

        <div class="post-actions">
          <button class="btn-action" type="button" @click.stop="toggleLike(item)">
            <img
              :src="item.is_liked ? iconLikeActive : iconLike"
              alt="like"
            >
            <span>{{ item.likes_count ?? 0 }}</span>
          </button>
          <button class="btn-action" type="button" @click.stop="openComments(item)">
            <img src="@/assets/images/common/icon_comment.png" alt="comment">
            <span>{{ item.comments_count ?? 0 }}</span>
          </button>
        </div>
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
    background-color: #f8f5ff;
    border-radius: 20px;
    padding: 30px 40px 50px;
    border: 1px solid transparent;
    transition: border 0.2s ease, transform 0.2s ease;
    cursor: pointer;
  }

  .post-card:hover {
    border-color: #d6ccf5;
    transform: translateY(-2px);
  }

  .post-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;
  }

  .post-title {
    font-size: 18px;
    font-weight: 700;
    color: #222;
  }

  .post-date {
    font-size: 14px;
    color: #888;
  }

  .book-info {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 18px;
  }

  .book-thumb {
    width: 70px;
    height: 95px;
    border-radius: 12px 24px 12px 24px;
    overflow: hidden;
    border: 1px solid #eee;
    background-color: #f1f1f1;
    flex-shrink: 0;
  }

  .book-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .book-meta {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .book-meta .book-title {
    font-size: 16px;
    font-weight: 600;
    color: #333;
  }

  .book-meta .book-author,
  .book-meta .book-publisher {
    font-size: 14px;
    color: #666;
  }

  .post-content {
    font-size: 16px;
    color: #555;
    line-height: 1.6;
    margin-bottom: 20px;
  }

  .post-actions {
    display: flex;
    gap: 18px;
    align-items: center;
  }

  .btn-action {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
    color: #444;
    background: transparent;
    border: none;
    padding: 0;
    cursor: pointer;
  }

  .btn-action img {
    width: 18px;
    height: 18px;
  }
</style>
