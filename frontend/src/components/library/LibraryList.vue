<script setup>
  import { computed, watch, nextTick } from 'vue'
  import { useRoute } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import LibraryBook from '@/components/library/LibraryBook.vue'
  import { useLibraryStore } from '@/stores/libraries'
  import { useScrollReveal } from '@/composables/scrollReveal'
  const { collect, refresh } = useScrollReveal()

  const libraryStore = useLibraryStore()
  const { libraryBookList, hasMore, isLoading } = storeToRefs(libraryStore)

  const route = useRoute()
  const status = computed(() => route.meta.status)

  // meta.status가 바뀔 때마다 fetcBookList 변경
  watch(
    () => route.meta.status,
    (nextStatus) => {
      if (nextStatus) {
        libraryStore.fetchBookList(nextStatus)
        window.scrollTo({ top: 0, behavior: 'auto' })
      }
    },
    { immediate: true }
  )

  watch(
    () => libraryBookList.value.length,
    async () => {
      await nextTick()
      refresh()
    }
  )

  // 더보기 버튼 클릭 시 append 버전으로 fetchBookList 불러오기
  const more = () => {
    if (!status.value) return
    libraryStore.fetchBookList(status.value, { append: true })
  }
</script>

<template>
  <div v-if="libraryBookList.length === 0" class="no-content">서재에 책을 등록해주세요.</div>
  <template v-else>
    <ul class="book-list">
      <li
        v-for="item in libraryBookList"
        :key="item.id"
        class="book fadeinup80"
        :ref="collect"
      >
        <LibraryBook :item="item" />
      </li>
    </ul>
    <button v-if="hasMore" class="btn-more" type="button" :disabled="isLoading" @click.stop="more">더 보기<img src="@/assets/images/common/icon_arrow_down.png" alt="더보기 버튼"></button>
  </template>
</template>

<style scoped>
  .book-list {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    align-items: flex-start;
    margin-top: 80px;
    padding: 0 20px;
    gap: 100px 0;
  }

  .book-list .book {
    width: 50%;
    display: flex;
  }
</style>




