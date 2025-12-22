<script setup>
  import { ref, watch } from 'vue'
  import { useAccountStore } from '@/stores/accounts'
  import { storeToRefs } from 'pinia'

  const accountStore = useAccountStore()
  const { signupErrors } = storeToRefs(accountStore)

  const username = ref(null)
  const password1 = ref(null)
  const password2 = ref(null)
  const lastName = ref(null)
  const firstName = ref(null)
  const email = ref(null)
  const profileImg = ref(null)

  const onFileChange = (e) => {
    profileImg.value = e.target.files[0]
  }

  const signup = function () {
    const formData = new FormData()

    formData.append('username', username.value)
    formData.append('password1', password1.value)
    formData.append('password2', password2.value)
    formData.append('last_name', lastName.value)
    formData.append('first_name', firstName.value)
    formData.append('email', email.value || '')
    // 파일 필드는 File 객체로 전달되어야 하므로 값이 있을 때만 전달
    if (profileImg.value) {
      formData.append('profile_img', profileImg.value)
    }
    
    accountStore.signup(formData)
  }

  // username 다시 작성 시 error-msg 삭제
  watch(username, () => {
    delete signupErrors.value.username
  })
</script>

<template>
  <div class="bg-container">
    <h1 class="page-title">회원가입</h1>
    <form class="form-style" @submit.prevent="signup">

      <div>
        <div class="form-header">
          <h2 class="title">기본 정보</h2>
          <p class="info"><span class="fc-red">* </span>필수입력사항</p>
        </div>

        <label class="form-label required" for="username">아이디</label>
        <input v-model="username" type="text" class="text-input" id="username" required>
        <p v-if="signupErrors?.username" class="error-msg">
          {{ signupErrors.username[0] }}
        </p>

        <label class="form-label required" for="password1">비밀번호</label>
        <input v-model="password1" type="password" class="text-input" id="password1" required>
        <p v-if="signupErrors?.password1" class="error-msg">
          {{ signupErrors.password1[0] }}
        </p>

        <label class="form-label required" for="password2">비밀번호 확인</label>
        <input v-model="password2" type="password" class="text-input" id="password2" required>
        <p v-if="signupErrors?.password2" class="error-msg">
          {{ signupErrors.password2[0] }}
        </p>

        <div>
          <div>
            <label class="form-label required" for="lastName">성</label>
            <input v-model="lastName" type="text" class="text-input" id="lastName" required>
          </div>
          <div>
            <label class="form-label required" for="firstName">이름</label>
            <input v-model="firstName" type="text" class="text-input" id="firstName" required>
          </div>
        </div>
      </div>

      <hr class="line">

      <div>
        <div class="form-header">
          <h2 class="title">추가 정보</h2>
        </div>

        <label class="form-label" for="email">이메일</label>
        <input v-model="email" type="text" class="text-input" id="email">

        <label class="form-label" for="profileImg">프로필 이미지</label>
        <input @change="onFileChange" type="file" class="file-input" id="profileImg">
      </div>

      <input type="submit" value="회원가입" class="btn-submit">
    </form>
  </div>
</template>

<style scoped>
  .bg-container {
    text-align: center;
  }

  .form-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .form-header .title {
    font-size: 24px;
    font-weight: 800;
  }

  .form-header .info {
    font-size: 14px;
    font-weight: 600;
    color: #333;
  }

  .line {
    margin: 40px 0 30px;
    border: 1px dashed #ccc;
  }

  .btn-submit {
    margin-top: 50px;
  }
</style>