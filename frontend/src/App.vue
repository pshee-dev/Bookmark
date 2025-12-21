<script setup>
  import LayoutHeader from '@/components/layout/LayoutHeader.vue'
  import LayoutFooter from '@/components/layout/LayoutFooter.vue'
  import ErrorModal from '@/components/ErrorModal.vue'
</script>

<template>
  <LayoutHeader />
  <main>
    <RouterView />
  </main>
  <LayoutFooter />

  <!-- error modal -->
  <ErrorModal />
</template>

<style scoped>
  main {
    margin-top: 100px;
    /* min-height: 100vh; */
  }
</style>
