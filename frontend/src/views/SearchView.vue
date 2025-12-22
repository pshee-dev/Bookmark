<script setup>
  import { computed } from 'vue'
  import { useBookStore } from '@/stores/books'
  import { storeToRefs } from 'pinia'
  import SearchBook from '@/components/SearchBook.vue'

  const bookStore = useBookStore()
  const { searchBookList, searchType, searchKeyword, isLoading } = storeToRefs(bookStore)


</script>

<template>
  <div class="bg-container">
    <h1 class="page-title">'{{ searchKeyword }}'에 대한 검색 결과</h1>
    <div class="container-box">
      <ul class="book-list">
        <li
          v-for="book in searchBookList"
          :key="book.id"
          class="book"
        >
          <SearchBook :book="book" />
        </li>
      </ul>
      <div v-if="isLoading">
        로딩 중...
      </div>
    </div>
  </div>
</template>

<style scoped>
.container-box {
  min-height: 500px;
}

.book-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  align-items: flex-start;
  gap: 100px 0;
}

.book-list .book {
  width: 50%;
  display: flex;
}
</style>