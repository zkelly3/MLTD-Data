<template>
  <MainPage :pageNotFound="pageNotFound">
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
      <MyTr><MyTh :class="songClass(shown.idol_type)">名稱</MyTh><MyTd>{{ shown.name }}</MyTd></MyTr>
      <MyTr><MyTh :class="songClass(shown.idol_type)">取得方式</MyTh><MyTd><b>{{ shown.aquire.name }}</b><br/>
      <router-link v-if="shown.aquire.from_url !== null" :to="shown.aquire.from_url">{{shown.aquire.from}}</router-link>
      <span v-else>{{ shown.aquire.from }}</span>
      </MyTd></MyTr>
      <MyTr><MyTh :class="songClass(shown.idol_type)">實裝時間</MyTh><MyTd>{{ shown.time }}</MyTd></MyTr>
    </div></div>
  </div>
  <ul class="nav nav-tabs mt-3" id="song_tabs" role="tablist">
    <li class="nav-item" role="presentation">
      <button class="nav-link active" id="sound-tab" data-bs-toggle="tab" data-bs-target="#sound" type="button" role="tab" aria-controls="sound" aria-selected="true">遊戲內音源</button>
    </li>
    <li v-if="shown.events" class="nav-item" role="presentation">
      <button class="nav-link" id="event-tab" data-bs-toggle="tab" data-bs-target="#gameEvent" type="button" role="tab" aria-controls="gameEvent" aria-selected="false">相關活動</button>
    </li>
  </ul>
  <div class="tab-content" id="song_tab_contents">
    <div class="tab-pane fade show active" id="sound" role="tabpanel" aria-labelledby="sound-tab">
      <table class="table align-middle">
          <tbody>
          <tr v-for="sound in shown.sound" :key="sound.id">
              <td>{{ sound.time }}</td>
              <td>{{ sound.group_name }}</td>
          </tr>
          </tbody>
      </table>
    </div>
    <div class="tab-pane fade" id="gameEvent" role="tabpanel" aria-labelledby="event-tab">
      <table class="table align-middle">
          <tbody>
          <tr v-for="event in shown.events" :key="event.id">
              <td><router-link :to="event.url">{{ event.name }}</router-link></td>
              <td>{{ showTime(event.start) }}</td>
          </tr>
          </tbody>
      </table>
    </div>
  </div>
  </MainPage>
</template>

<script>
import { h } from 'vue'
import MainPage from './MainPage.vue'
import { toDate, toDateString, toDateTimeString } from '../general'

function getDefaultSong() {
    return {
        id: 0,
        name: '不明',
        aquire: {
            'name': null,
            'from': '--',
            'from_url': null,
        },
        time: null,
    };
}

function fixData(song, ver) {
    if (!song) return;
    song.name = (!song.name) ? '不明' : song.name;
    song.time = toDateTimeString(toDate(song.time), ver);
    song.aquire.name = (!song.aquire.name) ? '尚未更新' : song.aquire.name;
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
            pageNotFound: false,
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
            }).catch((err) => {
                if (err.response && err.response.status === 404) {
                    this.pageNotFound = true;
                }
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
        songClass: function(idol_type) {
            switch (idol_type) {
                case 'All':
                    return 'song_all';
                case 'Princess':
                    return 'song_princess';
                case 'Fairy':
                    return 'song_fairy';
                case 'Angel':
                    return 'song_angel';
                default:
                    return 'song_all';
            }
        },
        showTime(time) {
            return this.japanese ? toDateString(toDate(time), 0) : toDateString(toDate(time), 1);
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
.song_all {
    background: #aaaaaa33;
}
.song_princess {
    background: #ff3b6a33;
}
.song_fairy {
    background: #3245ff33;
}
.song_angel {
    background: #e6e61333;
}
</style>