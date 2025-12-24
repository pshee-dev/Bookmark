<script setup>
  import { computed } from 'vue'
  import { useLibraryStore } from '@/stores/libraries'
  import { storeToRefs } from 'pinia'
  import { useScrollReveal } from '@/composables/scrollReveal'
  const { collect } = useScrollReveal()

  const props = defineProps({
    book: {
      type: Object,
      default: null,
    },
  })

  const libraryStore = useLibraryStore()
  const { libraryBook } = storeToRefs(libraryStore)

  const displayBook = computed(() => {
    return props.book ?? libraryBook.value?.book ?? {}
  })
</script>

<template>
  <div class="book-info">
    <div class="thumbnail fadein" :ref="collect">
      <img v-if="displayBook.thumbnail" :src="displayBook.thumbnail" :alt="displayBook.title">
      <img v-else src="@/assets/images/no_img_bookcover.jpg" alt="no-image">
    </div>
    <div class="info fadeinright80" :ref="collect">
      <h3 class="title">{{ displayBook.title }}</h3>
      <p>
        <span v-if="displayBook.author">{{ displayBook.author }}</span>
        <span v-if="displayBook.author && displayBook.publisher"> | </span>
        <span v-if="displayBook.publisher">{{ displayBook.publisher }}</span>
      </p>
    </div>
  </div>
  <hr class="line">
</template>

<style scoped>
.book-info {
  display: flex;
  gap: 30px;
  justify-content: flex-start;
  align-items: center;
}

.thumbnail {
  border-radius: 10px 30px 10px 30px;
  overflow: hidden;
  border: 1px solid #ddd;
}

.info .title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 15px;
}

.info p {
  font-size: 18px;
  color: #767676;
}

.line {
  margin: 50px 0;
  border-color: #ddd;
}
</style>
