<script setup>
  import { computed, onMounted, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import axios from 'axios'
  import { useAccountStore } from '@/stores/accounts'
  import { useErrorStore } from '@/stores/errors'
  import Loading from '@/components/Loading.vue'

  const API_URL = import.meta.env.VITE_API_URL
  const fallbackProfile = new URL('@/assets/images/no_img_profile.png', import.meta.url).href

  const route = useRoute()
  const router = useRouter()

  const accountStore = useAccountStore()
  const errorStore = useErrorStore()
  const { user, token } = storeToRefs(accountStore)

  const profile = ref({})
  const libraryCounts = ref({ reading: 0, want: 0, finished: 0 })
  const galfyCount = ref(0)
  const reviewCount = ref(0)
  const isFollowModalOpen = ref(false)
  const followType = ref('followings')
  const followList = ref([])
  const isFollowLoading = ref(false)
  const isFollowing = ref(false)
  const isFollowActionLoading = ref(false)

  const username = computed(() => route.params.username)
  const isOwner = computed(() => user.value?.username === username.value)

  const displayName = computed(() => {
    return profile.value?.full_name || user.value?.name || user.value?.username || ''
  })

  const resolveProfileUrl = (value) => {
    if (!value) return fallbackProfile
    if (value.startsWith('http://') || value.startsWith('https://')) return value
    if (!API_URL) return value
    return `${API_URL}${value}`
  }

  const fetchProfile = async () => {
    if (!token.value || !username.value) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/profile/`,
        {
          params: {
            username: username.value,
          },
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )
      profile.value = res.data
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }

  const fetchLibraryCount = async (statusKey) => {
    if (!token.value || !username.value) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/libraries/`,
        {
          params: {
            status: statusKey,
            username: username.value,
            limit: 1,
            offset: 0,
            'sort-direction': 'desc',
            'sort-type': 'created_at',
          },
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )
      libraryCounts.value[statusKey] = res.data?.count ?? 0
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }

  const fetchGalfyCount = async () => {
    if (!profile.value?.id || !token.value) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/${profile.value.id}/galfies/`,
        {
          params: {
            page: 1,
            page_size: 1,
            'sort-direction': 'desc',
            'sort-field': 'created_at',
          },
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )
      galfyCount.value = res.data?.count ?? 0
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }

  const fetchReviewCount = async () => {
    if (!profile.value?.id || !token.value) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/${profile.value.id}/reviews/`,
        {
          params: {
            page: 1,
            page_size: 1,
            'sort-direction': 'desc',
            'sort-field': 'created_at',
          },
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )
      reviewCount.value = res.data?.count ?? 0
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }

  const goEditProfile = () => {
    if (!username.value) return
    router.push({ name: 'userEdit', params: { username: username.value } })
  }

  const openFollowModal = async (type) => {
    followType.value = type === 'followers' ? 'followers' : 'followings'
    isFollowModalOpen.value = true
    await fetchFollowList()
  }

  const closeFollowModal = () => {
    isFollowModalOpen.value = false
    followList.value = []
  }

  const goUserProfile = (targetUsername) => {
    if (!targetUsername) return
    closeFollowModal()
    router.push({ name: 'userGalfyList', params: { username: targetUsername } })
  }

  const fetchFollowList = async () => {
    if (!profile.value?.id || !token.value) return
    isFollowLoading.value = true
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/${profile.value.id}/${followType.value}/`,
        {
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )
      followList.value = Array.isArray(res.data) ? res.data : []
    } catch (err) {
      if (err.response?.status === 404) {
        followList.value = []
      } else {
        errorStore.handleRequestError(err)
      }
    } finally {
      isFollowLoading.value = false
    }
  }

  const refreshForUser = async () => {
    await fetchProfile()
    await Promise.all([
      fetchLibraryCount('reading'),
      fetchLibraryCount('want'),
      fetchLibraryCount('finished'),
    ])
    await Promise.all([
      fetchGalfyCount(),
      fetchReviewCount(),
    ])
    if (!isOwner.value) {
      await fetchFollowStatus()
    }
  }

  const fetchFollowStatus = async () => {
    if (!user.value?.id || !profile.value?.id || !token.value) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/${user.value.id}/followings/`,
        {
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )
      const list = Array.isArray(res.data) ? res.data : []
      isFollowing.value = list.some((item) => item.id === profile.value.id)
    } catch (err) {
      if (err.response?.status === 404) {
        isFollowing.value = false
      } else {
        errorStore.handleRequestError(err)
      }
    }
  }

  const toggleFollow = async () => {
    if (!profile.value?.id || isFollowActionLoading.value) return
    isFollowActionLoading.value = true
    try {
      const res = await axios.post(
        `${API_URL}/api/v1/users/${profile.value.id}/follow/`,
        {},
        {
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )
      if (res.status === 200) {
        isFollowing.value = true
        profile.value.followers_count = (profile.value.followers_count ?? 0) + 1
      } else if (res.status === 204) {
        isFollowing.value = false
        profile.value.followers_count = Math.max((profile.value.followers_count ?? 1) - 1, 0)
      }
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isFollowActionLoading.value = false
    }
  }

  onMounted(async () => {
    await refreshForUser()
  })

  watch(
    () => route.params.username,
    () => {
      refreshForUser()
    }
  )
</script>

<template>
  <div class="bg-container user-page">
    <div class="container-box profile-section">
      <div class="profile-info">
        <div class="profile-image">
          <img
            :src="resolveProfileUrl(profile.profile_img)"
            :alt="displayName"
          >
        </div>
        <div class="profile-text">
          <h2 class="profile-title"><b>{{ displayName }}</b>님의 책갈피</h2>
          <ul class="profile-stats">
            <li>
              <button class="stat-button" type="button" @click="openFollowModal('followings')">
                팔로잉 <strong>{{ profile.followings_count ?? 0 }}</strong>
              </button>
            </li>
            <li>
              <button class="stat-button" type="button" @click="openFollowModal('followers')">
                팔로워 <strong>{{ profile.followers_count ?? 0 }}</strong>
              </button>
            </li>
            <li>갈피 <strong>{{ galfyCount }}</strong></li>
            <li>리뷰 <strong>{{ reviewCount }}</strong></li>
          </ul>
        </div>
        <button
          v-if="isOwner"
          class="btn btn-small btn-edit"
          type="button"
          @click.stop="goEditProfile"
        >
          회원 정보 수정
        </button>
        <button
          v-else
          class="btn btn-small btn-edit"
          type="button"
          :disabled="isFollowActionLoading"
          @click.stop="toggleFollow"
        >
          {{ isFollowing ? '언팔로우' : '팔로우' }}
        </button>
      </div>

      <div class="library-summary">
        <div class="summary-item">
          <p class="label">읽고 있는 책</p>
          <p class="value">{{ libraryCounts.reading }}</p>
        </div>
        <div class="summary-item">
          <p class="label">읽고 싶은 책</p>
          <p class="value">{{ libraryCounts.want }}</p>
        </div>
        <div class="summary-item">
          <p class="label">다 읽은 책</p>
          <p class="value">{{ libraryCounts.finished }}</p>
        </div>
      </div>
    </div>

    <div class="container-box">
      <ul class="tab-menu">
        <li>
          <RouterLink
            :to="{ name: 'userGalfyList', params: { username: username } }"
            class="tab-link"
          >
            갈피
          </RouterLink>
        </li>
        <li>
          <RouterLink
            :to="{ name: 'userReviewList', params: { username: username } }"
            class="tab-link"
          >
            리뷰
          </RouterLink>
        </li>
      </ul>

      <RouterView />
    </div>
  </div>

  <div v-if="isFollowModalOpen" class="modal-bg" @click.self="closeFollowModal">
    <div class="modal follow-modal">
      <div class="modal-header">
        <h2 class="title">{{ followType === 'followers' ? '팔로워' : '팔로잉' }}</h2>
        <button class="btn-close" type="button" @click="closeFollowModal">
          <img src="@/assets/images/common/btn_close.png" alt="닫기 버튼">
        </button>
      </div>
      <div v-if="isFollowLoading" class="no-content"><Loading /></div>
      <div v-else-if="followList.length === 0" class="no-content">팔로우 정보가 없습니다.</div>
      <ul v-else class="follow-list">
        <li
          v-for="item in followList"
          :key="item.id"
          class="follow-item"
          @click="goUserProfile(item.username)"
        >
          <div class="profile-image small">
            <img :src="resolveProfileUrl(item.profile_img)" :alt="item.full_name">
          </div>
          <p class="name f-pre"><small class="username f-pre">{{ item.username }}</small>{{ item.full_name }}</p>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
  .user-page {
    padding-top: 120px;
  }

  .profile-section {
    padding: 60px 80px;
  }

  .profile-info {
    position: relative;
    display: flex;
    align-items: center;
    gap: 25px;
  }

  .profile-image {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    overflow: hidden;
    border: 1px solid #eee;
    background-color: #f2f2f2;
  }

  .profile-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .profile-title {
    font-size: 26px;
    margin-bottom: 12px;
  }

  .profile-title b {
    font-weight: 700;
  }

  .profile-stats {
    display: flex;
    align-items: center;
    gap: 18px;
    color: #666;
    font-size: 16px;
  }

  .profile-stats strong {
    color: #111;
    margin-left: 4px;
  }

  .stat-button {
    border: none;
    background: transparent;
    color: inherit;
    font-size: inherit;
    padding: 0;
    cursor: pointer;
  }

  .btn-edit {
    position: absolute;
    right: 0;
    top: 0;
  }

  .library-summary {
    background-color: #f5f5f5;
    border-radius: 20px;
    margin-top: 25px;
    padding: 22px 30px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    text-align: center;
  }

  .summary-item {
    border-right: 1px solid #e5e1f2;
  }

  .summary-item:last-child {
    border-right: none;
  }

  .summary-item .label {
    font-size: 15px;
    color: #777;
    margin-bottom: 8px;
  }

  .summary-item .value {
    font-size: 24px;
    font-weight: 700;
    color: #111;
  }

  .container-box + .container-box {
    margin-top: 40px;
    padding: 40px 50px 50px;
  }

  .tab-link {
    width: 100%;
    padding: 18px 0;
    font-size: 20px;
    color: #999;
    font-weight: 400;
    display: block;
    position: relative;
    text-decoration: none;
  }

  .follow-modal {
    width: 480px;
  }

  .follow-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-height: 360px;
    overflow-y: auto;
  }

  .follow-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    color: #111;
    transition: all ease .2s;
    cursor: pointer;
  }

  .follow-item:hover .name {
    color: #456AFF;
  }

  .profile-image.small {
    width: 44px;
    height: 44px;
  }

  .name {
    font-size: 16px;
    font-weight: 600;
  }

  .name .username {
    display: block;
    color: #555;
    margin-bottom: 5px;
    font-size: 80%;
    font-weight: 400;
  }
</style>
