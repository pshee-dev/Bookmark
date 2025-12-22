<script setup>
  import { ref } from 'vue'
  import { useAccountStore } from '@/stores/accounts'

  const accountStore = useAccountStore()

  const username = ref(null)
  const password = ref(null)

  const login = function () {
    const payload = {
      username: username.value,
      password: password.value,
    }
    accountStore.login(payload)
  }
</script>

<template>
  <div class="bg-container">
    <h1 class="page-title">로그인</h1>
    <form class="form-style" @submit.prevent="login">
      <input v-model.trim="username" type="text" class="text-input" placeholder="아이디">
      <input v-model.trim="password" type="password" class="text-input" placeholder="비밀번호">
      <!-- Todo: 아이디 기억하기 -->
      <input type="submit" value="로그인" class="btn-submit">
    </form>
  </div>
</template>

<style scoped>
  .bg-container {
    text-align: center;
  }

  .form-style {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    gap: 10px;
  }
</style>