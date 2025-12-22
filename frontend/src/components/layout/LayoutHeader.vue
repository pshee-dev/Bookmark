<script setup>
  import { computed, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAccountStore } from '@/stores/accounts'
  import { useBookStore } from '@/stores/books'
  import { storeToRefs } from 'pinia'

  const router = useRouter()

  const accountStore =  useAccountStore()
  const { isLogin, user } = storeToRefs(accountStore)

  const bookStore = useBookStore()
  const { searchType, searchKeyword } = storeToRefs(bookStore)

  const localKeyword = ref(null)

  // 전체 검색 옵션
  const searchOptions = [
    { value: 'title', label: '제목 검색'},
    { value: 'author', label: '작가 검색'},
  ]

  // 검색 옵션 열림 여부
  const isSelectOpen = ref(false) 
  
  // 검색 옵션 선택
  const selectType = (option) => {
    searchType.value = option.value
    isSelectOpen.value = false
  }

  // 선택된 옵션 라벨
  const selectedLabel = computed(() => {
    return searchOptions.find(option => option.value === searchType.value).label
  })
  
  // 검색
  const search = () => {
    searchKeyword.value = localKeyword.value
    localKeyword.value = ''
    bookStore.search()
  }
</script>

<template>
  <header>
    <nav>
      <!-- 로고 -->
      <RouterLink :to="{name: 'main'}"><img class="logo" src="@/assets/images/common/logo.png" alt="책갈피 로고"></RouterLink>

      <!-- 검색 폼 -->
      <form class="form-search" @submit.prevent="search">

        <div class="select-box" @click="isSelectOpen = !isSelectOpen">
          <span>{{ selectedLabel }}</span>
          <img
            src="@/assets/images/common/icon_arrow_down.png"
            alt="화살표"
            class="icon-arrow"
            :class="{ open: isSelectOpen }"
          />

          <ul v-if="isSelectOpen" class="select-list">
            <li 
              v-for="option in searchOptions"
              :key="option.value"
              @click.stop="selectType(option)"
            >
              {{ option.label }}
            </li>
          </ul>
        </div>

        <input 
          v-model="localKeyword" 
          class="input-search" 
          type="text"
          placeholder="검색어를 입력하세요."
        >

        <button class="btn-search" type="submit">
          <img src="@/assets/images/common/icon_search.png" alt="검색 아이콘">
        </button>
      </form>

      <!-- 메뉴 -->
      <div v-if="isLogin && user" class="menu-list">
        <RouterLink :to="{name: 'libraries', params: {username: user.username}}">서재</RouterLink>
        <RouterLink :to="{name: 'feed'}">피드</RouterLink>
        <RouterLink :to="{name: 'user', params: {username: user.username}}">마이페이지</RouterLink>
      </div>
      <div v-if="!isLogin" class="menu-list">
        <RouterLink :to="{name: 'login'}">로그인</RouterLink>
        <RouterLink :to="{name: 'signup'}">회원가입</RouterLink>
      </div>
      
    </nav>
  </header>
</template>

<style scoped>
  /* ===== Header ===== */
  header {
    padding: 0 50px;
    background-color: #fff;
    position: fixed;
    top: 0;
    width: 100vw;
    z-index: 9999;
  }

  nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100px;
  }

  /* ===== Logo ===== */
  .logo {
    height: 45px;
  }
  
  /* ===== Search ===== */
  .form-search {
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    border: 1px solid #ddd;
    padding: 5px 10px;
  }

  /* Select */
  .select-box {
    position: relative;
    display: flex;
    align-items: center;
    gap: 20px;
    border-radius: 999px;
    background-color: #fff;
    font-size: 16px;
    cursor: pointer;
    user-select: none;
    padding: 0 20px 0 15px;
    margin-right: 20px;
  }

  .select-box::before {
    position:absolute;
    top: 50%;
    right: 0;
    transform: translateY(-50%);
    display: block;
    content: '';
    width: 1px;
    height: 20px;
    background-color: #ddd;
  }

  .icon-arrow {
    width: 24px;
    transition: transform 0.2s ease;
  }

  .icon-arrow.open {
    transform: rotate(180deg);
  }

  .select-list {
    position: absolute;
    top: calc(100% + 23px);
    left: 50%;
    transform: translateX(-50%);
    width: calc(100% + 20px);
    padding: 5px;
    background-color: #fff;
    border-radius: 20px;
    border: 1px solid #ddd;
    overflow: hidden;
    z-index: 10;
  }

  .select-list li {
    padding: 15px;
    border-radius: 15px;
    font-size: 14px;
    cursor: pointer;
    color: #767676;
  }

  .select-list li:hover {
    background-color: #EBEFFF;
    color: #333;
  }

  /* Input */
  .input-search {
    min-width: 600px;
    border: none;
    background-color: transparent;
    font-size: 16px;
    outline: none;
  }

  /* Button */
  .btn-search {
    border: none;
    background-color: transparent;
    cursor: pointer;
  }
  
  /* ===== Menu ===== */
  .menu-list {
    display: flex;
    gap: 30px;
  }

  .menu-list a {
    font-size: 18px;
    color: #333;
  }
</style>