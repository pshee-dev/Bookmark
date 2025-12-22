<script setup>
  import { Swiper, SwiperSlide } from 'swiper/vue'
  import { Navigation, Autoplay } from 'swiper/modules'
  import 'swiper/css'
  import 'swiper/css/navigation'

  import { ref } from 'vue'
  import axios from 'axios'

  const API_URL = import.meta.env.VITE_ALADIN_API_URL
  const API_KEY = import.meta.env.VITE_ALADIN_API_KEY
  const bookList = ref([])
  
  axios({
    method: 'get',
    url: `${API_URL}/ItemList.aspx`,
    params: {
      ttbkey: API_KEY,
      QueryType: 'Bestseller',
      SearchTarget: 'Book',
      MaxResult: 12,
      start: 1,
      output: 'JS',
      Version: 20131101,
    },
  })
    .then(res => {
      console.log(res.data)
      bookList.value = res.data.item
    })
    .catch(err => console.log(err))
  

</script>

<template>
  <section class="main-book main-section">
    <div class="tit-wrap">
      <h1 class="page-title">베스트 셀러</h1>
      <div class="btn-swiper">
        <button class="btn-prev"><img src="@/assets/images/common/icon_arrow_left.png" alt="이전 버튼"></button>
        <button class="btn-next"><img src="@/assets/images/common/icon_arrow_left.png" alt="다음 버튼"></button>
      </div>
    </div>

    <Swiper 
      class="book-list"
      :modules="[Autoplay, Navigation]"
      :slides-per-view="6"
      :space-between="20"
      :loop="true"
      :autoplay="{ delay: 2000, disableOnInteraction: false }"
      :navigation="{
        nextEl: '.btn-next',
        prevEl: '.btn-prev',
      }"
    >
      <SwiperSlide 
        v-for="book in bookList"
        :key="book.isbn13"
      >
        <div class="thumbnail">
          <img v-if="book.cover" :src="book.cover" :alt="book.title">
          <!-- <img v-else src="@/assets/images/no_img_bookcover.jpg" alt="no-image"> -->
        </div>
        <div class="info">
          <h2 class="title">{{ book.title }}</h2>
          <p class="author">{{ book.author }}</p>
        </div>
      </SwiperSlide>
    </Swiper>
  </section>
</template>

<style scoped>
.tit-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.btn-swiper {
  display: flex;
  gap: 10px;
}

.btn-swiper button {
  width:50px;
  height:50px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  background-color: #222;
  border: none;
  cursor: pointer;
  transition: all ease .2s;
}

.btn-swiper button:hover {
  background-color: #456AFF;
}

.btn-next img {
  transform: rotate(180deg);
}
</style>