<template>
  <div class="container">
    <div class="row"><nav class="navbar navbar-expand navbar-dark bg-primary">
      <a class="navbar-brand">ポンコマス</a>
      <ul class="navbar-nav">
        <li class="nav-item">
          <a class="nav-link" aria-current="page" href="/idols">偶像</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" aria-current="page" href="/cards">卡片</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" aria-current="page" href="/events">活動</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" aria-current="page" href="/gashas">卡池</a>
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
