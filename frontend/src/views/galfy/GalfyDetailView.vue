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
  import { useCommentStore } from '@/stores/comments'

  const route = useRoute()
  const router = useRouter()
  const errorStore = useErrorStore()
  const accountStore = useAccountStore()
  const feedStore = useFeedStore()
  const commentStore = useCommentStore()
  const { user, token } = storeToRefs(accountStore)

  const API_URL = import.meta.env.VITE_API_URL

  const galfy = ref(null)
  const isLoading = ref(false)
  const isFollowing = ref(false)

  const galfyId = computed(() => route.params.galfyId)
  const book = computed(() => galfy.value?.book ?? {})
  const authorName = computed(() => book.value?.author ?? '')

  const isOwner = computed(() => {
    const me = user.value?.username
    const author = galfy.value?.user?.username
    return !!me && !!author && me === author
  })

  const showFollowButton = computed(() => {
    return !!user.value?.id && !!galfy.value?.user?.id && !isOwner.value
  })

  const goBookDetail = () => {
    if (!book.value?.id) return
    router.push({ name: 'bookGalfyList', params: { bookId: book.value.id } })
  }

  const fetchFollowState = async () => {
    if (!showFollowButton.value || !token.value) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/${user.value.id}/followings/`,
        {
          headers: {
            Authorization: `Token ${token.value}`,
          }
        }
      )
      const followings = res.data ?? []
      isFollowing.value = followings.some((item) => item.id === galfy.value?.user?.id)
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }

  const toggleFollow = async () => {
    if (!showFollowButton.value || !token.value) return
    try {
      const res = await axios.post(
        `${API_URL}/api/v1/users/${galfy.value.user.id}/follow/`,
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

  const fetchGalfyDetail = async (id) => {
    if (!id) return
    isLoading.value = true
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/galfies/${id}/`,
        token.value
          ? { headers: { Authorization: `Token ${token.value}` } }
          : {}
      )
      galfy.value = res.data
      await fetchFollowState()
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  watch(
    () => galfyId.value,
    (id) => {
      fetchGalfyDetail(id)
    },
    { immediate: true }
  )

  const likeIcon = computed(() => {
    return galfy.value?.is_liked ? iconLikeActive : iconLike
  })

  const like = async () => {
    if (!galfy.value?.id) return
    const res = await feedStore.actionLikes('galfy', galfy.value.id)
    if (res) {
      galfy.value.likes_count = res.like_count
      galfy.value.is_liked = res.is_liked
    }
  }

  const openComments = () => {
    if (!galfy.value?.id) return
    commentStore.openComments({ type: 'galfy', id: galfy.value.id })
  }

  const goUpdateGalfy = () => {
    if (!galfy.value?.id || !galfy.value?.user?.username) return
    router.push({ name: 'galfyUpdate', params: { username: galfy.value.user.username, galfyId: galfy.value.id } })
  }

  const deleteGalfy = async () => {
    if (!galfy.value?.id) return
    const confirmed = window.confirm('정말 삭제하시겠습니까?')
    if (!confirmed) return
    try {
      await axios.delete(
        `${API_URL}/api/v1/galfies/${galfy.value.id}/`,
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
      <h1 class="page-title">{{ galfy?.user?.full_name }}님의 갈피</h1>
      <div class="btn-group" v-if="isOwner">
        <button class="btn btn-small" @click="goUpdateGalfy">수정</button>
        <button class="btn btn-small" @click="deleteGalfy">삭제</button>
      </div>
    </div>
    <div class="container-box">
      <div class="profile-section">
        <div class="profile-info">
          <div class="profile-image">
            <img v-if="galfy?.user?.profile_img" :src="galfy.user.profile_img" :alt="galfy.user.full_name">
            <img v-else src="@/assets/images/no_img_profile.png" alt="profile-no-image">
          </div>
          <div class="profile-text">
            <p class="profile-name">{{ galfy?.user?.full_name }}</p>
          </div>
        </div>
        <button
          v-if="showFollowButton"
          class="btn btn-small btn-follow"
          @click="toggleFollow"
        >
          {{ isFollowing ? '언팔로우' : '팔로우' }}
        </button>
      </div>

      <div class="content-section">
        <h3 class="content-title">P. {{ galfy?.page_number }}</h3>
        <p class="content-text">{{ galfy?.content }}</p>

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
          <p class="action-txt">{{ galfy?.likes_count ?? 0 }}</p>
        </button>
        <button class="btn-action comment" @click.stop="openComments">
          <img src="@/assets/images/common/icon_comment.png" alt="comment">
          <p class="action-txt">{{ galfy?.comments_count ?? 0 }}</p>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
  font-family: 'Pretendard', sans-serif;
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
  margin-right: 40px;
}
</style>
