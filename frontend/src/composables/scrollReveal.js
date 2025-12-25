import { onUnmounted } from 'vue'
import { gsap } from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function useScrollReveal() {
  // DOM 요소 → ScrollTrigger 인스턴스 1:1 매핑
  const triggers = new Map()

  const collect = (el) => {
    // el이 null 이거나 이미 처리된 요소인 경우 무시
    if (!el || triggers.has(el)) return

    const trigger = ScrollTrigger.create({
      trigger: el,
      start: 'top 90%', // 요소의 시작점이 화면의 90%에 도달했을 때
      onEnter: () => el.classList.add('show'), // .show 클래스 추가
      once: true,
    })

    // 매핑 저장
    triggers.set(el, trigger)
  }

  onUnmounted(() => {
    // 컴포넌트 unmount 시 초기화
    triggers.forEach(t => t.kill())
    triggers.clear()
  })

  return { collect }
}
