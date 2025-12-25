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
  import Loading from '../Loading.vue'

  const API_URL = import.meta.env.VITE_API_URL
  const fallbackProfile = new URL('@/assets/images/no_img_profile.png', import.meta.url).href

  const router = useRouter()

  const accountStore = useAccountStore()
  const errorStore = useErrorStore()
  const feedStore = useFeedStore()
  const commentStore = useCommentStore()
  const { token } = storeToRefs(accountStore)
  const { comments, targetId, targetType } = storeToRefs(commentStore)

  const popularFeeds = ref([])
  const isLoading = ref(false)

  const resolveProfileUrl = (value) => {
    if (!value) return fallbackProfile
    if (value.startsWith('http://') || value.startsWith('https://')) return value
    if (!API_URL) return value
    return `${API_URL}${value}`
  }

  const formatDate = (value) => {
    return value ? value.slice(0, 10) : ''
  }

  const getFeedType = (item) => {
    return item?.page_number ? 'galfy' : 'review'
  }

  const fetchPopularFeed = async () => {
    if (!token.value) return
    isLoading.value = true
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/feed/`,
        {
          params: {
            type: 'all',
            page: 1,
            page_size: 3,
            'sort-field': 'popularity',
            'sort-direction': 'desc',
          },
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )
      popularFeeds.value = res.data?.results ?? []
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  const goDetail = (item) => {
    if (!item?.id || !item?.user?.username) return
    const type = getFeedType(item)
    if (type === 'review') {
      router.push({ name: 'review', params: { username: item.user.username, reviewId: item.id } })
      return
    }
    router.push({ name: 'galfy', params: { username: item.user.username, galfyId: item.id } })
  }

  const goBookDetail = (item) => {
    if (!item?.book?.id) return
    router.push({ name: 'bookGalfyList', params: { bookId: item.book.id } })
  }

  const toggleLike = async (item) => {
    if (!item?.id) return
    const type = getFeedType(item)
    const res = await feedStore.actionLikes(type, item.id)
    if (!res) return
    item.likes_count = res.like_count
    item.is_liked = res.is_liked
  }

  const openComments = (item) => {
    if (!item?.id) return
    commentStore.openComments({ type: getFeedType(item), id: item.id })
  }

  const updateCommentsCount = (id, type, count) => {
    const target = popularFeeds.value.find((entry) => entry.id === id && getFeedType(entry) === type)
    if (target) {
      target.comments_count = count
    }
  }

  onMounted(() => {
    fetchPopularFeed()
  })

  watch(token, () => {
    if (!token.value) return
    fetchPopularFeed()
  })

  watch([comments, targetId, targetType], ([nextComments, nextId, nextType]) => {
    if (!nextType || !nextId) return
    updateCommentsCount(nextId, nextType, nextComments?.length ?? 0)
  })
</script>

<template>
  <section class="main-feed main-section">
    <div class="tit-wrap">
      <h1 class="page-title">인기 피드</h1>
      <RouterLink class="btn-link" :to="{ name: 'feed' }">바로가기 →</RouterLink>
    </div>

    <div v-if="isLoading" class="no-content"><Loading /></div>
    <div v-else-if="popularFeeds.length === 0" class="no-content">인기 피드가 없습니다.</div>
    <ul v-else class="feed-list">
      <li
        v-for="item in popularFeeds"
        :key="item.id"
        class="feed-card"
        @click.stop="goDetail(item)"
      >
        <div class="card-header">
          <div class="profile">
            <div class="profile-image">
              <img :src="resolveProfileUrl(item.user?.profile_img)" :alt="item.user?.full_name || 'profile'">
            </div>
            <div class="profile-text">
              <p class="name">{{ item.user?.full_name }}</p>
              <span class="date">{{ formatDate(item.created_at) }}</span>
            </div>
          </div>
          <span class="type-badge">{{ getFeedType(item) === 'review' ? '리뷰' : '갈피' }}</span>
        </div>

        <div class="card-body">
          <h3 class="title">
            <span v-if="getFeedType(item) === 'review'">{{ item.title }}</span>
            <span v-else>P. {{ item.page_number }}</span>
          </h3>
          <p class="content">{{ item.content }}</p>

          <div v-if="item.book" class="book-info">
            <div class="book-thumb">
              <img
                v-if="item.book.thumbnail"
                :src="item.book.thumbnail"
                :alt="item.book.title"
              >
              <img v-else src="@/assets/images/no_img_bookcover.jpg" alt="no-image">
            </div>
            <div class="book-meta">
              <div class="book-meta-info">
                <p class="book-title">{{ item.book.title }}</p>
                <p v-if="item.book.author" class="book-author">{{ item.book.author }}</p>
                <p v-if="item.book.publisher" class="book-publisher">{{ item.book.publisher }}</p>
              </div>
              <button class="btn btn-small btn-detail" type="button" @click.stop="goBookDetail(item)">
                책 보러가기
              </button>
            </div>
          </div>
        </div>


        <div class="actions">
          <button class="btn-action" type="button" @click.stop="toggleLike(item)">
            <img :src="item.is_liked ? iconLikeActive : iconLike" alt="like">
            <span>{{ item.likes_count ?? 0 }}</span>
          </button>
          <button class="btn-action" type="button" @click.stop="openComments(item)">
            <img src="@/assets/images/common/icon_comment.png" alt="comment">
            <span>{{ item.comments_count ?? 0 }}</span>
          </button>
        </div>
      </li>
    </ul>
  </section>
</template>

<style scoped>
  .tit-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 30px;
  }

  .page-title {
    margin-bottom: 0;
  }

  .btn-link {
    font-size: 16px;
    color: #555;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }

  .btn-link:hover {
    color: #111;
  }

  .feed-list {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 24px;
  }

  .feed-card {
    background-color: #fff;
    border-radius: 20px;
    padding: 22px 22px 26px;
    border: 1px solid #eee;
    /* box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04); */
    display: flex;
    flex-direction: column;
    gap: 16px;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .feed-card:hover {
    transform: translateY(-4px);
    border-color: #d6ccf5;
    /* box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);/ */
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .profile {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .profile-image {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    overflow: hidden;
    background-color: #f2f2f2;
    border: 1px solid #eee;
  }

  .profile-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .profile-text {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .name {
    font-size: 16px;
    font-weight: 600;
  }

  .type-badge {
    font-size: 14px;
    color: #777;
    padding: 5px 12px;
    border-radius: 999px;
    background-color: #f4f4f4;
    width: fit-content;
  }

  .date {
    font-size: 13px;
    color: #888;
  }

  .card-body {
    border-top: 1px solid #ddd;
    border-bottom: 1px solid #ddd;
    padding: 30px 0;
  }

  .card-body .title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 10px;
    color: #222;
  }

  .card-body .content {
    font-size: 15px;
    color: #555;
    line-height: 1.5;
  }

  .book-info {
    display: flex;
    /* align-items: center;/ */
    gap: 12px;
    background-color: #f8f7ff;
    padding: 12px;
    border-radius: 14px;
    margin-top: 20px;
  }

  .book-thumb {
    width: 100px;
    height: 140px;
    border-radius: 10px 30px 10px 30px;
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
    justify-content: space-between;
    align-items: flex-start;
    padding: 15px 0 10px;
  }

  .book-meta-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .book-meta .book-title {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin-bottom: 5px;
  }

  .book-meta .book-author,
  .book-meta .book-publisher {
    font-size: 14px;
    color: #666;
  }

  .btn-detail {
    font-size: 14px;
  }

  .actions {
    display: flex;
    gap: 18px;
    align-items: center;
  }

  .btn-action {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    color: #444;
    background: transparent;
    border: none;
    padding: 0;
    cursor: pointer;
  }

  .btn-action img {
    width: 25px;
    height: 25px;
  }

  @media (max-width: 1200px) {
    .feed-list {
      grid-template-columns: 1fr;
    }
  }
</style>
