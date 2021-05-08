<template>
  <MainPage>
  <template v-slot:navbar>
  <button class="btn btn-outline-light ms-auto" v-on:click="changeLanguage()" :disabled="notBoth">{{ panelWord }}</button>
  </template>

  <div class="row">
  <nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
    <ol class="breadcrumb">
      <li class="breadcrumb-item"><router-link to="/songs">所有遊戲內曲目</router-link></li>
      <li class="breadcrumb-item active" aria-current="page">{{ shown.name }}</li>
    </ol>
  </nav>
  </div>
  <div class="row g-0">
    <div class="col-xl-2 col-lg-3 col-12 text-center">
      <img class="song_image mw-100" :src="shown.img_url"/>
    </div>
    <div class="col-xl-10 col-lg-9"><div class="container-fluid">
      <MyTr><MyTh>名稱</MyTh><MyTd>{{ shown.name }}</MyTd></MyTr>
      <MyTr><MyTh>取得方式</MyTh><MyTd>尚未更新</MyTd></MyTr>
      <MyTr><MyTh>實裝時間</MyTh><MyTd>{{ shown.time }}</MyTd></MyTr>
    </div></div>
  </div>
  <ul class="nav nav-tabs mt-3">
    <li class="nav-item"><a class="nav-link active" href="#">遊戲內音源</a></li>
  </ul>
  <table id="cards" class="table align-middle">
    <tbody>
      <tr v-for="sound in shown.sound" :key="sound.id">
        <td>{{ sound.time }}</td>
        <td>{{ sound.group_name }}</td>
      </tr>
    </tbody>
  </table>
  </MainPage>
</template>

<script>
import { h } from 'vue'
import MainPage from './MainPage.vue'
import { toDate, toDateTimeString } from '../general'

function getDefaultSong() {
    return {
        id: 0,
        name: '不明',
        time: null,
    };
}

function fixData(song, ver) {
    if (!song) return;
    song.name = (!song.name) ? '不明' : song.name;
    song.time = toDateTimeString(toDate(song.time), ver);
    for (let i in song.sound) {
        song.sound[i].time = toDateTimeString(toDate(song.sound[i].time), ver);
    }
}

const MyTr = {
    name: 'MyTr',
    render() {
        return h('div', {class: "row g-0 border-bottom"}, this.$slots.default());
    },
};

const MyTh = {
    name: 'MyTh',
    render() {
        return h('div', {class: "col-xl-2 col-sm-3 p-2"}, this.$slots.default());
    },
};

const MyTd = {
    name: 'MyTd',
    render() {
        return h('div', {class: "col-xl-10 col-sm-9 p-2"}, this.$slots.default());
    },
};

export default {
    name: 'SongPage',
    components: {
        MainPage,
        MyTr,
        MyTh,
        MyTd,
    },
    inject: ['$api', '$setTitle'],
    props: ['song_id'],
    data() {
        return {
            song: [getDefaultSong(), getDefaultSong()],
            japanese: true,
            notBoth: false,
        };
    },
    mounted() {
        this.updatePage();
    },
    methods: {
        updatePage: function() {
            this.$api.getSong(this.song_id).then((res) => {
                const tmpSong = res.data;
                for (let i=0; i<tmpSong.length; ++i) {
                    fixData(tmpSong[i], i);
                }
                this.song = tmpSong;
                this.initialize();
                this.$setTitle(this.shown.name);
            });
        },
        initialize: function() {
            if (!this.song[0] || !this.song[1]) this.notBoth = true;
            if (!this.song[0]) {
                this.japanese = false;
            }
            
        },
        changeLanguage: function() {
            this.japanese = !this.japanese;
        },
    },
    computed: {
        shown: function() {
            return this.japanese ? this.song[0] : this.song[1];
        },
        panelWord: function() {
            return this.japanese ? '中文版' : '日文版'
        },
    },
    watch: {
        song_id: function() { this.updatePage(); },
    }
}
</script>

<style>
.song_image {
    height: 150px;
}
</style>