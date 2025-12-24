<script setup>
  import { useRouter } from 'vue-router'
  import { useAccountStore } from '@/stores/accounts'
  import { storeToRefs } from 'pinia'

  const router = useRouter()
  const accountStore = useAccountStore()
  const { user } = storeToRefs(accountStore)
  
  const props = defineProps({
    item: Object,
  })

  const goDetail = () => {
    router.push({name: 'library', params: { username: user.username, libraryId: props.item.id}})
  }

</script>

<template>
  <!-- 썸네일 -->
  <div class="thumbnail" @click.stop="goDetail">
    <img
      v-if="item.book.thumbnail"
      :src="item.book.thumbnail"
      :alt="item.book.title"
    />
    <img v-else src="@/assets/images/no_img_bookcover.jpg" alt="no-image">
  </div>

  <!-- 도서 정보 -->
  <div class="info">
    <div class="info-top">
      <h3 class="title">{{ item.book.title }}</h3>
      <p v-if="item.book.author" class="f-pre author">{{ item.book.author }}</p>
      <p v-if="item.book.publisher" class="f-pre publisher">{{ item.book.publisher }}</p>
    </div>
    <div class="info-bottom">
      <ul class="rating">
        <li v-for="n in 5" :key="n">
          <!-- 조건부 렌더링: rating 값에 따라 채워진 별/빈 별을 표시 -->
          <span :class="n <= item.rating ? 'filled' : 'empty'">★</span>
        </li>
      </ul>
      <p v-if="item.start_date" class="f-pre">{{ item.start_date }} ~ <span v-if="item.finish_date" class="f-pre">{{ item.finish_date }}</span></p>
    </div>
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
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .info .title {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 20px;
    line-height: 1.2;
  }

  .info p {
    font-size: 18px;
    margin-top: 12px;
    line-height: 1.2;
    color: #555;
  }

  .rating {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    justify-content: start;
  }

  .rating li {
    margin-right: 3px;
    font-size: 24px;
  }

  .filled {
    color: gold; /* 채워진 별 색상 */
  }

  .empty {
    color: lightgray; /* 빈 별 색상 */
  }
</style>