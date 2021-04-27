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
