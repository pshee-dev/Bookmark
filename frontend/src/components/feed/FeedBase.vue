<script setup>
  import { computed } from 'vue'
  import { useRouter } from 'vue-router'
  import iconLike from '@/assets/images/common/icon_like.png'
  import iconLikeActive from '@/assets/images/common/icon_likes_active.png'
  import { useFeedStore } from '@/stores/feeds'
  import { useCommentStore } from '@/stores/comments'
  import { useAccountStore } from '@/stores/accounts'
  import { storeToRefs } from 'pinia'

  const router = useRouter()
  const API_URL = import.meta.env.VITE_API_URL
  const fallbackProfile = new URL('@/assets/images/no_img_profile.png', import.meta.url).href
  const accountStore = useAccountStore()
  const feedStore = useFeedStore()
  const commentStore = useCommentStore()
  const { user } = storeToRefs(accountStore)

  const props = defineProps({
    feed: Object,
    feedType: String,
    showProfile: {
      type: Boolean,
      default: true,
    },
    showBookInfo: {
      type: Boolean,
      default: false,
    },
  })

  const formattedDate = computed(() => {
    return props.feed.created_at?.slice(0, 10)
  })

  const goFeedDetail = () => {
    const username = props.feed?.user?.username ?? user?.value?.username
    if (!username || !props.feed?.id) return
    if (props.feedType === 'review') {
      router.push({ name: 'review', params: { username, reviewId: props.feed.id } })
      return
    }
    if (props.feedType === 'galfy') {
      router.push({ name: 'galfy', params: { username, galfyId: props.feed.id } })
    }
  }

  const likeIcon = computed(() => {
    return props.feed?.is_liked ? iconLikeActive : iconLike
  })

  const resolveProfileUrl = (value) => {
    if (!value) return fallbackProfile
    if (value.startsWith('http://') || value.startsWith('https://')) return value
    if (!API_URL) return value
    return `${API_URL}${value}`
  }

  const like = async () => {
    const res = await feedStore.actionLikes(props.feedType, props.feed.id)
    if (!res) return
    if (props.feed) {
      props.feed.likes_count = res.like_count
      props.feed.is_liked = res.is_liked
    }
  }

  const openComments = () => {
    commentStore.openComments({ type: props.feedType, id: props.feed.id })
  }
</script>

<template>
  <div class="feed-card" @click.stop="goFeedDetail">
  <template v-if="showProfile">
    <div class="card-profile">
      <div class="profile-image">
        <img :src="resolveProfileUrl(feed.user?.profile_img)" :alt="feed.user?.full_name || 'profile'">
      </div>
      <p class="name">{{ feed.user.full_name }}</p>
    </div>
    <hr class="line">
  </template>
    <div class="card-body">
      <div class="tit-box">
        <h3 v-if="feedType === 'review'" class="title">{{ feed.title }}</h3>
        <h3 v-if="feedType === 'galfy'" class="title">P. {{ feed.page_number }}</h3>
        <span class="date">{{ formattedDate }}</span>
      </div>
      <p class="content">{{ feed.content }}</p>
    <div v-if="showBookInfo && feed.book" class="book-info">
        <div class="book-thumb">
          <img
            v-if="feed.book.thumbnail"
            :src="feed.book.thumbnail"
            :alt="feed.book.title"
          >
          <img v-else src="@/assets/images/no_img_bookcover.jpg" alt="no-image">
        </div>
        <div class="book-meta">
          <p class="book-title">{{ feed.book.title }}</p>
          <p v-if="feed.book.author" class="book-author">{{ feed.book.author }}</p>
          <p v-if="feed.book.publisher" class="book-publisher">{{ feed.book.publisher }}</p>
        </div>
      </div>
    </div>
    <div class="actions">
      <button class="btn-action like" @click.stop="like">
        <img :src="likeIcon" alt="like">
        <p class="action-txt">{{ feed.likes_count }}</p>
      </button>
      <button class="btn-action comment" @click.stop="openComments">
        <img src="@/assets/images/common/icon_comment.png" alt="comment">
        <p class="action-txt">{{ feed.comments_count }}</p>
      </button>
    </div>
  </div>
</template>

<style scoped>

  .feed-card {
    background-color: #f8f5ff;
    padding: 40px 30px;
    border-radius: 20px;
    transition-duration: .2s;
    border: 1px solid transparent;
    cursor: pointer;
    margin-bottom: 20px;
  }

  .feed-card:hover {
    border-color: #d6ccf5;
    transform: translateY(-2px);
  }

  .card-profile {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 10px;
  }

  .profile-image {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    overflow: hidden;
  }

  .profile-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .name {
    font-size: 18px;
    font-weight: 600;
  }

  .line {
    margin: 20px 0 30px;
    background-color: #d6ccf5;
    height: 1px;
    border: none;
  }

  .card-body {
    margin-bottom: 40px;
  }

  .tit-box {
    display: flex;
    justify-content: space-between;
    margin-bottom: 18px;
  }

  .title {
    font-size: 20px;
    font-weight: 600;
    color: #333;
  }

  .date {
    font-size: 16px;
    color: #767676;
  }

  .content {
    font-size: 18px;
    color: #555;
  }

  .book-info {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-top: 18px;
    background-color: #fff;
    padding: 15px 20px;
    border-radius: 10px;
  }

  .book-thumb {
    width: 64px;
    height: 88px;
    border-radius: 12px 24px 12px 24px;
    overflow: hidden;
    border: 1px solid #eee;
    background-color: #f1f1f1;
    flex-shrink: 0;
  }

  .book-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .book-meta {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .book-meta .book-title {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin-bottom: 6px;
  }

  .book-meta .book-author,
  .book-meta .book-publisher {
    font-size: 14px;
    color: #666;
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
</style>
