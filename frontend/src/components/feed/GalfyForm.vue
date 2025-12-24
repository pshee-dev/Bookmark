<script setup>
  import { computed, ref } from 'vue'
  import { storeToRefs } from 'pinia'
  import FeedCreateBookInfo from '@/components/feed/FeedCreateBookInfo.vue'
  import { useFeedStore } from '@/stores/feeds'
  import { useLibraryStore } from '@/stores/libraries'

  const feedStore = useFeedStore()
  const libraryStore = useLibraryStore()
  const { libraryBook } = storeToRefs(libraryStore)

  const pageNumber = ref('')
  const content = ref('')

  const bookId = computed(() => libraryBook.value?.book?.id ?? null)

  const handleCreateGalfy = async () => {
    const trimmedContent = content.value.trim()
    if (!bookId.value || !trimmedContent) return

    const normalizedPage = Number.parseInt(pageNumber.value, 10)
    const payload = {
      page_number: Number.isNaN(normalizedPage) ? null : normalizedPage,
      content: trimmedContent,
    }

    const created = await feedStore.createGalfy(bookId.value, payload)
    if (created) {
      pageNumber.value = ''
      content.value = ''
    }
  }
</script>

<template>
  <form class="form" @submit.prevent="handleCreateGalfy">
    <FeedCreateBookInfo />
    <button class="btn btn-small" type="submit">저장</button>

    <div class="form-row">
      <label class="form-label" for="currentPage">페이지</label>
      <input v-model="pageNumber" type="number" name="currentPage" id="currentPage" class="text-input">
    </div>
    <div class="form-row">
      <label class="form-label" for="content">내용</label>
      <textarea v-model="content" name="content" id="content" class="textarea f-pre"></textarea>
    </div>
  </form>
</template>

<style scoped>
.form {
  position:relative;
}

.form-label {
  width: 100px;
  margin: 13px 0 0;
  font-size: 20px;
}

.btn {
  position: absolute;
  top: 0;
  right: 0;
}

</style>
