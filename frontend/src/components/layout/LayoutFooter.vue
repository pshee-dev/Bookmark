<script setup>

</script>

<template>
  <footer>
    <img class="logo-footer" src="@/assets/images/common/logo_bk.png" alt="책갈피 로고">
    <ul class="footer-menu">
      <li><a href="">개인정보처리방침</a></li>
      <li><a href="">이용약관</a></li>
      <li><a href="">문의하기</a></li>
    </ul>
    <p class="copyright f-pre">Copyright ⓒ 2025 책갈피. All rights reserved.</p>
  </footer>
</template>

<style scoped>
  footer {
    background-color: #fff; 
    padding: 50px 20px 60px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }

  .logo-footer {
    width: 120px;
  }

  .footer-menu {
    margin: 30px 0 25px;
    display: flex;
    gap: 65px;
    align-items: center;
    justify-content: center;
  }

  .footer-menu li {
    position: relative;
  }

  .footer-menu li:not(:first-child)::before {
    position: absolute;
    content: '|';
    left: -32.5px;
  }

  .footer-menu a {
    font-size: 18px;
    color: #767676;
  }

  .footer-menu a:hover {
    color: #333;
  }

  .copyright {
    color: #555;
  }
</style>