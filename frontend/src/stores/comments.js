import { ref, computed } from 'vue'
import { defineStore, storeToRefs } from 'pinia'
import axios from 'axios'
import { useAccountStore } from '@/stores/accounts'
import { useErrorStore } from '@/stores/errors'
import { useFeedStore } from '@/stores/feeds'

export const useCommentStore = defineStore('comment', () => {
  const accountStore = useAccountStore()
  const { token } = storeToRefs(accountStore)
  const errorStore = useErrorStore()
  const feedStore = useFeedStore()

  const API_URL = import.meta.env.VITE_API_URL

  const isOpen = ref(false)
  const isLoading = ref(false)
  const targetType = ref(null)
  const targetId = ref(null)
  const comments = ref([])
  const draft = ref('')

  const isReady = computed(() => !!targetType.value && !!targetId.value)

  const buildUrl = () => {
    const prefix = targetType.value === 'review' ? 'reviews' : 'galfies'
    return `${API_URL}/api/v1/${prefix}/${targetId.value}/comments/`
  }

  const openComments = async ({ type, id }) => {
    targetType.value = type
    targetId.value = id
    isOpen.value = true
    await fetchComments()
  }

  const closeComments = () => {
    isOpen.value = false
    comments.value = []
    draft.value = ''
    targetType.value = null
    targetId.value = null
  }

  const fetchComments = async () => {
    if (!isReady.value) return
    isLoading.value = true
    try {
      const res = await axios.get(buildUrl(), {
        params: {
          'sort-direction': 'desc',
          'sort-field': 'created_at',
        },
      })
      comments.value = res.data?.results ?? res.data ?? []
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  const submitComment = async () => {
    if (!isReady.value) return
    const content = draft.value.trim()
    if (!content) return
    isLoading.value = true
    try {
      const res = await axios.post(
        buildUrl(),
        { content },
        {
          headers: {
            Authorization: `Token ${token.value}`,
          }
        }
      )
      comments.value = [res.data, ...comments.value]
      const nextCount = (comments.value?.length ?? 0)
      feedStore.updateFeedCommentsCount(targetType.value, targetId.value, nextCount)
      draft.value = ''
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  const deleteComment = async (commentId) => {
    if (!commentId || !token.value) return
    isLoading.value = true
    try {
      await axios.delete(
        `${API_URL}/api/v1/comments/${commentId}/`,
        {
          headers: {
            Authorization: `Token ${token.value}`,
          }
        }
      )
      comments.value = comments.value.filter((item) => item.id !== commentId)
      const nextCount = comments.value.length
      feedStore.updateFeedCommentsCount(targetType.value, targetId.value, nextCount)
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  return {
    isOpen,
    isLoading,
    targetType,
    targetId,
    comments,
    draft,
    openComments,
    closeComments,
    fetchComments,
    submitComment,
    deleteComment,
  }
})
