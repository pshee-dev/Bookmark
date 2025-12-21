import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useRouter } from 'vue-router'
import axios from 'axios'

export const useAccountStore = defineStore('account', () => {
  const router = useRouter()

  const API_URL = import.meta.env.VITE_API_URL
  const token = ref(null)
  const user = ref(null) // 로그인 시 유저 정보 캐싱
  
  const signupErrors = ref({})
  

  // 회원가입
  const signup = function (formData) {
    signupErrors.value = {} // 이전 에러 초기화
    axios({
      method: 'post',
      url: `${API_URL}/accounts/signup/`,
      data: formData,
    })
      .then(res => {
        console.log('회원 가입이 완료되었습니다.')
        
        // 회원가입 후 자동 로그인
        const username = formData.get('username')
        const password = formData.get('password1')
        login({ username, password })
      })
      .catch(err => {
        if (err.response && err.response.status === 400) {
          signupErrors.value = err.response.data
        } else {
          console.error(err)
        }
      })
  }


  // 로그인
  const login = function ({ username, password }) {
    axios({
      method: 'post',
      url: `${API_URL}/accounts/login/`,
      data: {
        username, 
        password,
      }
    })
      .then(res => {
        console.log('로그인이 완료되었습니다.')
        token.value = res.data.key
        userInfo(token.value)
        router.push({ name: 'main' })
      })
      .catch(err => console.log(err))
  }

  // 유저 정보 캐싱
  const userInfo = function(token) {
    axios({
      method: 'get',
      url: `${API_URL}/accounts/user/`,
      headers: {Authorization: `Token ${token}`}
    })
      .then(res => {
        console.log(res.data)
        user.value = {
          username: res.data.username,
          name: res.data.full_name,
        }
      })
      .catch(err => console.log(err))
  }

  // 로그인 여부 확인
  const isLogin = computed(() => {
    return token.value ? true : false
  })

  // 로그아웃
  const logout = function () {
    axios({
      method: 'post',
      url: `${API_URL}/accounts/logout/`
    })
      .then(res => {
        token.value = null
        user.value = null
        router.push({ name: 'login' })
      })
      .catch(err => console.log(err))
  }

  return {
    signup,
    login,
    token,
    isLogin,
    logout,
    signupErrors,
    user,
  }
}, {persist: [
  {
    key: 'user-local',
    storage: localStorage,
    pick: ['user', 'token']
  }, 
  {
    key: 'user-session',
    storage: sessionStorage,
    pick: []
  }
]})
