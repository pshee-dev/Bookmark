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
  const accountStore = useAccountStore()
  const feedStore = useFeedStore()
  const commentStore = useCommentStore()
  const { user } = storeToRefs(accountStore)

  const props = defineProps({
    feed: Object,
    feedType: String,
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

  const like = async () => {
    await feedStore.actionLikes(props.feedType, props.feed.id)
  }

  const openComments = () => {
    commentStore.openComments({ type: props.feedType, id: props.feed.id })
  }
</script>

<template>
  <div class="feed-card" @click.stop="goFeedDetail">
    <div class="card-profile">
      <div class="profile-image">
        <img v-if="feed.user.profile_img" :src="feed.user.profile_img" :alt="feed.user.full_name">
        <img v-else src="@/assets/images/no_img_profile.png" alt="profile-no-image">
      </div>
      <p class="name">{{ feed.user.full_name }}</p>
    </div>
    <hr class="line">
    <div class="card-body">
      <div class="tit-box">
        <h3 v-if="feedType === 'review'" class="title">{{ feed.title }}</h3>
        <h3 v-if="feedType === 'galfy'" class="title">P. {{ feed.page_number }}</h3>
        <span class="date">{{ formattedDate }}</span>
      </div>
      <p class="content">{{ feed.content }}</p>
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
    background: linear-gradient(90deg, rgba(69, 106, 255, 0.05) 0%, rgba(163, 58, 255, 0.05) 100%);
    padding: 30px 40px 50px;
    border-radius: 20px;
    transition-duration: .2s;
    border: 2px solid transparent;
    cursor: pointer;
    margin-bottom: 20px;
  }

  .feed-card:hover {
    border: 2px solid #7830b7;
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
    border: 1px soild #ccc;
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
</style>
