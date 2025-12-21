<script setup>
  import LayoutHeader from '@/components/layout/LayoutHeader.vue'
  import LayoutFooter from '@/components/layout/LayoutFooter.vue'
</script>

<template>
  <LayoutHeader />
  <main>
    <RouterView />
  </main>
  <LayoutFooter />
</template>

<style scoped>
  main {
    margin-top: 100px;
    min-height: 100vh; /* test */
  }
</style>
