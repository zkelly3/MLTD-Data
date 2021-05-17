<template>
  <MainPage :pageNotFound="pageNotFound">
  <div class="row">
  <nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
    <ol class="breadcrumb">
      <li class="breadcrumb-item active" aria-current="page">首頁</li>
    </ol>
  </nav>
  </div>
  
  <div class="row">
    <div class="col">
      <h5>簡介</h5>
      <p>
        這是一個整理 MLTD 與其相關資訊的小破站，基本上是製作者 (我) 寫給自己開心的。<br/>
        也許會時常有資訊的錯誤或缺乏，不適合做為一個嚴謹的查詢網站。<br/>
        如果想要有較為正確的資料，請前往其他網站 ouo
      </p>
      <h5>主要頁面</h5>
      <ul>
        <li><router-link to="/idols">偶像</router-link></li>
        <li><router-link to="/cards">卡片</router-link></li>
        <li><router-link to="/events">活動</router-link></li>
        <li><router-link to="/gashas">卡池</router-link></li>
        <li><router-link to="/songs">曲目</router-link></li>
      </ul>
      <h5>其他頁面</h5>
      <ul>
        <li><router-link to="/pst">上下位整理</router-link></li>
      </ul>
    </div>
  </div>
  </MainPage>
</template>

<script>
import MainPage from './MainPage.vue'

export default {
    name: 'HomePage',
    components: {
        MainPage,
    },
};
</script>