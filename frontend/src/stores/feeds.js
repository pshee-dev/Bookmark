import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { defineStore, storeToRefs } from 'pinia'
import { useErrorStore } from '@/stores/errors'
import axios from 'axios'

export const useFeedStore = defineStore('feed', () => {
  const API_URL = import.meta.env.VITE_API_URL
  
  const galfyList = ref([])
  const galfyCount = ref(0)

  const reviewList = ref([])
  const reviewCount = ref(0)
  
  const isLoading = ref(false)

  const sordDirection = 'desc'
  const sortField = 'created_at'
  const pageSize = 10

  const fetchGalfies = async (bookId) => {
    isLoading.value = true
    try {
      const res = await axios.get(
        `${API_URL}/books/${bookId}/galfies/`, {
          params: {
            'sort-direction' : sordDirection,
            'sort-field' : sortField,
            page_size : pageSize,
          }
        }
      )
      galfyList.value = res.data.results
      galfyCount.value = res.data.count
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  const fetchReviews = async (bookId) => {
    isLoading.value = true
    try {
      const res = await axios.get(
        `${API_URL}/books/${bookId}/reviews/`, {
          params: {
            'sort-direction' : sordDirection,
            'sort-field' : sortField,
            page_size : pageSize,
          }
        }
      )
      reviewList.value = res.data.results
      reviewCount.value = res.data.count
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading,
    galfyList,
    reviewList,
    galfyCount,
    reviewCount,
    fetchGalfies,
    fetchReviews,
  }
})