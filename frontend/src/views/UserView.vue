<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import axios from 'axios'
  import { useAccountStore } from '@/stores/accounts'
  import { useErrorStore } from '@/stores/errors'

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

  const username = computed(() => route.params.username)

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
    if (!user.value?.id || !token.value) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/${user.value.id}/`,
        {
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
    if (!token.value) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/libraries/`,
        {
          params: {
            status: statusKey,
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
    if (!user.value?.id || !token.value) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/${user.value.id}/galfies/`,
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
    if (!user.value?.id || !token.value) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/users/${user.value.id}/reviews/`,
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

  onMounted(async () => {
    await fetchProfile()
    await Promise.all([
      fetchLibraryCount('reading'),
      fetchLibraryCount('want'),
      fetchLibraryCount('finished'),
      fetchGalfyCount(),
      fetchReviewCount(),
    ])
  })
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
            <li>팔로잉 <strong>{{ profile.followings_count ?? 0 }}</strong></li>
            <li>팔로워 <strong>{{ profile.followers_count ?? 0 }}</strong></li>
            <li>갈피 <strong>{{ galfyCount }}</strong></li>
            <li>리뷰 <strong>{{ reviewCount }}</strong></li>
          </ul>
        </div>
        <button class="btn btn-small btn-edit" type="button" @click.stop="goEditProfile">회원 정보 수정</button>
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
    gap: 18px;
    color: #666;
    font-size: 16px;
  }

  .profile-stats strong {
    color: #111;
    margin-left: 4px;
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
</style>
