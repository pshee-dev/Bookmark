<script setup>

</script>

<template>
  <div class="loading">
    <img class="rotate-r" src="@/assets/images/loading.png" alt="로딩중">
    <p>Loading</p>
  </div>
</template>

<style scoped>
  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    gap: 20px;
  }

  img {
    width: 100px;
    height: 100px;
  }

  p {
    font-size: 24px;
    font-weight: 600;
    color: #999;
  }
</style>