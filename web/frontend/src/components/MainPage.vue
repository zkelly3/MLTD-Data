<template>
  <div class="container">
    <div class="row"><nav class="navbar navbar-expand navbar-dark bg-primary">
      <a class="navbar-brand">ポンコマス</a>
      <ul class="navbar-nav">
        <li class="nav-item">
          <router-link class="nav-link" aria-current="page" to="/idols">偶像</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" aria-current="page" to="/cards">卡片</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" aria-current="page" to="/events">活動</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" aria-current="page" to="/gashas">卡池</router-link>
        </li>
      </ul>
      <slot name="navbar"></slot>
    </nav></div>
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'MainPage',
}
</script>

<style>
.card_icon {
  display: inline-block;
  position: relative;
  height: 50px;
  width: 50px;
}
.card_icon img {
  height: 100%;
  width: 100%;
}
.card_icon:after {
  content: '';
  position: absolute;
  height: 100%;
  width: 100%;
  left: 0;
  top: 0;
  z-index: 100;
  background-size: contain;
}
.card_ssr:after {
  background-image: url('/static/images/card_icon_mark/rare_SSR.png');
}
.card_sr:after {
  background-image: url('/static/images/card_icon_mark/rare_SR.png');
}
.card_r:after {
  background-image: url('/static/images/card_icon_mark/rare_R.png');
}
.idol_pr:after, .card_n_pr:after {
  border: 2px #ff3b6a solid;
  border-radius: 5px;
}
.idol_fa:after, .card_n_fa:after {
  border: 2px #3245ff solid;
  border-radius: 5px;
}
.idol_an:after, .card_n_an:after {
  border: 2px #e6e613 solid;
  border-radius: 5px;
}
.idol_gu:after {
  border: 2px #25b340 solid;
  border-radius: 5px;
}
</style>
