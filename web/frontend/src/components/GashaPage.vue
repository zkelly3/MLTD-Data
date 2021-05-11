<template>
<MainPage :pageNotFound="pageNotFound">
  <template v-slot:navbar>
  <button class="btn btn-outline-light ms-auto" v-on:click="changeLanguage()" :disabled="notBoth">{{ panelWord }}</button>
  </template>

  <div class="row">
    <nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/gashas">所有卡池</router-link></li>
        <li class="breadcrumb-item active" aria-current="page">{{ shown.name }}</li>
      </ol>
    </nav>
  </div>
  <div class="row"><div class="col">
    <table class="table" id="event"><tbody>
      <tr class="text-center"><td colspan="2"><img class="img-fluid gasha_image" :src="shown.img_url || defaultGasha" v-on:error="replaceByDefault"/></td></tr>
      <tr><th>名稱</th><td>【{{ shown.gasha_type }}】{{ shown.name }}</td></tr>
      <tr><th>開始時間</th><td>{{ shown.start }}</td></tr>
      <tr><th>結束時間</th><td>{{ shown.over }}</td></tr>
      <tr><th>備註</th><td style="white-space: pre-wrap;">{{ shown.comment }}</td></tr>
    </tbody></table>
  </div></div>
  <div class="row"><div class="col">
    <h4>Pick Up 對象</h4>
    <table class="table align-middle"><tbody>
      <tr v-for="card in shown.pick_up" :key="card.name">
        <td><router-link :to="card.url">
          <CardIcon class="me-2" :card="card" />{{ card.name }}
        </router-link></td>
        <td>{{ card.comment }}</td>
      </tr>
    </tbody></table>
  </div></div>
  <div class="row mb-3" v-if="shown.gasha_type === '特殊'"><div class="col">
    <h4>其餘活動對象卡片</h4>
    <div class="row">
      <div class="col-lg-4 mb-2" v-for="card in shown.others" :key="card.name">
        <router-link :to="card.url">
          <CardIcon class="me-2" :card="card" />{{ card.name }}
        </router-link>
      </div>
    </div>
  </div></div>
  <div class="row mb-3" v-if="shown.gasha_type !== '特殊'"><div class="col">
    <h4>同時實裝在卡池的卡片</h4>
    <div class="row">
      <div class="col-lg-4 mb-2" v-for="card in shown.others" :key="card.name">
        <router-link :to="card.url">
          <CardIcon class="me-2" :card="card" />{{ card.name }}
        </router-link>
      </div>
    </div>
  </div></div>
</MainPage>
</template>

<script>
import CardIcon from './CardIcon.vue'
import MainPage from './MainPage.vue'
import { toDate, toDateTimeString } from '../general'

function getDefaultGasha() {
    return {
        name: '不明',
        start: null,
        over: null,
        pick_up: [],
        others: [],
    };
}

function fixData(gasha, ver) {
    if (!gasha) return;
    
    gasha.name = (!gasha.name) ? '不明' : gasha.name;
    gasha.start = toDateTimeString(toDate(gasha.start), ver);
    gasha.over = toDateTimeString(toDate(gasha.over), ver);
    
    for (let i in gasha.pick_up) {
        let card = gasha.pick_up[i];
        card.name = (!card.name) ? '不明' : card.name;
    }
    
    for (let i in gasha.others) {
        let card = gasha.others[i];
        card.name = (!card.name) ? '不明' : card.name;
    }
}

export default {
    name: 'GashaPage',
    components: {
        CardIcon,
        MainPage,
    },
    inject: ['$api', '$setTitle'],
    props: ['gasha_id'],
    data() {
        return {
            gasha: [getDefaultGasha(), getDefaultGasha()],
            japanese: true,
            notBoth: false,
            defaultGasha: '/static/images/default/no_gasha_banner.png',
            pageNotFound: false,
        };
    },
    mounted() {
        this.updatePage();
    },
    methods: {
        updatePage: function() {
            this.$api.getGasha(this.gasha_id).then((res)=> {
                const tmpGasha = res.data;
                for (let i=0; i<tmpGasha.length; ++i) {
                    fixData(tmpGasha[i], i);
                }
                this.gasha = tmpGasha;
                this.initialize();
                this.$setTitle(this.shown.name);
            }).catch((err) => {
                if (err.response && err.response.status === 404) {
                    this.pageNotFound = true;
                }
            });
        },
        initialize: function() {
            if (!this.gasha[0] || !this.gasha[1]) this.notBoth = true;
            if (!this.gasha[0]) {
                this.japanese = false;
            }
        },
        changeLanguage: function() {
            this.japanese = !this.japanese;
        },
        replaceByDefault(e) {
          e.target.src = '/static/images/default/no_gasha_banner.png';
        }
    },
    computed: {
        shown: function() {
            return this.japanese ? this.gasha[0] : this.gasha[1];
        },
        panelWord: function() {
            return this.japanese ? '中文版' : '日文版'
        }
    },
    watch: {
        gasha_id: function() { this.updatePage(); },
    }
};
</script>

<style>
.gasha_image {
  max-height: 250px;
}
</style>
