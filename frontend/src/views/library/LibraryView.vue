<script setup>
  import { useRoute } from 'vue-router'
  const route = useRoute()
  const username = route.params.username
</script>

<template>
  <div class="bg-container">
    <h1 class="page-title">내 서재</h1>
    <div class="container-box">
      <ul class="tab-menu">
        <li><RouterLink :to="{name: 'reading', params: { username: username }}">읽고 있는 책</RouterLink></li>
        <li><RouterLink :to="{name: 'want', params: { username: username }}">읽고 싶은 책</RouterLink></li>
        <li><RouterLink :to="{name: 'finished', params: { username: username }}">다 읽은 책</RouterLink></li>
      </ul>

      <RouterView />
    </div>
  </div>
</template>

<style scoped>
 .container-box {
  padding-bottom: 100px;
 }
</style>