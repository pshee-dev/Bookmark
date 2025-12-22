import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { defineStore, storeToRefs } from 'pinia'
import { useErrorStore } from '@/stores/errors'
import axios from 'axios'

export const useBookStore = defineStore('book', () => {
  const router = useRouter()
  
  const errorStore = useErrorStore()
  const { errorStatus } = storeToRefs(errorStore)
  const API_URL = import.meta.env.VITE_API_URL

  const searchType = ref('title')
  const searchKeyword = ref(null)

  const searchBookList = ref([])

  const search = () => {
    axios({
      method: 'get',
      url: `${API_URL}/books/search/`,
      params: {
        keyword: searchKeyword.value,
        field: searchType.value,
        page_size: 10,
        page: 1,
      },
    })
      .then(res => {
        console.log(res.data)
        searchBookList.value = res.data.results
        router.push({name: 'search'})
      })
      .catch(err => {
        if (err.response && err.response.status === 400) {
          errorStatus.value = err.response.data.error.code
          errorStore.openErrorModal(err.response.data.error.message)
        }
        console.log(err)
      })
  }

  return {
    searchType,
    searchKeyword,
    searchBookList,
    search,
  }
})