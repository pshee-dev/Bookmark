import { createRouter, createWebHistory } from 'vue-router'
import MainView from '@/views/MainView.vue'

// Todo: navigation guard 설정

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
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('@/views/SignupView.vue'),
    },

    // 서재 라우터
    {
      path: '/libraries/:username',
      name: 'libraries',
      component: () => import('@/views/library/LibraryListView.vue'),
    },
    {
      path: '/libraries/:username/:libraryId',
      name: 'library',
      component: () => import('@/views/library/LibraryDetailView.vue'),
    },

    // 피드 라우터
    {
      path: '/feeds',
      component: () => import('@/views/FeedView.vue'),
      children: [
        { path: '', name: 'feed', component: () => import('@/components/feed/FeedGalfyList.vue') },
        { path: '/galfy', name: 'feedGalfyList', component: () => import('@/components/feed/FeedGalfyList.vue') },
        { path: '/review', name: 'feedReviewList', component: () => import('@/components/feed/FeedReviewList.vue') },
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
      children: [
        { path: '', name: 'book', component: () => import('@/components/BookGalfyList.vue') },
        { path: '/galfy', name: 'bookGalfyList', component: () => import('@/components/BookGalfyList.vue') },
        { path: '/review', name: 'bookReviewList', component: () => import('@/components/BookReviewList.vue') },
      ],
    },

    // 갈피 라우터
    {
      path: '/galfy/:username/create',
      name: 'galfyCreate',
      component: () => import('@/views/galfy/GalfyCreateView.vue'),
    },
    {
      path: '/galfy/:username/:galfyId/update',
      name: 'galfyUpdate',
      component: () => import('@/views/galfy/GalfyUpdateView.vue'),
    },
    {
      path: '/galfy/:username/:galfyId',
      name: 'galfy',
      component: () => import('@/views/galfy/GalfyDetailView.vue'),
    },

    // 리뷰 라우터
    {
      path: '/review/:username/create',
      name: 'reviewCreate',
      component: () => import('@/views/review/ReviewCreateView.vue'),
    },
    {
      path: '/review/:username/:reviewId/update',
      name: 'reviewUpdate',
      component: () => import('@/views/review/ReviewUpdateView.vue'),
    },
    {
      path: '/review/:username/:reviewId/recommend',
      name: 'recommend',
      component: () => import('@/views/RecommendView.vue'),
    },
    {
      path: '/review/:username/:reviewId',
      name: 'review',
      component: () => import('@/views/review/ReviewDetailView.vue'),
    },

    // 마이페이지 라우터
    {
      path: '/bookmark/:username',
      component: () => import('@/views/UserView.vue'),
      children: [
        { path: '', name: 'user', component: () => import('@/components/UserGalfyList.vue') },
        { path: '/galfy', name: 'userGalfyList', component: () => import('@/components/UserGalfyList.vue') },
        { path: '/review', name: 'userReviewList', component: () => import('@/components/UserReviewList.vue') },
      ],
    },
  ],
})

export default router
