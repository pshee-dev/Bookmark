<script setup>
  import { computed, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import FeedCreateBookInfo from '@/components/feed/FeedCreateBookInfo.vue'
  import { useFeedStore } from '@/stores/feeds'
  import { useLibraryStore } from '@/stores/libraries'
  import { useAccountStore } from '@/stores/accounts'

  const feedStore = useFeedStore()
  const libraryStore = useLibraryStore()
  const accountStore = useAccountStore()
  const router = useRouter()
  const { libraryBook } = storeToRefs(libraryStore)
  const { user } = storeToRefs(accountStore)

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
  const isRecommendModalOpen = ref(false)
  const createdReviewId = ref(null)

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
    const isUpdate = props.mode === 'update' && props.initialValue?.id
    if ((!isUpdate && !bookId.value) || !trimmedTitle || !trimmedContent) return
    const payload = {
      title: trimmedTitle,
      content: trimmedContent,
    }

    const created = isUpdate
      ? await feedStore.updateReview(props.initialValue.id, payload, { navigate: false })
      : await feedStore.createReview(bookId.value, payload, { navigate: false })
    if (created) {
      title.value = ''
      content.value = ''
      createdReviewId.value = created.id ?? props.initialValue?.id ?? null
      isRecommendModalOpen.value = true
    }
  }

  const closeRecommendModal = () => {
    isRecommendModalOpen.value = false
  }

  const goRecommend = () => {
    if (!createdReviewId.value || !user.value?.username) return
    closeRecommendModal()
    router.push({ name: 'recommend', params: { username: user.value.username, reviewId: createdReviewId.value } })
  }

  const goAfterCreate = () => {
    closeRecommendModal()
    router.back()
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

  <div v-if="isRecommendModalOpen" class="modal-bg" @click.self="closeRecommendModal">
    <div class="modal recommend-modal">
      <div class="modal-header">
        <h2 class="title">다음 읽을 책을 추천받아볼까요?</h2>
      </div>
      <p class="recommend-text">
        방금 작성한 리뷰를 바탕으로<br>
        당신에게 어울리는 다음 책을 골라봤어요.
      </p>
      <div class="recommend-actions">
        <button class="btn btn-submit" type="button" @click="goRecommend">추천 받을래요</button>
        <button class="btn btn-submit btn-ghost" type="button" @click="goAfterCreate">지금은 괜찮아요</button>
      </div>
    </div>
  </div>
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

.recommend-modal {
  width: 520px;
}

.recommend-text {
  font-size: 18px;
  line-height: 1.6;
  color: #333;
  margin: 0 0 30px;
}

.recommend-actions {
  display: flex;
  gap: 12px;
}

.recommend-actions .btn-submit {
  position: relative;
  width: calc(50% -6px);
}

.btn-ghost {
  background-color: #fff;
  border: 1px solid #ddd;
  color: #333;
}

.btn-ghost:hover {
  background-color: #f5f5f5;
}

</style>
