<script setup>
  import { Swiper, SwiperSlide } from 'swiper/vue'
  import { Navigation, Autoplay } from 'swiper/modules'
  import 'swiper/css'
  import 'swiper/css/navigation'

  import { nextTick, onMounted, ref } from 'vue'
  import axios from 'axios'  

  import { useScrollReveal } from '@/composables/scrollReveal'
  const { collect } = useScrollReveal()

  import { useErrorStore } from '@/stores/errors'
  const errorStore = useErrorStore()

  const API_URL = import.meta.env.VITE_API_URL
  const bookList = ref([])
  const swiperRef = ref(null)

  const onSwiper = (instance) => {
    swiperRef.value = instance
  }

  onMounted(() => {
    axios({
      method: 'get',
      url: `${API_URL}/api/v1/books/`,
      params: {
        page: 1,
        page_size: 10,
        'sort-direction': 'asc',
        'sort-field': 'id',
      },
    })
      .then(res => {
        bookList.value = res.data.results ?? []
        nextTick(() => {
          if (!swiperRef.value) return
          swiperRef.value.update()
          if (swiperRef.value.autoplay) {
            swiperRef.value.autoplay.start()
          }
        })
      })
      .catch(err => {
        errorStore.handleRequestError(err)
      })
  })
  
</script>

<template>
  <section class="main-book main-section">
    <div class="tit-wrap">
      <h1 class="page-title fadeinup80" :ref="collect">베스트 셀러</h1>
      <div class="btn-swiper fadeinleft80" :ref="collect">
        <button class="btn-prev"><img src="@/assets/images/common/icon_arrow_left.png" alt="이전 버튼"></button>
        <button class="btn-next"><img src="@/assets/images/common/icon_arrow_left.png" alt="다음 버튼"></button>
      </div>
    </div>

    <div class="fadein" :ref="collect">
      <Swiper 
        v-if="bookList.length"
        @swiper="onSwiper"
        class="book-list"
        :modules="[Autoplay, Navigation]"
        :slides-per-view="6"
        :space-between="0"
        :loop="true"
        :autoplay="{ delay: 2000, disableOnInteraction: false }"
        :navigation="{
          nextEl: '.btn-next',
          prevEl: '.btn-prev',
        }"
        :observer="true"
        :observe-parents="true"
      >
        <SwiperSlide 
          v-for="book in bookList"
          :key="book.id"
          class="book"
        >
          <div class="thumbnail">
            <img v-if="book.thumbnail" :src="book.thumbnail" :alt="book.title">
            <img v-else src="@/assets/images/no_img_bookcover.jpg" alt="no-image">
          </div>
          <div class="info">
            <h2 class="title f-pre">{{ book.title }}</h2>
            <p class="author f-pre">{{ book.author }}</p>
          </div>
        </SwiperSlide>
      </Swiper>
    </div>
  </section>
</template>

<style scoped>
.tit-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
}

.page-title {
  margin-bottom: 0;
}

.swiper-slide {
  padding: 0 15px;
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

.book {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.thumbnail {
  width: 11vw;
  height: 16vw;
  border-radius: 20px 60px 20px 60px;
  overflow: hidden;
  border: 1px solid #ddd;
}

.thumbnail img {
  width:100%;
  height: 100%;
  object-fit: cover;
}

.info {
  word-break: break-all;
  line-height: 1.2;
}

.info .title {
  font-size: 22px;
  font-weight: 600;
  margin: 20px 0 10px;
}

.info .author {
  font-size: 18px;
  color: #555;
}

.fadein.show {
  animation-delay: .3s;
}

</style>
