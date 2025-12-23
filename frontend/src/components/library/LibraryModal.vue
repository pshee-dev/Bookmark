<script setup>
  import { computed, reactive, watch } from 'vue'
  import { storeToRefs } from 'pinia'
  import { useLibraryStore } from '@/stores/libraries'

  const libraryStore = useLibraryStore()
  const { isLibraryModalOpen, libraryMode, modalBook, modalInitialValue } = storeToRefs(libraryStore)
  const { closeLibraryModal, submitLibrary } = libraryStore

  const defaultForm = {
    status: 'reading',
    start_date: '',
    finish_date: '',
    rating: 0,
    current_page: 0,
  }

  const formState = reactive({ ...defaultForm })

  const modalTitle = computed(() => libraryMode.value === 'update' ? '서재 정보 수정' : '서재에 담기')
  const submitLabel = computed(() => libraryMode.value === 'update' ? '수정' : '저장')

  const resetForm = (value = modalInitialValue.value) => {
    formState.status = value?.status ?? defaultForm.status
    formState.start_date = value?.start_date ?? defaultForm.start_date
    formState.finish_date = value?.finish_date ?? defaultForm.finish_date
    formState.rating = value?.rating ?? defaultForm.rating
    formState.current_page = value?.current_page ?? defaultForm.current_page
  }

  watch(() => modalInitialValue.value, (val) => resetForm(val), { deep: true, immediate: true })
  watch(() => libraryMode.value, () => resetForm(), { immediate: false })
  watch(() => isLibraryModalOpen.value, (isOpen) => {
    if (isOpen) {
      resetForm()
    }
  })

  const closeModal = () => {
    closeLibraryModal()
  }

  const formatPayload = () => ({
    status: formState.status,
    start_date: formState.start_date || null,
    finish_date: formState.finish_date || null,
    rating: formState.rating === '' ? null : Number(formState.rating),
    current_page: formState.current_page === '' ? null : Number(formState.current_page),
  })

  const submit = () => {
    submitLibrary(formatPayload())
  }
</script>

<template>
  <div v-if="isLibraryModalOpen" class="modal-bg" @click.self="closeModal">
    <div class="modal library-modal">
      <div class="modal-header">
        <h2 class="title">{{ modalTitle }}</h2>
        <button class="btn-close" type="button" @click="closeModal">
          <img src="@/assets/images/common/btn_close.png" alt="닫기 버튼">
        </button>
      </div>

      <div class="book-summary" v-if="modalBook?.title">
        <p class="book-title">{{ modalBook.title }}</p>
        <p class="book-meta">
          <span v-if="modalBook.author">{{ modalBook.author }}</span>
          <span v-if="modalBook.author && modalBook.publisher" class="divider"> | </span>
          <span v-if="modalBook.publisher">{{ modalBook.publisher }}</span> <br>
        </p>
      </div>

      <form class="form" @submit.prevent="submit">
        <select id="status" v-model="formState.status">
          <option value="reading">읽고 있는 책</option>
          <option value="want">읽고 싶은 책</option>
          <option value="finished">다 읽은 책</option>
        </select>

        <label class="form-label" for="start_date">독서 시작일</label>
        <input id="start_date" v-model="formState.start_date" type="date">

        <label class="form-label" for="finish_date">독서 완료일</label>
        <input id="finish_date" v-model="formState.finish_date" type="date">

        <label class="form-label" for="current_page">읽고 있는 페이지</label>
        <input
          id="current_page"
          v-model.number="formState.current_page"
          type="number"
          min="0"
          step="1"
        >

        <label class="form-label" for="rating">평점</label>
        <input
          id="rating"
          v-model.number="formState.rating"
          type="number"
          min="0"
          max="5"
          step="1"
        >

        <button class="btn-submit" type="submit">{{ submitLabel }}</button>
      </form>
    </div>
  </div>
</template>

<style scoped>
  .modal-header {
    margin-bottom: 20px;
  }

  .book-summary {
    border: 1px solid #eee;
    border-radius: 12px;
    padding: 20px 15px;
    margin-bottom: 25px;
    background: #fafafa;
  }

  .book-title {
    font-weight: 600;
    font-size: 18px;
    margin-bottom: 10px;
  }

  .book-meta {
    color: #777;
    font-size: 14px;
    margin: 0;
  }

  .divider {
    margin: 0 6px;
  }

  input,
  select {
    width: 100%;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #ddd;
    color: #333;
    font-size: 16px;
    font-family: 'Pretendard', sans-serif;
  }

  .btn-submit {
    margin-top: 50px;
  }
</style>
