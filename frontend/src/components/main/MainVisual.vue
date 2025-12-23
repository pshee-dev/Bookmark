<script setup>
  import { useRouter } from 'vue-router'
  import { computed } from 'vue'
  import { storeToRefs } from 'pinia'
  import { useAccountStore } from '@/stores/accounts'

  import { Swiper, SwiperSlide } from 'swiper/vue'
  import { Autoplay, EffectFade } from 'swiper/modules'
  import 'swiper/css'
  import 'swiper/css/effect-fade'

  import { useScrollReveal } from '@/composables/scrollReveal'
  const { collect } = useScrollReveal()
  
  const router = useRouter()

  const accountStore = useAccountStore()
  const { isLogin, user } = storeToRefs(accountStore)

  const goLogin = () => {
    router.push({name: 'login'})
  }
  const goLibrary = () => {
    if (!user.value?.username) return
    router.push({name: 'libraries', params: {username: user.value.username}})
  }
</script>

<template>
  <section class="main-visual">
    <div class="txt-wrap fadeinup80" :ref="collect">
      <h2 class="sub-title">책은 덮어도 이야기는 남도록, <br>나만의 독서 흔적이 쌓이는 곳</h2>
      <h1 class="title">책갈피</h1>

      <template v-if="!isLogin">
        <p class="txt f-pre">아직 로그인 하지 않았어요. <br><b class="f-pre">로그인</b>하고 나만의 독서 기록을 시작해보세요.</p>
        <button @click.stop="goLogin" class="btn">로그인</button>
      </template>
      <template v-else>
        <p class="txt f-pre"><b class="f-pre">{{ user?.name ? user?.name : '회원' }}</b>님, 안녕하세요 :&#41; <br>천천히 읽고 가볍게 기록하여 독서 습관을 길러보세요.</p>
        <button @click.stop="goLibrary" class="btn">내 서재 바로가기</button>
      </template>
    </div>

    <Swiper 
      class="img-wrap"
      :modules="[Autoplay, EffectFade]"
      :loop="true"
      :autoplay="{ delay: 2500, disableOnInteraction: false }"
      effect="fade"
      :fade-effect="{ crossFade: true }"
    >
      <SwiperSlide><img src="@/assets/images/mainvisual1.jpg" alt="메인 이미지"></SwiperSlide>
      <SwiperSlide><img src="@/assets/images/mainvisual2.jpg" alt="메인 이미지"></SwiperSlide>
    </Swiper>
  </section>
</template>

<style scoped>
.main-visual {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 80px;
  line-height: 1.25;
}

.txt-wrap {
  padding-left: 200px;
}

.sub-title {
  font-size: 50px;
}

.title {
  font-size: 80px;
  font-weight: 800;
  margin: 30px 0 80px;
}

.txt {
  font-size: 24px;
  margin-bottom: 35px;
  line-height: 1.5;
}

.txt b {
  font-weight: 600;
}

.btn {
  
}

.img-wrap {
  width: 50%;
  height: 840px;
  border-radius: 50px 0 0 180px;
  overflow: hidden;
  margin: 0;
}

.img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.swiper-wrapper {
  z-index: 0;
}

.swiper-slide img {
  transform: scale(1.1);
  transition: all ease 2.5s;
}

.swiper-slide-active img {
  transform: scale(1);
}
</style>