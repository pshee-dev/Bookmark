<script setup>
  import { useBookStore } from '@/stores/books'
  import { storeToRefs } from 'pinia'
  const bookStore = useBookStore()
  const { bookDetail } = storeToRefs(bookStore)

</script>

<template>
  <div class="bg-container">
    <h1 class="page-title">{{ bookDetail.title }}</h1>
    <!-- 도서 상세 정보 section -->
    <section class="container-box book-detail">
      <div class="book">
        <!-- 썸네일 -->
        <div class="thumbnail">
          <img
            v-if="bookDetail.thumbnail"
            :src="bookDetail.thumbnail"
            :alt="bookDetail.title"
          />
          <img v-else src="@/assets/images/no_img_bookcover.jpg" alt="no-image">
        </div>

        <!-- 도서 정보 -->
        <div class="info">
          <h3 class="title">도서 정보</h3>
          <p v-if="bookDetail.category.name"><span class="cate">분야</span> {{ bookDetail.category.name }}</p>
          <p v-if="bookDetail.author"><span class="cate">작가</span> {{ bookDetail.author }}</p>
          <p v-if="bookDetail.publisher"><span class="cate">출판사</span> {{ bookDetail.publisher }}</p>
          <p v-if="bookDetail.published_date"><span class="cate">출판일</span> {{ bookDetail.published_date }}</p>
          <p v-if="bookDetail.isbn"><span class="cate">ISBN</span> {{ bookDetail.isbn }}</p>
        </div>
      </div>
      <button class="btn">서재에 담기</button>
    </section>

    <!-- 도서 갈피/리뷰 리스트 section -->
    <section class="container-box post-list">
      <ul class="tab-menu">
        <li><RouterLink :to="{name: 'bookGalfyList', params: {bookId: bookDetail.id}}">갈피</RouterLink></li>
        <li><RouterLink :to="{name: 'bookReviewList', params: {bookId:  bookDetail.id}}">리뷰</RouterLink></li>
      </ul>

      <RouterView />
    </section>
  </div>
</template>

<style scoped>
  .container-box:not(:first-child) {
    margin-top: 30px;
  }

  .book-detail {
    padding: 60px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  .post-list {
    padding: 20px 50px 80px;
  }

  .book {
    display: flex;
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
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 30px;
    line-height: 1.2;
  }

  .info p {
    font-size: 18px;
    margin-top: 12px;
    line-height: 1.2;
  }

  .info p .cate {
    display: inline-block;
    min-width: 70px;
    font-weight: 600;
  }
</style>