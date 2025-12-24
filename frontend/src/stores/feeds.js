import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { defineStore, storeToRefs } from 'pinia'
import { useErrorStore } from '@/stores/errors'
import { useAccountStore } from '@/stores/accounts'
import axios from 'axios'

export const useFeedStore = defineStore('feed', () => {
  const router = useRouter()
  const errorStore = useErrorStore()
  const accountStore = useAccountStore()
  const { user, token } = storeToRefs(accountStore)
  
  const API_URL = import.meta.env.VITE_API_URL
  
  const galfyList = ref([])
  const galfyCount = ref(0)

  const reviewList = ref([])
  const reviewCount = ref(0)
  
  const isLoading = ref(false)

  const sordDirection = 'desc'
  const sortField = 'created_at'
  const pageSize = 10

  const fetchGalfies = async (bookId, { mine = false } = {}) => {
    isLoading.value = true
    try {
      const authHeaders = token.value
        ? { headers: { Authorization: `Token ${token.value}` } }
        : {}
      const res = await axios.get(
        `${API_URL}/books/${bookId}/galfies/`, 
        {                                                                                            
          params: {                                                                                  
            'sort-direction': sordDirection,                                                         
            'sort-field': sortField,                                                                 
            page_size: pageSize,                                                                     
            ...(mine ? { mine: true } : {}),                                                         
          },                                                                                         
          ...(mine ? { headers: { Authorization: `Token ${token.value}` } } : authHeaders),                   
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

  const fetchReviews = async (bookId, { mine = false } = {}) => {
    isLoading.value = true
    try {
      const authHeaders = token.value
        ? { headers: { Authorization: `Token ${token.value}` } }
        : {}
      const res = await axios.get(
        `${API_URL}/books/${bookId}/reviews/`,
        {
          params: {
            'sort-direction': sordDirection,
            'sort-field': sortField,
            page_size: pageSize,
            ...(mine ? { mine: true } : {}),
          },
          ...(mine ? { headers: { Authorization: `Token ${token.value}` } } : authHeaders),
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

  const createGalfy = async (bookId, payload) => {
    if (!bookId) return null
    isLoading.value = true
    try {
      const res = await axios.post(
        `${API_URL}/books/${bookId}/galfies/`,
        payload,
        {
          headers: {
            Authorization: `Token ${token.value}`
          }
        }
      )
      galfyList.value = [res.data, ...galfyList.value]
      galfyCount.value += 1
      router.back()
      return res.data
    } catch (err) {
      errorStore.handleRequestError(err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const updateGalfy = async (galfyId, payload) => {
    if (!galfyId) return null
    isLoading.value = true
    try {
      const res = await axios.patch(
        `${API_URL}/galfies/${galfyId}/`,
        payload,
        {
          headers: {
            Authorization: `Token ${token.value}`
          }
        }
      )
      const target = galfyList.value.find((item) => item.id === galfyId)
      if (target) {
        Object.assign(target, res.data)
      }
      router.back()
      return res.data
    } catch (err) {
      errorStore.handleRequestError(err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const createReview = async (bookId, payload) => {
    if (!bookId) return null
    isLoading.value = true
    try {
      const res = await axios.post(
        `${API_URL}/books/${bookId}/reviews/`,
        payload,
        {
          headers: {
            Authorization: `Token ${token.value}`
          }
        }
      )
      reviewList.value = [res.data, ...reviewList.value]
      reviewCount.value += 1
      router.back()
      return res.data
    } catch (err) {
      errorStore.handleRequestError(err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const updateReview = async (reviewId, payload) => {
    if (!reviewId) return null
    isLoading.value = true
    try {
      const res = await axios.patch(
        `${API_URL}/reviews/${reviewId}/`,
        payload,
        {
          headers: {
            Authorization: `Token ${token.value}`
          }
        }
      )
      const target = reviewList.value.find((item) => item.id === reviewId)
      if (target) {
        Object.assign(target, res.data)
      }
      router.back()
      return res.data
    } catch (err) {
      errorStore.handleRequestError(err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const updateFeedLike = (feedType, feedId, likeCount, isLiked) => {
    const targetList = feedType === 'review' ? reviewList.value : galfyList.value
    const target = targetList.find((item) => item.id === feedId)
    if (!target) return
    target.likes_count = likeCount
    target.is_liked = isLiked
  }

  const actionLikes = async (feedType, feedId) => {
    isLoading.value = true
    try {
      const res = await axios.post(
        `${API_URL}/likes/`,
        {
          target_type: feedType,
          target_id: feedId,
        },
        {
          headers: {
            Authorization: `Token ${token.value}`
          }
        }
      )
      updateFeedLike(feedType, feedId, res.data.like_count, res.data.is_liked)
      return res.data
    } catch (err) {
      errorStore.handleRequestError(err)
      return null
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
    createGalfy,
    updateGalfy,
    createReview,
    updateReview,
    actionLikes,
  }
})
