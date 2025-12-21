<script setup>
  import { useErrorStore } from '@/stores/errors'
  import { storeToRefs } from 'pinia'

  const errorStore = useErrorStore()
  const { isErrorModalOpen, errorMessage } = storeToRefs(errorStore)
  const { closeErrorModal } = errorStore

</script>

<template>
  <!-- 모달 열려 있을 때만 렌더링 -->
  <div v-if="isErrorModalOpen" class="modal-bg">
    <div class="modal">
      <div class="modal-header">
        <h2 class="title">이용 안내</h2>
        <button class="btn-close" @click="closeErrorModal">
          <img src="@/assets/images/common/btn_close.png" alt="닫기 버튼">
        </button>
      </div>

      <p class="message">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<style scoped>
  .message {
    font-size: 20px;
    line-height: 1.25;
    color: #555;
    min-height: 100px;
  }
</style>
