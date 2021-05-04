<template>
<MainPage>
  <template v-slot:navbar>
    <button class="btn btn-outline-light ms-auto" v-on:click="changeLanguage()" :disabled="notBoth">{{ panelWord }}</button>
  </template>

  <div class="row">
    <nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
      <ol class="breadcrumb">
        <li class="breadcrumb-item active" aria-current="page">所有遊戲內曲目</li>
      </ol>
    </nav>
  </div>
  <table class="table mt-3 align-middle" id="songs">
    <tbody><tr v-for="song in pageFltSongs" :key="song.id">
        <td>{{ song.name }}<br/><small class="text-muted">{{ song.group_name }}</small></td>
        <td>{{ showTime(song.time) }}</td>
    </tr></tbody>
    </table>
    <Pagination :list="shown" :purPageInit=20 :currentInit=1 @filtered_list="val => { pageFltSongs = val; }"/>
  </MainPage>
</template>

<script>
import MainPage from './MainPage.vue'
import Pagination from './Pagination.vue'
import { toDate, toDateString } from '../general'

function fixData(songs) {
    if (!songs) return;

    for(let i in songs) {
        let song = songs[i];
        song.name = (!song.name) ? '不明' : song.name;
        song[i] = song;
    }
}

export default {
    name: 'SongsPage',
    components: {
        MainPage,
        Pagination,
    },
    inject: ['$api', '$setTitle'],
    props: [],
    data() {
        return {
            songs: [[], []],
            japanese: true,
            notBoth: false,
            pageFltSongs: [],
        };
    },
    mounted() {
        this.updatePage();
    },
    methods: {
        updatePage: function() {
            this.$api.getSongs().then((res) => {
                const tmpSongs = res.data;
                for (let i=0; i<tmpSongs.length; ++i) {
                    fixData(tmpSongs[i]);
                }
                this.songs = tmpSongs;
                this.initialize();
            });
        },
        initialize: function () {
            if (!this.songs[0] || !this.songs[1]) this.notBoth = true;
            if (!this.songs[0]) this.japanese = false;
        },
        changeLanguage: function () {
            this.japanese = !this.japanese;
        },
        showTime(time) {
            return this.japanese ? toDateString(toDate(time), 0) : toDateString(toDate(time), 1);
        },
    },
    computed: {
        shown: function () {
            return this.japanese ? this.songs[0] : this.songs[1];
        },
        panelWord: function () {
            return this.japanese ? '中文版' : '日文版'
        },
        fltSongs() {
            // 保留以便之後寫 filter
            var self = this;
            return self.songs;
        }
    },
    watch: {
    },
};
</script>
