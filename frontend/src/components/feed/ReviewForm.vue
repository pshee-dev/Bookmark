<script setup>
  import { computed, ref, watch } from 'vue'
  import { storeToRefs } from 'pinia'
  import FeedCreateBookInfo from '@/components/feed/FeedCreateBookInfo.vue'
  import { useFeedStore } from '@/stores/feeds'
  import { useLibraryStore } from '@/stores/libraries'

  const feedStore = useFeedStore()
  const libraryStore = useLibraryStore()
  const { libraryBook } = storeToRefs(libraryStore)

  const props = defineProps({
    mode: {
      type: String,
      default: 'create',
    },
    initialValue: {
      type: Object,
      default: null,
    },
  })

  const title = ref('')
  const content = ref('')

  const bookId = computed(() => {
    return props.initialValue?.book?.id ?? libraryBook.value?.book?.id ?? null
  })
  const formBook = computed(() => props.initialValue?.book ?? null)

  watch(
    () => props.initialValue,
    (nextValue) => {
      if (!nextValue) return
      title.value = nextValue.title ?? ''
      content.value = nextValue.content ?? ''
    },
    { immediate: true }
  )

  const handleCreateReview = async () => {
    const trimmedTitle = title.value.trim()
    const trimmedContent = content.value.trim()
    if (!bookId.value || !trimmedTitle || !trimmedContent) return

    const payload = {
      title: trimmedTitle,
      content: trimmedContent,
    }

    const created = props.mode === 'update' && props.initialValue?.id
      ? await feedStore.updateReview(props.initialValue.id, payload)
      : await feedStore.createReview(bookId.value, payload)
    if (created) {
      title.value = ''
      content.value = ''
    }
  }
</script>

<template>
  <form class="form" @submit.prevent="handleCreateReview">
    <FeedCreateBookInfo :book="formBook" />
    <button class="btn btn-small" type="submit">저장</button>

    <div class="form-row">
      <label class="form-label" for="title">제목</label>
      <input v-model="title" type="text" name="title" id="title" class="text-input">
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
