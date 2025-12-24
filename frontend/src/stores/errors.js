import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export const useErrorStore = defineStore('error', () => {
  const router = useRouter()

  const isErrorModalOpen = ref(false) // 에러 모달 열림 여부
  const errorMessage = ref('') // 에러 메시지
  const errorStatus = ref('') // 현재 에러 상태

  // 공통 에러 핸들러
  const handleRequestError = (err) => {
    if (err.status !== 400) return
    const data = err.response?.data ?? null
    const message = ref('요청을 처리하지 못했습니다.')

    if (data?.error) {
      message.value = data.error.message
      errorStatus.value = data.error.code
    } else if (data && typeof data === 'object') {
      const entries = Object.entries(data)
      const [key, value] = entries[0] ?? []
      errorStatus.value = key

      if (Array.isArray(value)) {
        message.value = value[0]   // 첫 번째 에러 메시지
      } else if (value) {
        message.value = value
      }
    }
    openErrorModal(message.value)
    console.error(err)
  }

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
    handleRequestError,
  }
})