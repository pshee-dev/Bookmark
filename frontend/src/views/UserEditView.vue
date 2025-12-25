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

  const form = ref({
    username: '',
    last_name: '',
    first_name: '',
    email: '',
  })

  const profileFile = ref(null)
  const profilePreview = ref('')
  const profileOrigin = ref('')
  const removeProfile = ref(false)
  const isLoading = ref(false)

  const displayName = computed(() => {
    return user.value?.name || user.value?.username || ''
  })

  const resolveProfileUrl = (value) => {
    if (!value) return fallbackProfile
    if (value.startsWith('http://') || value.startsWith('https://')) return value
    if (!API_URL) return value
    return `${API_URL}${value}`
  }

  const fetchMe = async () => {
    if (!token.value) return
    isLoading.value = true
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/accounts/user/`,
        {
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )
      form.value.username = res.data?.username ?? ''
      form.value.last_name = res.data?.last_name ?? ''
      form.value.first_name = res.data?.first_name ?? ''
      form.value.email = res.data?.email ?? ''
      profileOrigin.value = resolveProfileUrl(res.data?.profile_img || '')
      profilePreview.value = profileOrigin.value
      removeProfile.value = false
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  const onFileChange = (e) => {
    const file = e.target.files?.[0] || null
    profileFile.value = file
    if (!file) {
      profilePreview.value = profileOrigin.value
      return
    }
    removeProfile.value = false
    profilePreview.value = URL.createObjectURL(file)
  }

  const clearProfile = () => {
    profileFile.value = null
    removeProfile.value = true
    profilePreview.value = fallbackProfile
  }

  const submit = async () => {
    if (!token.value) return
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('last_name', form.value.last_name || '')
      formData.append('first_name', form.value.first_name || '')
      formData.append('email', form.value.email || '')
      if (profileFile.value) {
        formData.append('profile_img', profileFile.value)
      } else if (removeProfile.value) {
        formData.append('profile_img', '')
      }

      const res = await axios.patch(
        `${API_URL}/api/v1/accounts/user/`,
        formData,
        {
          headers: {
            Authorization: `Token ${token.value}`,
          },
        }
      )

      if (user.value) {
        user.value = {
          ...user.value,
          id: res.data?.id ?? user.value.id,
          username: res.data?.username ?? user.value.username,
          name: res.data?.full_name ?? user.value.name,
        }
      }

      router.push({ name: 'user', params: { username: res.data?.username ?? route.params.username } })
    } catch (err) {
      errorStore.handleRequestError(err)
    } finally {
      isLoading.value = false
    }
  }

  const cancel = () => {
    router.back()
  }

  onMounted(() => {
    fetchMe()
  })
</script>

<template>
  <div class="bg-container">
    <h1 class="page-title">회원 정보 수정</h1>
    <form class="form-style" @submit.prevent="submit">
      <div class="profile-preview">
        <div class="preview-image">
          <img :src="profilePreview || fallbackProfile" :alt="displayName">
        </div>
        <div class="preview-info">
          <p class="preview-name">{{ displayName }}</p>
          <div class="preview-actions">
            <label class="btn btn-small btn-outline f-pre" for="profileImg">이미지 변경</label>
            <button class="btn btn-small btn-outline f-pre" type="button" @click="clearProfile">이미지 초기화</button>
          </div>
          <input @change="onFileChange" type="file" class="file-input hidden" id="profileImg">
        </div>
      </div>

      <label class="form-label" for="username">아이디</label>
      <input v-model="form.username" type="text" class="text-input" id="username" disabled>

      <label class="form-label required" for="lastName">성</label>
      <input v-model="form.last_name" type="text" class="text-input" id="lastName" required>

      <label class="form-label required" for="firstName">이름</label>
      <input v-model="form.first_name" type="text" class="text-input" id="firstName" required>

      <label class="form-label" for="email">이메일</label>
      <input v-model="form.email" type="email" class="text-input" id="email">

      <div class="btn-row">
        <button class="btn btn-outline" type="button" @click="cancel">취소</button>
        <button class="btn" type="submit" :disabled="isLoading">저장</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
  .bg-container {
    text-align: center;
  }

  .profile-preview {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 30px;
    text-align: left;
  }

  .preview-image {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    overflow: hidden;
    border: 1px solid #eee;
    background-color: #f2f2f2;
    flex-shrink: 0;
  }

  .preview-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .preview-info {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .preview-name {
    font-size: 20px;
    font-weight: 700;
  }

  .preview-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .preview-actions * {
    line-height: 1;
  }

  .hidden {
    display: none;
  }

  .btn-row {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 40px;
  }

  .btn-outline {
    background-color: #fff;
    border: 1px solid #ddd;
    color: #333;
  }

  .btn-outline:hover {
    border-color: #111;
    color: #111;
    background-color: #f5f5f5;
  }
</style>
