<script setup>
  import { computed, onMounted, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import axios from 'axios'
  import { useAccountStore } from '@/stores/accounts'
  import { useErrorStore } from '@/stores/errors'
  import { useLibraryStore } from '@/stores/libraries'
  import LibraryModal from '@/components/library/LibraryModal.vue'
  import Loading from '@/components/Loading.vue'

  const API_URL = import.meta.env.VITE_API_URL

  const route = useRoute()
  const router = useRouter()
  const errorStore = useErrorStore()
  const accountStore = useAccountStore()
  const libraryStore = useLibraryStore()
  const { token } = storeToRefs(accountStore)
  const { openLibraryModal } = libraryStore

  const reviewId = computed(() => route.params.reviewId)
  const keywords = ref([])
  const books = ref([])
  const isLoading = ref(false)
  const activeIndex = ref(0)

  const currentBook = computed(() => books.value[activeIndex.value] ?? null)

  const coverFallback = new URL('@/assets/images/no_img_bookcover.jpg', import.meta.url).href
  const resolveCover = (value) => value || coverFallback

  const getBookAt = (offset) => {
    const total = books.value.length
    if (!total) return null
    const nextIndex = (activeIndex.value + offset + total) % total
    return books.value[nextIndex]
  }

  const sideBooks = computed(() => {
    const total = books.value.length
    if (total <= 1) return []
    const count = Math.min(2, total - 1)
    return Array.from({ length: count }, (_, idx) => getBookAt(idx + 1))
  })

  const goPrev = () => {
    const total = books.value.length
    if (total <= 1) return
    activeIndex.value = (activeIndex.value - 1 + total) % total
  }

  const goNext = () => {
    const total = books.value.length
    if (total <= 1) return
    activeIndex.value = (activeIndex.value + 1) % total
  }

  const setActiveByOffset = (offset) => {
    const total = books.value.length
    if (!total) return
    activeIndex.value = (activeIndex.value + offset + total) % total
  }

  const goBookDetail = (bookId) => {
    if (!bookId) return
    router.push({ name: 'bookGalfyList', params: { bookId } })
  }

  const addToLibrary = (book) => {
    if (!book?.id) return
    openLibraryModal({ mode: 'create', book, bookId: book.id })
  }

  const fetchRecommendations = async () => {
    if (!reviewId.value) return
    isLoading.value = true
    try {
      const res = await axios.get(
        `${API_URL}/api/recommendations/${reviewId.value}/`,
        token.value
          ? { headers: { Authorization: `Token ${token.value}` } }
          : {}
      )
      keywords.value = res.data?.keywords ?? []
      books.value = res.data?.books ?? []
      activeIndex.value = 0
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  onMounted(() => {
    fetchRecommendations()
  })

  watch(reviewId, () => {
    fetchRecommendations()
  })
</script>

<template>
  <div class="bg-container recommend-view">
    <h1 class="page-title">AI 도서 추천</h1>
    <div class="container-box">
      <p class="recommend-lead">
        방금 작성한 리뷰에서 아래와 같은 독서 취향이 느껴졌어요 !
      </p>
      <div class="tag-list" v-if="keywords.length">
        <span v-for="keyword in keywords" :key="keyword" class="tag"># {{ keyword }}</span>
      </div>

      <div v-if="isLoading" class="no-content">
        <Loading />
      </div>
      <div v-else-if="books.length === 0" class="no-content">추천 결과가 없습니다.</div>

      <div v-else class="recommend-carousel">
        <button class="nav-btn nav-left" type="button" @click="goPrev">
          <img src="@/assets/images/common/icon_arrow_left.png" alt="prev">
        </button>

        <div class="recommend-stage">
          <div class="cover-wrap">
            <img :src="resolveCover(currentBook?.thumbnail)" :alt="currentBook?.title || 'cover'">
          </div>

          <div class="info-card">
            <div class="quote-mark">“</div>
            <p class="meta-value">{{ currentBook?.category?.name || '-' }}</p>
            <h2 class="book-title">{{ currentBook?.title }}</h2>
            <p class="book-meta">
              {{ currentBook?.author || '작가 미상' }}
              <span v-if="currentBook?.publisher"> | {{ currentBook.publisher }}</span>
            </p>
            <div class="reason-box">
              <p class="reason-title">추천 이유</p>
              <p class="reason-text">{{ currentBook?.reason || '리뷰와 비슷한 분위기의 책이에요.' }}</p>
            </div>
            <div class="action-row">
              <button class="btn btn-small" type="button" @click="goBookDetail(currentBook?.id)">책 보러가기</button>
              <button class="btn btn-small btn-ghost" type="button" @click="addToLibrary(currentBook)">서재에 담기</button>
            </div>
          </div>
        </div>

        <div class="side-list">
          <button
            v-for="(book, index) in sideBooks"
            :key="book?.id ?? index"
            class="side-card"
            type="button"
            @click="setActiveByOffset(index + 1)"
          >
            <img :src="resolveCover(book?.thumbnail)" :alt="book?.title || 'cover'">
          </button>
        </div>

        <button class="nav-btn nav-right" type="button" @click="goNext">
          <img src="@/assets/images/common/icon_arrow_left.png" alt="next">
        </button>
      </div>
    </div>
  </div>

  <LibraryModal />
</template>

<style scoped>
  .recommend-view {
    padding-bottom: 180px;
  }

  .container-box {
    padding: 60px 80px 80px;
  }

  .recommend-lead {
    font-size: 20px;
    color: #333;
    font-weight: 600;
  }

  .tag-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 18px 0 40px;
  }

  .tag {
    padding: 8px 16px;
    border-radius: 999px;
    background: #f0f0f5;
    color: #555;
    font-size: 14px;
    font-weight: 500;
  }

  .recommend-carousel {
    position: relative;
    display: flex;
    align-items: center;
    gap: 32px;
  }

  .recommend-stage {
    border-radius: 30px;
    flex: 1;
    display: flex;
    align-items: center;
  }

  .cover-wrap {
    width: 235px;
    height: 330px;
    border-radius: 20px 60px 20px 60px;
    overflow: hidden;
    z-index: 1;
  }

  .cover-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .info-card {
    border-radius: 30px;
    padding: 60px;
    padding-left: 100px;
    margin-left: -60px;
    position: relative;
    background-color: #f5f5f5;
    flex: 1;
    z-index: 0;
  }

  .quote-mark {
    font-size: 52px;
    line-height: 1;
    color: #d5d5d5;
    margin-bottom: 10px;
  }

  .meta-label {
    font-size: 13px;
    color: #888;
    margin-bottom: 4px;
  }

  .meta-value {
    font-size: 14px;
    font-weight: 600;
    color: #333;
    margin-bottom: 12px;
  }

  .book-title {
    font-size: 24px;
    font-weight: 800;
    margin-bottom: 15px;
    line-height: 1.2;
  }

  .book-meta {
    color: #777;
    font-size: 16px;
    margin-bottom: 30px;
  }

  .reason-box {
    padding: 25px 20px;
    border-radius: 20px;
    background: #fff;
    margin-bottom: 50px;
  }

  .reason-title {
    font-weight: 700;
    margin-bottom: 6px;
    font-size: 16px;
    color: #333;
  }

  .reason-text {
    font-size: 18px;
    color: #555;
    line-height: 1.6;
  }

  .action-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }

  .btn-ghost {
    background: #fff;
    color: #333;
    border: 1px solid #ddd;
  }

  .btn-ghost:hover {
    background: #f4f4f4;
  }

  .side-list {
    display: flex;
    gap: 25px;
  }

  .side-card {
    width: 235px;
    height: 330px;
    border-radius: 20px 60px 20px 60px;
    border: none;
    overflow: hidden;
    cursor: pointer;
  }

  .side-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .nav-btn {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: none;
    background: #111;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    z-index: 2;
  }

  .nav-btn img {
    width: 20px;
    height: 20px;
  }

  .nav-left {
    left: -22px;
  }

  .nav-right {
    right: -22px;
  }

  .nav-right img {
    transform: rotate(180deg);
  }

  @media (max-width: 1200px) {
    .recommend-carousel {
      flex-direction: column;
    }

    .recommend-stage {
      grid-template-columns: 1fr;
    }

    .side-list {
      order: 3;
    }
  }
</style>
