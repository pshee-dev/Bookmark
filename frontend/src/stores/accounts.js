import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useRouter } from 'vue-router'
import axios from 'axios'

export const useAccountStore = defineStore('account', () => {
  const router = useRouter()
  
  const API_URL = 'http://127.0.0.1:8000'
  const token = ref(null)

  const username = ref('user')

  // 회원가입
  const signUp = function (payload) {
    const { username, password1, password2 } = payload

    axios({
      method: 'post',
      url: `${API_URL}/accounts/signup/`,
      data: {
        username, password1, password2,
      }
    })
      .then(res => {
        console.log('회원 가입이 완료되었습니다.')
        const password = password1
        logIn({ username, password })
      })
      .catch(err => console.log(err))
  }


  // 로그인
  const logIn = function (payload) {
    const { username, password } = payload
    axios({
      method: 'post',
      url: `${API_URL}/accounts/login/`,
      data: {
        username, password
      }
    })
      .then(res => {
        console.log('로그인이 완료되었습니다.')
        token.value = res.data.key
        router.push({ name: 'main' })
      })
      .catch(err => console.log(err))
  }

  // 로그인 여부 확인
  const isLogin = computed(() => {
    return token.value ? true : false
  })

  // 로그아웃
  const logOut = function () {
    axios({
      method: 'post',
      url: `${API_URL}/accounts/logout/`
    })
      .then(res => {
        token.value = null
        router.push({ name: 'login' })
      })
      .catch(err => console.log(err))
  }

  return {
    signUp,
    logIn,
    token,
    isLogin,
    logOut,
    username,
  }
})
