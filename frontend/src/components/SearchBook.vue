<script setup>
  import axios from 'axios'
  import { useRouter, onBeforeRouteLeave } from 'vue-router'
  import { useBookStore } from '@/stores/books'

  const router = useRouter()
  const bookStore = useBookStore()
  const props = defineProps({
    book: Object,
  })

  const goDetail = () => {
    bookStore.goDetail(props.book.isbn)
  }

  // onBeforeRouteLeave((to, from) => {
  //   // 검색어 초기화
  //   if (to.name !== 'search') {
  //     bookStore.resetSearch()
  //   }
  // })

</script>

<template>
  <!-- 썸네일 -->
  <div class="thumbnail" @click.stop="goDetail">
    <img
      v-if="book.thumbnail"
      :src="book.thumbnail"
      :alt="book.title"
    />
    <img v-else src="@/assets/images/no_img_bookcover.jpg" alt="no-image">
  </div>

  <!-- 도서 정보 -->
  <div class="info">
    <h3 class="title">{{ book.title }}</h3>
    <p class="category">{{ book.category?.name }}</p>
    <p class="author">{{ book.author }}</p>
    <p class="publisher">
      <span v-if="book.publisher">{{ book.publisher }}&nbsp;&nbsp;|&nbsp;&nbsp;</span>{{ book.published_date }}
    </p>
  </div>
</template>

<style scoped>
.thumbnail {
  border-radius: 20px 60px 20px 60px;
  overflow: hidden;
  width: 235px;
  height: 330px;
  border: 1px solid #ddd;
  flex-shrink: 0;
  cursor: pointer;
  position: relative;
}

.thumbnail::before {
  position: absolute;
  content: '자세히 보기';
  font-size: 18px;
  color: #fff;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  z-index: 2;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition-duration: .2s;
}

.thumbnail:hover::before {
  opacity: 1;
}

.thumbnail:hover img {
  transform: scale(1.2);
}

.info {
  padding: 30px 40px;
  word-break: keep-all;
}

.info .title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 20px;
  line-height: 1.2;
}

.info p {
  font-size: 20px;
  margin-top: 12px;
  line-height: 1.2;
}
</style>