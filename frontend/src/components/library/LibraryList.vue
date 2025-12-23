<script setup>
  import { onMounted, computed } from 'vue'
  import { useRoute } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import LibraryBook from '@/components/library/LibraryBook.vue'
  import { useLibraryStore } from '@/stores/libraries'

  const libraryStore = useLibraryStore()
  const { libraryBookList } = storeToRefs(libraryStore)

  const route = useRoute()
  const status = computed(() => route.meta.status)

  onMounted(() => {
    libraryStore.fetchBookList(status)
  })
</script>

<template>
  <ul class="book-list">
    <li
      v-for="book in libraryBookList"
      :key="book.id"
      class="book"
    >
      <LibraryBook :book="book" />
    </li>
  </ul>
</template>

<style scoped>
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