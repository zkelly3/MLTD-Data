<template>
<MainPage>
  <template v-slot:navbar>
    <button class="btn btn-outline-light ms-auto" v-on:click="changeLanguage()" :disabled="notBoth">{{ panelWord }}</button>
  </template>

  <div class="row">
    <nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/idols">所有偶像</router-link></li>
        <li class="breadcrumb-item active" aria-current="page">{{ shown.info.name }}</li>
      </ol>
    </nav>
  </div>
  <div id="info" class="card mb-3" style="max-width: 450px">
    <div class="row g-0">
      <div class="col-md-4">
        <img :src="shown.info.img_url" />
      </div>
      <div class="col-md-8">
        <div class="card-body">
          <div class="row">
            <div class="col"><b>姓名</b> {{ shown.info.name }} (CV: {{ shown.info.CV }})</div>
          </div>
          <div class="row">
            <div class="col"><b>陣營</b> {{ shown.info.idol_type }}</div>
          </div>
          <div class="row">
            <div class="col"><b>年齡</b> {{ shown.info.age }}</div>
          </div>
          <div class="row">
            <div class="col"><b>身高</b> {{ shown.info.height }}</div>
          </div>
          <div class="row">
            <div class="col"><b>體重</b> {{ shown.info.weight }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <ul class="nav nav-tabs">
    <li class="nav-item"><a class="nav-link active" href="#">卡片</a></li>
  </ul>
  <table id="cards" class="table align-middle">
    <tbody>
      <tr v-for="card in shown.cards" :key="card.name">
        <td><router-link :to="card.url">
            <CardIcon class="me-2" :card="fixCard(card)" />{{ card.name }}
          </router-link></td>
        <td>{{ card.time }}</td>
      </tr>
    </tbody>
  </table>
</MainPage>
</template>

<script>
import CardIcon from './CardIcon.vue'
import MainPage from './MainPage.vue'
import { deleteNull, toDate, toDateString } from '../general'

function getDefaultIdol() {
    return {
        info: {
            name: '不明',
            idol_type: '不明',
            age: '不明',
            height: '不明',
            weight: '不明',
        },
        cards: [],
    };
}

function fixData(idol, ver) {
    if (!idol) return;

    deleteNull(idol.info);
    idol.info = Object.assign({
        name: '不明',
        idol_type: '不明',
        age: '不明',
        height: '不明',
        weight: '不明'
    }, idol.info);

    for (let i in idol.cards) {
        let card = idol.cards[i];
        deleteNull(card);
        idol.cards[i] = Object.assign({
            id: 0,
            name: '不明',
            rare: -1,
            time: null,
            img_url: '#',
            url: '#'
        }, card);
        idol.cards[i].time = toDateString(toDate(card.time), ver);
    }
}

export default {
    name: 'IdolPage',
    components: {
        CardIcon,
        MainPage,
    },
    inject: ['$api', '$setTitle'],
    props: ['idol_id'],
    data() {
        return {
            idol: [getDefaultIdol(), getDefaultIdol()],
            japanese: true,
            notBoth: false,
        };
    },
    mounted() {
        this.updatePage();
    },
    methods: {
        updatePage: function() {
            this.$api.getIdol(this.idol_id).then((res) => {
                const tmpIdol = res.data;
                for (let i=0; i<tmpIdol.length; ++i) {
                    fixData(tmpIdol[i], i);
                }
                this.idol = tmpIdol;
                this.initialize();
                this.$setTitle(this.shown.info.name);
            });
        },
        initialize: function () {
            if (!this.idol[0] || !this.idol[1]) this.notBoth = true;
            if (!this.idol[0]) this.japanese = false;
        },
        changeLanguage: function () {
            this.japanese = !this.japanese;
        },
        imgStyle(img_url) {
            return {
                backgroundImage: 'url(' + img_url + ')',
            };
        },
        fixCard: function(card) {
            return {...card, idol_type: this.shown.info.idol_type};
        },
    },
    computed: {
        shown: function () {
            return this.japanese ? this.idol[0] : this.idol[1];
        },
        panelWord: function () {
            return this.japanese ? '中文版' : '日文版'
        },
        fltCards() {
            // 保留以便之後寫稀有度 filter
            var self = this;
            var res = self.cards.slice();
            res = res.filter(card => {
                if (self.japanese) {
                    return card['jp_time'];
                } else {
                    return card['as_time'];
                }
            });
            return res;
        }
    },
    watch: {
        idol_id: function() { this.updatePage(); },
    },
};
</script>
