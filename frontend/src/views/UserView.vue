<script setup>
  import { computed, onMounted, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import axios from 'axios'
  import { useAccountStore } from '@/stores/accounts'
  import { useFeedStore } from '@/stores/feeds'
  import { useCommentStore } from '@/stores/comments'
  import { useErrorStore } from '@/stores/errors'
  import iconLike from '@/assets/images/common/icon_like.png'
  import iconLikeActive from '@/assets/images/common/icon_likes_active.png'

  const API_URL = import.meta.env.VITE_API_URL
  const fallbackProfile = new URL('@/assets/images/no_img_profile.png', import.meta.url).href

  const route = useRoute()
  const router = useRouter()

  const accountStore = useAccountStore()
  const errorStore = useErrorStore()
  const feedStore = useFeedStore()
  const commentStore = useCommentStore()
  const { user, token } = storeToRefs(accountStore)
  const { comments, targetId, targetType } = storeToRefs(commentStore)

  const profile = ref({})
  const libraryCounts = ref({ reading: 0, want: 0, finished: 0 })

  const galfyList = ref([])
  const reviewList = ref([])
  const galfyCount = ref(0)
  const reviewCount = ref(0)
  const galfyPage = ref(1)
  const reviewPage = ref(1)
  const galfyHasMore = ref(false)
  const reviewHasMore = ref(false)
  const galfyLoading = ref(false)
  const reviewLoading = ref(false)

  const username = computed(() => route.params.username)

  const activeTab = computed(() => {
    return route.name === 'userReviewList' ? 'review' : 'galfy'
  })

  const activeList = computed(() => {
    return activeTab.value === 'review' ? reviewList.value : galfyList.value
  })

  const activeCount = computed(() => {
    return activeTab.value === 'review' ? reviewCount.value : galfyCount.value
  })

  const activeHasMore = computed(() => {
    return activeTab.value === 'review' ? reviewHasMore.value : galfyHasMore.value
  })

  const activeLoading = computed(() => {
    return activeTab.value === 'review' ? reviewLoading.value : galfyLoading.value
  })

  const displayName = computed(() => {
    return profile.value?.full_name || user.value?.name || user.value?.username || ''
  })

  const formatDate = (value) => {
    return value ? value.slice(0, 10) : ''
  }

  const resolveProfileUrl = (value) => {
    if (!value) return fallbackProfile
    if (value.startsWith('http://') || value.startsWith('https://')) return value
    if (!API_URL) return value
    return `${API_URL}${value}`
  }

  const fetchProfile = async () => {
    if (!user.value?.id || !token.value) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/${user.value.id}/`,
        {
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )
      profile.value = res.data
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }

  const fetchLibraryCount = async (statusKey) => {
    if (!token.value) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/libraries/`,
        {
          params: {
            status: statusKey,
            limit: 1,
            offset: 0,
            'sort-direction': 'desc',
            'sort-type': 'created_at',
          },
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )
      libraryCounts.value[statusKey] = res.data?.count ?? 0
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }

  const fetchGalfies = async ({ page = 1, append = false } = {}) => {
    if (!user.value?.id || !token.value) return
    if (galfyLoading.value) return
    galfyLoading.value = true
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
      galfyHasMore.value = Boolean(res.data?.next)
      galfyPage.value = page
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      galfyLoading.value = false
    }
  }

  const fetchReviews = async ({ page = 1, append = false } = {}) => {
    if (!user.value?.id || !token.value) return
    if (reviewLoading.value) return
    reviewLoading.value = true
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/${user.value.id}/reviews/`,
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
      reviewHasMore.value = Boolean(res.data?.next)
      reviewPage.value = page
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      reviewLoading.value = false
    }
  }

  const loadMore = () => {
    if (activeTab.value === 'review') {
      fetchReviews({ page: reviewPage.value + 1, append: true })
      return
    }
    fetchGalfies({ page: galfyPage.value + 1, append: true })
  }

  const goDetail = (item) => {
    if (!item?.id || !item?.user?.username) return
    if (activeTab.value === 'review') {
      router.push({ name: 'review', params: { username: item.user.username, reviewId: item.id } })
      return
    }
    router.push({ name: 'galfy', params: { username: item.user.username, galfyId: item.id } })
  }

  const toggleLike = async (item) => {
    if (!item?.id) return
    const res = await feedStore.actionLikes(activeTab.value, item.id)
    if (!res) return
    item.likes_count = res.like_count
    item.is_liked = res.is_liked
  }

  const openComments = (item) => {
    if (!item?.id) return
    commentStore.openComments({ type: activeTab.value, id: item.id })
  }

  const updateCommentsCount = (type, id, count) => {
    if (!type || !id) return
    const targetList = type === 'review' ? reviewList.value : galfyList.value
    const target = targetList.find((entry) => entry.id === id)
    if (target) {
      target.comments_count = count
    }
  }

  const goEditProfile = () => {
    if (!username.value) return
    router.push({ name: 'userEdit', params: { username: username.value } })
  }

  onMounted(async () => {
    await fetchProfile()
    await Promise.all([
      fetchLibraryCount('reading'),
      fetchLibraryCount('want'),
      fetchLibraryCount('finished'),
      fetchGalfies(),
      fetchReviews(),
    ])
  })

  watch([comments, targetId, targetType], ([nextComments, nextId, nextType]) => {
    if (!nextType || !nextId) return
    updateCommentsCount(nextType, nextId, nextComments?.length ?? 0)
  })
</script>

<template>
  <div class="bg-container user-page">
    <div class="container-box profile-section">

      <div class="profile-info">
        <div class="profile-image">
          <img
            :src="resolveProfileUrl(profile.profile_img)"
            :alt="displayName"
          >
        </div>
        <div class="profile-text">
          <h2 class="profile-title"><b>{{ displayName }}</b>님의 책갈피</h2>
          <ul class="profile-stats">
            <li>팔로잉 <strong>{{ profile.followings_count ?? 0 }}</strong></li>
            <li>팔로워 <strong>{{ profile.followers_count ?? 0 }}</strong></li>
            <li>갈피 <strong>{{ galfyCount }}</strong></li>
            <li>리뷰 <strong>{{ reviewCount }}</strong></li>
          </ul>
        </div>
        <button class="btn btn-small btn-edit" type="button" @click.stop="goEditProfile">회원 정보 수정</button>
      </div>

      <div class="library-summary">
        <div class="summary-item">
          <p class="label">읽고 있는 책</p>
          <p class="value">{{ libraryCounts.reading }}</p>
        </div>
        <div class="summary-item">
          <p class="label">읽고 싶은 책</p>
          <p class="value">{{ libraryCounts.want }}</p>
        </div>
        <div class="summary-item">
          <p class="label">다 읽은 책</p>
          <p class="value">{{ libraryCounts.finished }}</p>
        </div>
      </div>
    </div>

    <div class="container-box">
      <ul class="tab-menu">
        <li>
          <RouterLink
            :to="{ name: 'userGalfyList', params: { username: username } }"
            class="tab-link"
            :class="{ 'router-link-active': activeTab === 'galfy' }"
          >
            갈피
          </RouterLink>
        </li>
        <li>
          <RouterLink
            :to="{ name: 'userReviewList', params: { username: username } }"
            class="tab-link"
            :class="{ 'router-link-active': activeTab === 'review' }"
          >
            리뷰
          </RouterLink>
        </li>
      </ul>

      <div class="tab-body">
        <h4 class="count-title">
          작성된 {{ activeTab === 'review' ? '리뷰' : '갈피' }} <strong>{{ activeCount }}</strong>개
        </h4>

        <div v-if="activeLoading && activeList.length === 0" class="no-content">로딩중</div>
        <div v-else-if="activeList.length === 0" class="no-content">
          {{ activeTab === 'review' ? '작성된 리뷰가 없습니다.' : '작성된 갈피가 없습니다.' }}
        </div>

        <ul v-else class="post-list">
          <li
            v-for="item in activeList"
            :key="item.id"
            class="post-card"
            @click.stop="goDetail(item)"
          >
            <div class="post-header">
              <p class="post-title">
                <span v-if="activeTab === 'review'">{{ item.title }}</span>
                <span v-else>P. {{ item.page_number }}</span>
              </p>
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
          v-if="activeHasMore"
          class="btn-more"
          type="button"
          @click.stop="loadMore"
        >
          더 보기<img src="@/assets/images/common/icon_arrow_down.png" alt="더 보기">
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .user-page {
    padding-top: 120px;
  }

  .profile-section {
    padding:60px 80px;
  }

  .profile-info {
    position: relative;
    display: flex;
    align-items: center;
    gap: 25px;
  }

  .profile-image {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    overflow: hidden;
    border: 1px solid #eee;
    background-color: #f2f2f2;
  }

  .profile-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .profile-title {
    font-size: 26px;
    margin-bottom: 12px;
  }
  
  .profile-title b {
    font-weight: 700;
  }

  .profile-stats {
    display: flex;
    gap: 18px;
    color: #666;
    font-size: 16px;
  }

  .profile-stats strong {
    color: #111;
    margin-left: 4px;
  }

  .btn-edit {
    position:absolute;
    right: 0;
    top: 0;
  }

  .library-summary {
    background-color: #f5f5f5;
    border-radius: 20px;
    margin-top: 25px;
    padding: 22px 30px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    text-align: center;
  }

  .summary-item {
    border-right: 1px solid #e5e1f2;
  }

  .summary-item:last-child {
    border-right: none;
  }

  .summary-item .label {
    font-size: 15px;
    color: #777;
    margin-bottom: 8px;
  }

  .summary-item .value {
    font-size: 24px;
    font-weight: 700;
    color: #111;
  }

  .container-box {
    margin-top: 40px;
    padding: 40px 50px 50px;
  }

  .tab-link {
    width: 100%;
    padding: 18px 0;
    font-size: 20px;
    color: #999;
    font-weight: 400;
    display: block;
    position: relative;
    text-decoration: none;
  }

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

  @media (max-width: 1024px) {
    .profile-card {
      flex-direction: column;
      align-items: flex-start;
    }

    .profile-stats {
      flex-wrap: wrap;
    }

    .library-summary {
      grid-template-columns: 1fr;
      text-align: left;
    }

    .summary-item {
      border-right: none;
      border-bottom: 1px solid #e5e1f2;
      padding-bottom: 14px;
    }

    .summary-item:last-child {
      border-bottom: none;
      padding-bottom: 0;
    }
  }

  @media (max-width: 640px) {
    .user-page {
      padding: 80px 40px 120px;
    }

    .profile-card,
    .feed-section {
      padding: 30px;
      border-radius: 24px 50px 24px 50px;
    }

    .book-info {
      flex-direction: column;
      align-items: flex-start;
    }
  }
</style>
