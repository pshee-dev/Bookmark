<script setup>
  import { computed, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import axios from 'axios'
  import iconLike from '@/assets/images/common/icon_like.png'
  import iconLikeActive from '@/assets/images/common/icon_likes_active.png'
  import { useAccountStore } from '@/stores/accounts'
  import { useErrorStore } from '@/stores/errors'
  import { useFeedStore } from '@/stores/feeds'

  const route = useRoute()
  const router = useRouter()
  const errorStore = useErrorStore()
  const accountStore = useAccountStore()
  const feedStore = useFeedStore()
  const { user, token } = storeToRefs(accountStore)

  const API_URL = import.meta.env.VITE_API_URL

  const review = ref(null)
  const isLoading = ref(false)
  const isFollowing = ref(false)

  const reviewId = computed(() => route.params.reviewId)
  const book = computed(() => review.value?.book ?? {})
  const authorName = computed(() => book.value?.author ?? '')

  const isOwner = computed(() => {
    const me = user.value?.username
    const author = review.value?.user?.username
    return !!me && !!author && me === author
  })

  const showFollowButton = computed(() => {
    return !!user.value?.id && !!review.value?.user?.id && !isOwner.value
  })

  const goBookDetail = () => {
    if (!book.value?.id) return
    router.push({ name: 'bookGalfyList', params: { bookId: book.value.id } })
  }

  const fetchFollowState = async () => {
    if (!showFollowButton.value || !token.value) return
    try {
      const res = await axios.get(
        `${API_URL}/users/${user.value.id}/followings/`,
        {
          headers: {
            Authorization: `Token ${token.value}`,
          }
        }
      )
      const followings = res.data ?? []
      isFollowing.value = followings.some((item) => item.id === review.value?.user?.id)
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }

  const toggleFollow = async () => {
    if (!showFollowButton.value || !token.value) return
    try {
      const res = await axios.post(
        `${API_URL}/users/${review.value.user.id}/follow/`,
        {},
        {
          headers: {
            Authorization: `Token ${token.value}`,
          }
        }
      )
      isFollowing.value = res.status === 200
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }

  const fetchReviewDetail = async (id) => {
    if (!id) return
    isLoading.value = true
    try {
      const res = await axios.get(
        `${API_URL}/reviews/${id}/`,
        token.value
          ? { headers: { Authorization: `Token ${token.value}` } }
          : {}
      )
      review.value = res.data
      await fetchFollowState()
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  watch(
    () => reviewId.value,
    (id) => {
      fetchReviewDetail(id)
    },
    { immediate: true }
  )

  const likeIcon = computed(() => {
    return review.value?.is_liked ? iconLikeActive : iconLike
  })

  const like = async () => {
    if (!review.value?.id) return
    const res = await feedStore.actionLikes('review', review.value.id)
    if (res) {
      review.value.likes_count = res.like_count
      review.value.is_liked = res.is_liked
    }
  }

  const goUpdateReview = () => {
    if (!review.value?.id || !review.value?.user?.username) return
    router.push({ name: 'reviewUpdate', params: { username: review.value.user.username, reviewId: review.value.id } })
  }

  const deleteReview = async () => {
    if (!review.value?.id) return
    const confirmed = window.confirm('정말 삭제하시겠습니까?')
    if (!confirmed) return
    try {
      await axios.delete(
        `${API_URL}/reviews/${review.value.id}/`,
        {
          headers: {
            Authorization: `Token ${token.value}`
          }
        }
      )
      router.back()
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }
</script>

<template>
  <div class="bg-container">
    <div class="tit-wrap">
      <h1 class="page-title">{{ review?.user?.full_name }}님의 리뷰</h1>
      <div class="btn-group" v-if="isOwner">
        <button class="btn btn-small" @click="goUpdateReview">수정</button>
        <button class="btn btn-small" @click="deleteReview">삭제</button>
      </div>
    </div>
    <div class="container-box">
      <div class="profile-section">
        <div class="profile-info">
          <div class="profile-image">
            <img v-if="review?.user?.profile_img" :src="review.user.profile_img" :alt="review.user.full_name">
            <img v-else src="@/assets/images/no_img_profile.png" alt="profile-no-image">
          </div>
          <div class="profile-text">
            <p class="profile-name">{{ review?.user?.full_name }}</p>
          </div>
        </div>
        <button
          v-if="showFollowButton"
          class="btn btn-small btn-follow"
          @click="toggleFollow"
        >
          {{ isFollowing ? '팔로잉' : '팔로우' }}
        </button>
      </div>

      <div class="content-section">
        <h3 class="content-title">{{ review?.title }}</h3>
        <p class="content-text">{{ review?.content }}</p>

        <div class="book-section">
          <div class="book-thumbnail">
            <img v-if="book.thumbnail" :src="book.thumbnail" :alt="book.title">
            <img v-else src="@/assets/images/no_img_bookcover.jpg" alt="no-image">
          </div>
          <div class="book-info">
            <h2 class="book-title">{{ book.title }}</h2>
            <p class="book-author">{{ authorName }}</p>
            <button class="btn btn-small btn-book" @click="goBookDetail">책 보러가기</button>
          </div>
        </div>
      </div>

      <div class="actions">
        <button class="btn-action like" @click.stop="like">
          <img :src="likeIcon" alt="like">
          <p class="action-txt">{{ review?.likes_count ?? 0 }}</p>
        </button>
        <button class="btn-action comment">
          <img src="@/assets/images/common/icon_comment.png" alt="comment">
          <p class="action-txt">{{ review?.comments_count ?? 0 }}</p>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .tit-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 40px;
  }

  .page-title {
    margin: 0;
  }

  .btn-group {
    display: flex;
    gap: 10px;
    margin-right: 40px;
  }

  .book-section {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px 30px;
    background-color: #f9f9f9;
    border-radius: 10px;
  }

  .book-thumbnail {
    width: 100px;
    height: 140px;
    border-radius: 10px 30px 10px 30px;
    overflow: hidden;
    flex-shrink: 0;
  }

  .book-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .book-info {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .book-title {
    font-size: 16px;
    font-weight: 700;
  }

  .book-author {
    font-size: 14px;
    color: #666;
  }

  .btn-book {
    width: fit-content;
    font-size: 14px;
  }

  .content-section {
    border-top: 1px solid #eee;
    border-bottom: 1px solid #eee;
    padding: 30px 0;
    margin: 30px 0;

  }

  .profile-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .profile-info {
    display: flex;
    align-items: center;
    gap: 15px;
  }

  .profile-image {
    width: 54px;
    height: 54px;
    border-radius: 50%;
    overflow: hidden;
  }

  .profile-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .profile-name {
    font-size: 18px;
    font-weight: 600;
  }

  .btn-follow {
    border: 1px solid #ddd;
    background-color: #fff;
    color: #111;
  }

  .btn-follow:hover {
    border-color: #456AFF;
    color: #456AFF;
    background-color: #EBEFFF;
  }

  .content-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 18px;
  }

  .content-text {
    font-size: 18px;
    line-height: 1.6;
    color: #555;
    white-space: pre-line;
    margin-bottom: 25px;
  }

  .actions {
    display: flex;
    gap: 25px;
    align-items: center;
    justify-content: flex-start;
  }

  .btn-action {
    outline: none;
    border: none;
    background-color: transparent;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
  }

.action-txt {
  font-size: 16px;
  font-weight: 600;
}

.tit-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
}

.page-title {
  margin: 0;
}

.btn-group {
  display: flex;
  gap: 10px;
}
</style>
