import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { defineStore, storeToRefs } from 'pinia'
import { useErrorStore } from '@/stores/errors'
import { useAccountStore } from '@/stores/accounts'
import axios from 'axios'

export const useLibraryStore = defineStore('library', () => {
  const router = useRouter()

  const accountStore = useAccountStore()
  const { token, user } = storeToRefs(accountStore)
  const errorStore = useErrorStore()

  const API_URL = import.meta.env.VITE_API_URL

  const libraryBookList = ref([])
  const sortDirection = 'desc'
  const sortType = 'created_at'
  const page = 20

  const isLoading = ref(false)
  const libraryBook = ref({})

  const isLibraryModalOpen = ref(false)
  const libraryMode = ref('create')
  const modalBook = ref(null)
  const modalBookId = ref(null)
  const modalLibraryId = ref(null)
  const modalInitialValue = ref(null)

  const fetchBookList = (status) => {
    axios({
      method: 'get',
      url: `${API_URL}/libraries/`,
      params: {
        status: status,
        'sort-direction': sortDirection,
        'sort-type': sortType,
        page: page,
      },
      headers: {
        Authorization: `Token ${token.value}`
      },
    })
      .then(res => {
        console.log(res.data)
        libraryBookList.value = res.data.results
      })
      .catch(err => {
        errorStore.handleRequestError(err)
      })
  }

  const createLibrary = async (bookId, payload) => {
    isLoading.value = true
    try {
      const res = await axios.post(
        `${API_URL}/libraries/`,
        {
          ...payload,
          book: bookId,
        },
        {
          headers: {
            Authorization: `Token ${token.value}`
          }
        },
      )
      libraryBook.value = res.data
      router.push({ name: 'reading', params: { username: user.value.username, libraryId: res.data.id } })
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  const updateLibrary = async (libraryId, bookId, payload) => {
    isLoading.value = true
    try {
      const res = await axios.patch(
        `${API_URL}/libraries/${libraryId}/`,
        payload,
        {
          headers: {
            Authorization: `Token ${token.value}`
          },
        }
      )
      libraryBook.value = res.data
      router.push({ name: 'reading', params: { username: user.value.username, libraryId: res.data.id } })
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  const deleteLibrary = async (libraryId) => {
    isLoading.value = true
    try {
      await axios.delete(
        `${API_URL}/libraries/${libraryId}/`,
        {
          headers: {
            Authorization: `Token ${token.value}`
          },
        }
      )
      router.push({ name: 'reading', params: { username: user.value.username } })
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  const openLibraryModal = ({ mode = 'create', book = null, bookId = null, libraryId = null, initialValue = null } = {}) => {
    libraryMode.value = mode === 'update' ? 'update' : 'create'
    modalBook.value = book
    modalBookId.value = bookId
    modalLibraryId.value = libraryId
    modalInitialValue.value = initialValue
    isLibraryModalOpen.value = true
  }

  const closeLibraryModal = () => {
    isLibraryModalOpen.value = false
  }

  const submitLibrary = async (formValue) => {
    try {
      if (libraryMode.value === 'update') {
        await updateLibrary(modalLibraryId.value, modalBookId.value, formValue)
      } else {
        await createLibrary(modalBookId.value, formValue)
      }
      closeLibraryModal()
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }

  return {
    isLoading,
    libraryBook,
    libraryBookList,
    fetchBookList,
    createLibrary,
    updateLibrary,
    deleteLibrary,
    isLibraryModalOpen,
    libraryMode,
    modalBook,
    modalBookId,
    modalLibraryId,
    modalInitialValue,
    openLibraryModal,
    closeLibraryModal,
    submitLibrary,
  }
})
