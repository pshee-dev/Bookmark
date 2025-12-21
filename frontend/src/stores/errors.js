import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export const useErrorStore = defineStore('error', () => {
  const router = useRouter()

  const isErrorModalOpen = ref(false) // 에러 모달 열림 여부
  const errorMessage = ref('') // 에러 메시지
  const errorStatus = ref('') // 현재 에러 상태

  // 에러 모달 열기
  const openErrorModal = (message) => {
    isErrorModalOpen.value = true
    errorMessage.value = message
  }

  // 에러 모달 닫기
  const closeErrorModal = () => {
    if (errorStatus.value === 'requiresAuth') {
      router.push({name: 'login'})
    } else if (errorStatus.value === 'ownerOnly' || errorStatus.value === 'guestOnly') {
      window.history.back()
    }
    isErrorModalOpen.value = false
    errorMessage.value = ''
    errorStatus.value = ''
  }

  return {
    isErrorModalOpen,
    errorMessage,
    errorStatus,
    openErrorModal,
    closeErrorModal,
  }
})