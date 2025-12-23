import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { defineStore, storeToRefs } from 'pinia'
import { useErrorStore } from '@/stores/errors'
import axios from 'axios'

export const useBookStore = defineStore('book', () => {
  const router = useRouter()
  
  const errorStore = useErrorStore()
  const API_URL = import.meta.env.VITE_API_URL

  const searchType = ref('title')
  const searchKeyword = ref(null)

  const searchBookList = ref([])
  const bookDetail = ref({})

  /*
  구글 북스 api 반환 값에 대한 정확도가 떨어지는 이슈가 있음
  더보기 버튼 구현하지 않고 40개 데이터 검색한 결과만 보여주는 것으로 임시 작업
  */
  const pageSize = 40
  const currentPage = ref(1)
  const hasMore = ref(true)
  const isLoading = ref(false)

  // 첫 검색 (리스트 초기화)
  const search = async () => {
    currentPage.value = 1
    hasMore.value = true
    searchBookList.value = []
    router.push({ name: 'search' })
    
    await fetchBooks()
  }

  // 더보기
  // const loadMore = async () => {
  //   if (!hasMore.value || isLoading.value) return
  //   currentPage.value += 1
  //   await fetchBooks()
  // }

  // book 패치
  const fetchBooks = async () => {
    isLoading.value = true
    try {
      const res = await axios.get(`${API_URL}/books/search/`, {
        params: {
          keyword: searchKeyword.value,
          field: searchType.value,
          page_size: pageSize,
          page: currentPage.value,
        },
      })

      const results = res.data.results
      console.log(res.data)

      // if (results.length < pageSize) {
      //   hasMore.value = false // 더 이상 없음
      // }

      searchBookList.value.push(...results)
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  // 상세보기 이동
  const goDetail = async (isbn) => {
    isLoading.value = true
    try {
      // 상세보기 클릭 시 isbn 정보를 통해 book_id 반환
      const res = await axios.post(`${API_URL}/books/resolve/`, {
        isbn: isbn,
      })
      const bookId = res.data.book_id

      // 반환된 bookId를 통해 도서 상세 정보 bookDetail에 할당 후 상세페이지로 이동
      const res2 = await axios.get(`${API_URL}/books/${bookId}/`)
      bookDetail.value = res2.data
      router.push({name: 'bookGalfyList', params: {bookId: bookId}})

    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  // 상세보기 직접 접근 시 (URL 직접 접근 대응)
  const fetchBookDetail = async (bookId) => {
    if (!bookId) return

    // 이미 같은 책이 store에 있으면 재요청 안 함
    if (bookDetail.value.id === Number(bookId)) {
      return
    }

    isLoading.value = true
    try {
      const res = await axios.get(
        `${API_URL}/books/${bookId}/`
      )
      bookDetail.value = res.data
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  // 검색어 초기화 (캐시 비우기)
  const resetSearch = () => {
    searchKeyword.value = null
    searchBookList.value = []
    currentPage.value = 1
    hasMore.value = true

    sessionStorage.removeItem('book-session')
  }

  return {
    searchType,
    searchKeyword,
    searchBookList,
    bookDetail,
    search,
    currentPage,
    hasMore,
    isLoading,
    // loadMore,
    fetchBooks,
    goDetail,
    // resetSearch,
    fetchBookDetail,
  }
}, {
  persist: [
    {
      key: 'book-session',
      storage: sessionStorage,
      pick: ['searchKeyword', 'searchBookList', 'bookDetail']
    }
  ]
})