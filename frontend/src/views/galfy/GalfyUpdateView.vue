<script setup>
  import { computed, ref, watch } from 'vue'
  import { useRoute } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import axios from 'axios'
  import { useAccountStore } from '@/stores/accounts'
  import { useErrorStore } from '@/stores/errors'
  import GalfyForm from '@/components/feed/GalfyForm.vue'

  const route = useRoute()
  const errorStore = useErrorStore()
  const accountStore = useAccountStore()
  const { token } = storeToRefs(accountStore)

  const API_URL = import.meta.env.VITE_API_URL
  const galfyId = computed(() => route.params.galfyId)
  const galfy = ref(null)

  const fetchGalfyDetail = async (id) => {
    if (!id) return
    try {
      const res = await axios.get(
        `${API_URL}/api/v1/galfies/${id}/`,
        token.value
          ? { headers: { Authorization: `Token ${token.value}` } }
          : {}
      )
      galfy.value = res.data
    } catch (err) {
      errorStore.handleRequestError(err)
    }
  }

  watch(
    () => galfyId.value,
    (id) => {
      fetchGalfyDetail(id)
    },
    { immediate: true }
  )
</script>

<template>
  <div class="bg-container">
    <h1 class="page-title">갈피 수정</h1>
    <div class="container-box">
      <GalfyForm mode="update" :initial-value="galfy" />
    </div>
  </div>
</template>

<style scoped>

</style>
