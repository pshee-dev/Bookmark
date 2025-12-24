<script setup>
  import { ref, watch } from 'vue'
  import { storeToRefs } from 'pinia'
  import { useScrollReveal } from '@/composables/scrollReveal'
  import { useLibraryStore } from '@/stores/libraries'
  import { useAccountStore } from '@/stores/accounts'
  import LibraryBook from '@/components/library/LibraryBook.vue'
  import Loading from '../Loading.vue'

  const { collect } = useScrollReveal()

  const libraryStore = useLibraryStore()
  const { libraryBookList, isLoading } = storeToRefs(libraryStore)

  const accountStore = useAccountStore()
  const { isLogin } = storeToRefs(accountStore)

  const tabs = [
    { value: 'reading', label: '읽고 있는 책' },
    { value: 'want', label: '읽고 싶은 책' },
    { value: 'finished', label: '다 읽은 책' },
  ]

  const activeStatus = ref(tabs[0].value)

  watch(
    activeStatus,
    (nextStatus) => {
      if (nextStatus) {
        libraryStore.fetchBookList(nextStatus)
      }
    },
    { immediate: true }
  )

  const setStatus = (nextStatus) => {
    if (activeStatus.value === nextStatus) return
    activeStatus.value = nextStatus
  }
</script>

<template>
  <section class="main-library main-section">
    <h1 class="page-title fadeinup80" :ref="collect">내 서재</h1>
    
    <div class="container-box">
      <ul class="tab-menu">
        <li v-for="tab in tabs" :key="tab.value">
          <a
            href="#"
            class="tab-link"
            :class="{ 'router-link-active': activeStatus === tab.value }"
            @click.prevent="setStatus(tab.value)"
          >
            {{ tab.label }}
          </a>
        </li>
      </ul>

      <div v-if="!isLogin" class="no-content">로그인 후 이용 가능한 서비스입니다.</div>
      <div v-else-if="isLoading && libraryBookList.length === 0" class="no-content"><Loading /></div>
      <div v-else-if="libraryBookList.length === 0" class="no-content">서재에 책을 등록해주세요.</div>
      <ul v-else class="book-list fadeinup80" :ref="collect">
        <li
          v-for="item in libraryBookList"
          :key="item.id"
          class="book"
        >
          <LibraryBook :item="item" />
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
  .container-box {
    padding: 40px 50px 50px;
  }

  .tab-menu {
    margin-bottom: 50px;
    display: flex;
    gap: 30px;
    border: none;
  }

  .tab-menu li {
    flex: initial;
  }

  .tab-menu li a {
    font-size: 20px;
    padding: 12px 0;
  }

  .tab-menu li a.router-link-active::after {
    height: 2px;
  }

  .tab-link {
    text-decoration: none;
    background: transparent;
    border: none;
  }

  .book-list {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    align-items: flex-start;
    padding: 0 20px;
    gap: 100px 0;
  }

  .book-list .book {
    width: 50%;
    display: flex;
  }
</style>
