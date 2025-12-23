<script setup>
  import { computed, watch, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import { useFeedStore } from '@/stores/feeds'
  import { useLibraryStore } from '@/stores/libraries'
  import FeedBase from '@/components/feed/FeedBase.vue'
  import LibraryModal from '@/components/library/LibraryModal.vue'
  import { useScrollReveal } from '@/composables/scrollReveal'
  const { collect } = useScrollReveal()

  const route = useRoute()
  const router = useRouter()
  const libraryId = computed(() => route.params.libraryId)

  const libraryStore = useLibraryStore()
  const { libraryBook } = storeToRefs(libraryStore)
  const { fetchLibraryDetail, openLibraryModal, deleteLibrary } = libraryStore

  const book = computed(() => libraryBook.value?.book ?? {})

  const statusLabel = computed(() => {
    const map = {
      reading: '읽고 있는 책',
      want: '읽고 싶은 책',
      finished: '다 읽은 책',
    }
    return map[libraryBook.value?.status] ?? ''
  })

  const handleUpdateLibrary = () => {
    if (!libraryBook.value?.id || !book.value?.id) return
    openLibraryModal({
      mode: 'update',
      book: book.value,
      bookId: book.value.id,
      libraryId: libraryBook.value.id,
      initialValue: libraryBook.value,
    })
  }

  watch(
    () => libraryId.value,
    (nextId) => {
      if (!nextId) return
      if (!libraryBook.value?.id || libraryBook.value.id !== Number(nextId)) {
        fetchLibraryDetail(nextId)
      }
    },
    { immediate: true }
  )
  
  const handleDeleteLibrary = () => {
    if (!libraryBook.value?.id) return
    const confirmed = window.confirm('정말 삭제하시겠습니까?')
    if (confirmed) {
      deleteLibrary(libraryId.value)
    }
  }

  const username = route.params.username

  const feedStore = useFeedStore()
  const { galfyList, galfyCount } = storeToRefs(feedStore)

  onMounted(() => {
    feedStore.fetchGalfies(book.value.id)
  })
</script>

<template>
  <div class="bg-container">
    <div class="tit-wrap">
      <h1 class="page-title">{{ book.title }}</h1>
      <div class="btn-wrap">
        <button class="btn btn-small" @click="handleUpdateLibrary">수정</button>
        <button class="btn btn-small" @click="handleDeleteLibrary">삭제</button>
      </div>
    </div>
    <section class="container-box book-detail">
      <div class="book-info">
        <div class="thumbnail fadein" :ref="collect">
          <img v-if="book.thumbnail" :src="book.thumbnail" :alt="book.title">
          <img v-else src="@/assets/images/no_img_bookcover.jpg" alt="no-image">
        </div>

        <div class="info fadeinright80" :ref="collect">
          <h3 class="title">도서 정보</h3>
          <p v-if="book.category?.name"><span class="cate">분야</span> {{ book.category?.name }}</p>
          <p v-if="book.author"><span class="cate">작가</span> {{ book.author }}</p>
          <p v-if="book.publisher"><span class="cate">출판사</span> {{ book.publisher }}</p>
          <p v-if="book.published_date"><span class="cate">출판일</span> {{ book.published_date }}</p>
          <p v-if="book.isbn"><span class="cate">ISBN</span> {{ book.isbn }}</p>
        </div>
      </div>

      <div class="info library-info fadeinright80" :ref="collect">
        <h3 class="title">독서 상태</h3>
        <p v-if="libraryBook.rating !== null && libraryBook.rating !== undefined"><span class="cate">평점</span> {{ libraryBook.rating }}</p>
        <p v-if="libraryBook.start_date"><span class="cate">독서 날짜</span> {{ libraryBook.start_date }} ~ <span v-if="libraryBook.finish_date">{{ libraryBook.finish_date }}</span></p>
        <p v-if="libraryBook.current_page"><span class="cate">독서량</span> {{ libraryBook.current_page }} / {{ book.page }} 페이지</p>
        <p><span class="cate">리뷰</span> </p>
      </div>
      <span v-if="statusLabel" class="status-label fadeinup" :ref="collect">{{ statusLabel }}</span>

    </section>

    <section class="container-box">
      <div class="post-list-div">
        <div class="tit-wrap">
          <h4 class="count-title">작성된 갈피 <strong>{{ galfyCount }}</strong>개</h4>
          <button @click="createGalfy" class="btn btn-small">작성하기</button>
        </div>
        <ul v-if="galfyCount !== 0">
          <li
            v-for="galfy in galfyList"
          >
            <FeedBase :feed-type="'galfy'" :feed="galfy"/>
          </li>
        </ul>
        <div v-else class="no-content">작성된 갈피가 없습니다.</div>
      </div>
    </section>

    <LibraryModal />
  </div>
</template>

<style scoped>
  .container-box {
    margin-top: 30px;
  }

  .tit-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .page-title {
    margin: 0;
  }
  
  .btn-wrap {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    margin-right: 40px;
  }

  .book-detail {
    position: relative;
    padding: 60px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  .book-detail > div {
    width:50%;
  }

  .book-info {
    display: flex;
    border-right: 1px solid #999;
  }

  .thumbnail {
    border-radius: 20px 60px 20px 60px;
    overflow: hidden;
    width: 235px;
    height: 330px;
    border: 1px solid #ddd;
    flex-shrink: 0;
  }

  .thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition-duration: .2s;
  }

  .info {
    padding: 30px 40px;
    word-break: keep-all;
  }

  .info .title {
    font-size: 32px;
    font-weight: 600;
    margin-bottom: 30px;
    line-height: 1.2;
  }

  .info p {
    display: flex;
    font-size: 18px;
    margin-top: 15px;
    line-height: 1.2;
  }

  .info p .cate {
    display: inline-block;
    min-width: 80px;
    font-weight: 600;
  }

  .library-info {
    padding-left: 80px;
    position: relative;
  }

  .status-label {
    position: absolute;
    display: block;
    top: 90px;
    right: 100px;
    font-size: 18px;
    padding: 10px 20px;
    background-color: #8651b5;
    color: #fff;
    border-radius: 999px;
  }

  .post-list-div {
    padding: 50px 30px 0;
  }

  .count-title {
    font-size: 18px;
  }

  .count-title strong {
    font-weight: 800;
  }

  .fadeinright80.show {
    animation-delay: .2s;
  }

  .fadeinup.show {
    animation-delay: .4s;
  }
</style>

