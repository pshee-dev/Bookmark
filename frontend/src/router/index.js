import { createRouter, createWebHistory } from 'vue-router'
import MainView from '@/views/MainView.vue'
import { useAccountStore } from '@/stores/accounts'
import { useErrorStore } from '@/stores/errors'
import { storeToRefs } from 'pinia'

/*
[ navigation guard 설정 ]

meta.requiresAuth  → 로그인 필요
meta.guestOnly     → 비로그인 전용
meta.ownerOnly     → 본인만 접근
*/

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'main',
      component: MainView,
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('@/views/SignupView.vue'),
      meta: { guestOnly: true },
    },

    // 서재 라우터
    {
      path: '/libraries/:username',
      name: 'libraries',
      component: () => import('@/views/library/LibraryListView.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/libraries/:username/:libraryId',
      name: 'library',
      component: () => import('@/views/library/LibraryDetailView.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },

    // 피드 라우터
    {
      path: '/feeds',
      component: () => import('@/views/FeedView.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'feed', component: () => import('@/components/FeedGalfyList.vue') },
        { path: 'galfy', name: 'feedGalfyList', component: () => import('@/components/FeedGalfyList.vue') },
        { path: 'review', name: 'feedReviewList', component: () => import('@/components/FeedReviewList.vue') },
      ],
    },

    // 도서 검색 및 상세보기 라우터
    {
      path: '/search',
      name: 'search',
      component: () => import('@/views/SearchView.vue'),
    },
    {
      path: '/books/:bookId',
      component: () => import('@/views/BookDetailView.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'book', component: () => import('@/components/BookGalfyList.vue') },
        { path: 'galfy', name: 'bookGalfyList', component: () => import('@/components/BookGalfyList.vue') },
        { path: 'review', name: 'bookReviewList', component: () => import('@/components/BookReviewList.vue') },
      ],
    },

    // 갈피 라우터
    {
      path: '/galfy/:username/create',
      name: 'galfyCreate',
      component: () => import('@/views/galfy/GalfyCreateView.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/galfy/:username/:galfyId/update',
      name: 'galfyUpdate',
      component: () => import('@/views/galfy/GalfyUpdateView.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/galfy/:username/:galfyId',
      name: 'galfy',
      component: () => import('@/views/galfy/GalfyDetailView.vue'),
      meta: { requiresAuth: true },
    },

    // 리뷰 라우터
    {
      path: '/review/:username/create',
      name: 'reviewCreate',
      component: () => import('@/views/review/ReviewCreateView.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/review/:username/:reviewId/update',
      name: 'reviewUpdate',
      component: () => import('@/views/review/ReviewUpdateView.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/review/:username/:reviewId/recommend',
      name: 'recommend',
      component: () => import('@/views/RecommendView.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/review/:username/:reviewId',
      name: 'review',
      component: () => import('@/views/review/ReviewDetailView.vue'),
      meta: { requiresAuth: true },
    },

    // 마이페이지 라우터
    {
      path: '/bookmark/:username',
      component: () => import('@/views/UserView.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
      children: [
        { path: '', name: 'user', component: () => import('@/components/UserGalfyList.vue') },
        { path: 'galfy', name: 'userGalfyList', component: () => import('@/components/UserGalfyList.vue') },
        { path: 'review', name: 'userReviewList', component: () => import('@/components/UserReviewList.vue') },
      ],
    },
  ],
})

router.beforeEach((to, from) => {
  const accountStore = useAccountStore()
  const errorStore = useErrorStore()
  const { isLogin, user } = storeToRefs(accountStore)
  const { errorStatus } = storeToRefs(errorStore)

  // 1. 로그인 상태에서 로그인/회원가입 접근
  if (to.meta.guestOnly && isLogin.value) {
    errorStore.openErrorModal('이미 로그인 상태입니다.')
    errorStatus.value = 'guestOnly'
    return false
  }

  // 2. 로그인 필요한 페이지인데 비로그인
  if (to.meta.requiresAuth && !isLogin.value) {
    errorStore.openErrorModal('로그인이 필요한 페이지입니다.')
    errorStatus.value = 'requiresAuth'
    return false
  }

  // 3. 본인만 접근 가능한 페이지에 다른 유저가 접근
  if (to.meta.ownerOnly) {
    console.log(to.params.username, user.value.username)

    if (to.params.username !== user.value.username) {
      errorStore.openErrorModal('접근 권한이 없습니다.')
      errorStatus.value = 'ownerOnly'
      return false
    }
  }

})

export default router
