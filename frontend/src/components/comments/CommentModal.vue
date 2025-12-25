<script setup>
  import { computed } from 'vue'
  import { storeToRefs } from 'pinia'
  import { useCommentStore } from '@/stores/comments'
  import { useAccountStore } from '@/stores/accounts'

  const commentStore = useCommentStore()
  const accountStore = useAccountStore()
  const { user } = storeToRefs(accountStore)
  const { isOpen, isLoading, comments, draft } = storeToRefs(commentStore)
  const { closeComments, submitComment, deleteComment } = commentStore

  const commentCount = computed(() => comments.value.length)
  const API_URL = import.meta.env.VITE_API_URL
  const fallbackProfile = new URL('@/assets/images/no_img_profile.png', import.meta.url).href

  const closeModal = () => {
    closeComments()
  }

  const resolveProfileUrl = (value) => {
    if (!value) return fallbackProfile
    if (value.startsWith('http://') || value.startsWith('https://')) return value
    if (!API_URL) return value
    return `${API_URL}${value}`
  }

  const formatDate = (value) => {
    if (!value) return ''
    return String(value).slice(0, 10)
  }

  const isOwner = (comment) => {
    if (!comment?.user?.username || !user.value?.username) return false
    return comment.user.username === user.value.username
  }

  const removeComment = (commentId) => {
    deleteComment(commentId)
  }
</script>

<template>
  <div v-if="isOpen" class="modal-bg" @click.self="closeModal">
    <div class="modal comment-modal">
      <div class="modal-header">
        <h2 class="title">댓글 전체보기</h2>
        <button class="btn-close" type="button" @click="closeModal">
          <img src="@/assets/images/common/btn_close.png" alt="닫기 버튼">
        </button>
      </div>

      <div class="comment-list" v-if="commentCount > 0">
        <div v-for="comment in comments" :key="comment.id" class="comment-item">
          <div class="comment-profile">
            <div class="profile-image">
              <img
                :src="resolveProfileUrl(comment.user?.profile_img)"
                :alt="comment.user?.full_name || 'profile'"
              >
            </div>
            <div class="comment-body">
              <div class="comment-header">
                <div>
                  <p class="comment-name">{{ comment.user?.full_name }}</p>
                  <p class="comment-created-at f-pre">{{ formatDate(comment.created_at) }}</p>
                </div>
                <button
                  v-if="isOwner(comment)"
                  class="btn btn-small btn-delete"
                  type="button"
                  @click="removeComment(comment.id)"
                >
                  삭제
                </button>
              </div>
            </div>
          </div>
          <div class="comment-content f-pre">{{ comment.content }}</div>
        </div>
      </div>
      <div v-else class="no-content">작성된 댓글이 없습니다.</div>

      <form class="comment-form" @submit.prevent="submitComment">
        <input v-model="draft" class="text-input" placeholder="댓글을 입력하세요">
        <button class="btn btn-submit" type="submit" :disabled="isLoading">등록</button>
      </form>
    </div>
  </div>
</template>

<style scoped>
  .comment-modal {
    width: 520px;
  }

  .comment-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-height: 320px;
    overflow-y: auto;
    margin-bottom: 20px;
    border-bottom: 1px solid #ddd;
  }

  .comment-item {
    border-bottom: 1px solid #eee;
    padding-bottom: 12px;
  }

  .comment-profile {
    display: flex;
    gap: 12px;
    align-items: flex-start;
  }

  .profile-image {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    overflow: hidden;
    flex-shrink: 0;
  }

  .profile-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .comment-name {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 4px;
  }

  .comment-created-at {
    font-size: 14px;
    color: #555;
    line-height: 1.4;
  }

  .comment-content {
    padding: 20px 0 30px;
    font-size: 16px;
    color: #555;
  }

  .comment-body {
    width: 100%;
  }

  .comment-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }

  .btn-delete {
    border: 1px solid #ddd;
    background-color: #fff;
    color: #111;
    font-size: 14px;
    padding: 8px 20px;
  }

  .btn-delete:hover {
    border-color: #456AFF;
    color: #456AFF;
    background-color: #EBEFFF;
  }

  .comment-form {
    display: flex;
    gap: 5px;
  }

  .text-input {
    width:80%;
  }

  .btn-submit {
    width: calc(20% - 5px);
    min-width: auto;
    font-size: 16px;
  }
</style>
