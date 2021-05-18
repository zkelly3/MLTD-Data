<template>
<MainPage :pageNotFound="pageNotFound">
  <template v-slot:navbar>
    <button class="btn btn-outline-light ms-auto" v-on:click="changeLanguage()" :disabled="notBoth">{{ panelWord }}</button>
  </template>
  <div class="row">
    <nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
      <ol class="breadcrumb">
        <li class="breadcrumb-item active" aria-current="page">{{ shown.name }}</li>
      </ol>
    </nav>
  </div>

  <div class="row">
    <div class="col">
      <table class="table">
        <tbody>
          <tr>
            <th>名稱</th><td>{{ shown.name }}</td>
          </tr>
          <tr>
            <th>遊戲內曲目</th><td>
              <div class="row">
                <div class="col-4 mb-2" v-for="song in shown.songs" :key="song.id">
                  <router-link :to="song.url" ><img class="song_icon me-2" :src="song.img_url"/>{{ song.name }}</router-link>
                </div>
              </div>
            </td>
          </tr>
          <tr>
            <th>成員</th><td>
              <div class="row">
                <div class="col-3 mb-2" v-for="idol in shown.members" :key="idol.id">
                  <router-link :to="idol.url"><img class="idol_icon me-2" :src="idol.img_url"/>{{ idol.name }}</router-link>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  </MainPage>
</template>

<script>
import MainPage from './MainPage.vue'
import { toDate, toDateString } from '../general'

function getDefaultGroup() {
    return {
        id: 0,
        name: '不明',
        songs:[],
        members:[],
    };
}

function fixData(group) {
    if (!group) return;
    group.name = (!group.name) ? '不明' : group.name;
}

export default {
    name: 'GroupPage',
    components: {
        MainPage,
    },
    inject: ['$api', '$setTitle'],
    props: ['group_id'],
    data() {
        return {
            group: [getDefaultGroup(), getDefaultGroup()],
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
            this.$api.getGroup(this.group_id).then((res) => {
                const tmpGroup = res.data;
                for (let i=0; i<tmpGroup.length; ++i) {
                    fixData(tmpGroup[i]);
                }
                this.group = tmpGroup;
                this.initialize();
                this.$setTitle(this.shown.name);
            }).catch((err) => {
                if (err.response && err.response.status === 404) {
                    this.pageNotFound = true;
                }
            });
        },
        initialize: function() {
            if (!this.group[0] || !this.group[1]) this.notBoth = true;
            if (!this.group[0]) {
                this.japanese = false;
            }
            
        },
        changeLanguage: function() {
            this.japanese = !this.japanese;
        },
        showTime(time) {
            return this.japanese ? toDateString(toDate(time), 0) : toDateString(toDate(time), 1);
        },
    },
    computed: {
        shown: function() {
            return this.japanese ? this.group[0] : this.group[1];
        },
        panelWord: function() {
            return this.japanese ? '中文版' : '日文版'
        },
    },
    watch: {
        group_id: function() { this.updatePage(); },
    }
}
</script>

<style>
.song_icon {
  height: 40px;
}
.idol_icon {
  height: 40px;
}
</style>