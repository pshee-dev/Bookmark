import { onUnmounted, onMounted, nextTick } from 'vue'
import { gsap } from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function useScrollReveal() {
  // DOM 요소 → ScrollTrigger 인스턴스 1:1 매핑
  const triggers = new Map()

  const refresh = () => {
    requestAnimationFrame(() => ScrollTrigger.refresh())
  }

  const collect = (el) => {
    // el이 null 이거나 이미 처리된 요소인 경우 무시
    if (!el) return

    /*
    RouterLink 같은 컴포넌트 인스턴스에도 스크롤 트리거 적용
    ref로 전달받았을 때, 
      1. el = 컴포넌트 객체
      2. el.$el = 실제 DOM 요소(Vue 컴포넌트 인스턴스의 실제 DOM 루트 요소)
    */
    const target = el.$el ?? el
    if (!target || triggers.has(target)) return

    const trigger = ScrollTrigger.create({
      trigger: target,
      start: 'top 90%', // 요소의 시작점이 화면의 90%에 도달했을 때
      toggleClass: { targets: target, className: 'show' },
      // onEnter: () => el.classList.add('show'), // .show 클래스 추가
      // onEnterBack: () => {},
      // once: true,
    })

    // 매핑 저장
    triggers.set(target, trigger)
  }

  onUnmounted(() => {
    // 컴포넌트 unmount 시 초기화
    triggers.forEach(t => t.kill())
    triggers.clear()
  })

  onMounted(async () => {
    await nextTick()
    refresh()
  })

  return { collect, refresh }
}
