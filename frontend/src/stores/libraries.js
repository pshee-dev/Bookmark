import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { defineStore, storeToRefs } from 'pinia'
import { useErrorStore } from '@/stores/errors'
import { useAccountStore } from '@/stores/accounts'
import axios from 'axios'

export const useLibraryStore = defineStore('library', () => {
  const accountStore = useAccountStore()
  const { token, user } = storeToRefs(accountStore)

  const API_URL = import.meta.env.VITE_API_URL

  const libraryBookList = ref([])

  const sortDirection = 'desc'
  const sortType = 'created_at'
  const page = 20
  
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
        console.log(err)
      })
  }

  const createLibrary = () => {

  }

  const updateLibrary = () => {

  }

  return {
    libraryBookList,
    fetchBookList,
    createLibrary,
    updateLibrary,
  }
})