<template>
  <MainPage>
  <template v-slot:navbar>
  <button class="btn btn-outline-light ms-auto" v-on:click="changeLanguage()" :disabled="notBoth">{{ panelWord }}</button>
  </template>

  <div class="row">
  <nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
    <ol class="breadcrumb">
      <li class="breadcrumb-item"><a href="/cards">所有卡片</a></li>
      <li class="breadcrumb-item active" aria-current="page">{{ shown.name }}</li>
    </ol>
  </nav>
  </div>
  <div class="row g-0">
    <div class="col-xl-2 col-lg-3 col-12 text-center">
      <img role="button" class="card_image mw-100" :src="shown.img_url" data-bs-toggle="modal" data-bs-target="#cardModal"/>
    </div>
    <div class="col-xl-10 col-lg-9"><div class="container-fluid">
      <MyTr><MyTh :style="styleList">名稱</MyTh><MyTd>{{ shown.name }}</MyTd></MyTr>
      <MyTr><MyTh :style="styleList">所屬偶像</MyTh><MyTd><a :href="shown.idol.url"> {{ shown.idol.name }}</a></MyTd></MyTr>
      <MyTr><MyTh :style="styleList">取得方式</MyTh><MyTd><b>{{ shown.aquire.type }}</b><br><a :href="shown.from_url" v-if="shown.has_from_url">{{ shown.aquire.title }}</a><span v-else>{{ shown.aquire.title }}</span></MyTd></MyTr>
      <MyTr><MyTh :style="styleList">{{ shown.awakenWord }}</MyTh><MyTd v-if="shown.awaken !== null"><a :href="shown.awaken.url">
      <div class="card_icon me-2" :class="cardClass(shown.rare)">
        <img :src="shown.awaken.img_url"/>
      </div>{{ shown.awakenName }}</a>
      </MyTd><MyTd v-else>尚未更新</MyTd></MyTr>
      <MyTr><MyTh :style="styleList">實裝時間</MyTh><MyTd>{{ shown.time }}</MyTd></MyTr>
    </div></div>
  </div>
  <div class="row g-0"><div class="col"><div class="container-fluid">
      <MyTr><MyTh :style="styleList">技能</MyTh><MyTd><b class="align-middle">{{ shown.skill.name }}</b><span class="badge bg-info rounded-pill ms-1 align-middle">{{ shown.skill.type.name }}</span><br>{{ shown.skill.description }}</MyTd></MyTr>
      <MyTr><MyTh :style="styleList">背景敘述</MyTh><MyTd>{{ shown.flavor }}</MyTd></MyTr>
    </div>
  </div></div>
  <div v-if="shown.from == 'Gasha' && shown.gashas.length != 0" class="row"><div class="col">
    <h4>實裝 / Pick Up 的卡池</h4>
    <table id="gashas" class="table"><tbody>
      <th v-for="gashaTitle in gashaTitles" :key="gashaTitle">{{ gashaTitle }}</th>
      <tr v-for="gasha in shown.gashas" :key="gasha.start">
        <td>{{ gasha.gasha_type }}</td>
        <td><a :href="gasha.url">{{ gasha.name }}</a></td>
        <td>{{ gasha.start }}</td>
        <td>{{ gasha.over }}</td>
      </tr>
    </tbody></table>
  </div></div>
  <div v-if="shown.from == 'Event' && shown.event != null" class="row"><div class="col">
    <h4>實裝的活動</h4>
    <table id="event" class="table"><tbody>
      <tr>
        <td>{{ shown.event.event_type }}</td>
        <td><a :href="shown.event.url">{{ shown.event.name }}</a></td>
        <td>{{ shown.event.start }}</td>
        <td>{{ shown.event.over }}</td>
      </tr>
    </tbody></table>
  </div></div>

  <div class="modal fade" id="cardModal" tabindex="-1" aria-labelledby="cardModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-fullscreen" role="document">
      <div id="cardGallery" class="carousel slide" data-bs-ride="carousel">
        <div class="carousel-inner">
          <div class="carousel-item active">
            <img :src="shown.img_url" class="d-block" style="max-height: 100vh; max-width: 100vw; margin: auto">
          </div>
          <div v-if="shown.rare === 6 || shown.rare === 7" class="carousel-item">
            <img :src="shown.big_img_url" class="d-block" style="max-height: 100vh; max-width: 100vw; margin: auto">
          </div>
        </div>
        <a class="carousel-control-prev" style="pointer-events: auto" role="button" href="#cardGallery" data-bs-slide="prev">
          <span class="carousel-control-prev-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Previous</span>
        </a>
        <a class="carousel-control-next" style="pointer-events: auto" role="button" href="#cardGallery" data-bs-slide="next">
          <span class="carousel-control-next-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Next</span>
        </a>
      </div>
    </div>
  </div>
  </MainPage>
</template>

<script>
import { h } from 'vue'
import MainPage from './MainPage.vue'
import { deleteNull, toDate, toDateTimeString } from '../general'

function getDefaultCard() {
    return {
        id: 0,
        name: '不明',
        awaken: null,
        time: null,
        flavor: '尚未更新',
        idol: {
            name: '不明',
            url: '#',
            color: '#ffffff',
            idol_type: '不明'
        },
        aquire: {
            type: '不明',
            title: '尚未更新',
        },
        skill: {
            type: {
                id: 0,
                name: '',
            },
            name: '',
            description: '',
        }
    };
}

function fixData(card, ver) {
    if (!card) return;
    deleteNull(card);
    card = Object.assign({
        id: 0,
        name: '不明',
        awaken: null,
        time: null,
        flavor: '尚未更新'
    }, card);
    
    deleteNull(card.idol);
    card.idol = Object.assign({
        name: '不明',
        url: "#",
        color: '#ffffff',
        idol_type: '不明',
    }, card.idol);
    
    deleteNull(card.aquire);
    card.aquire = Object.assign({
        type: '不明',
        title: '尚未更新',
    }, card.aquire);
    
    if (card.skill) deleteNull(card.skill);
    card.skill = Object.assign({
        type: {
            'id': 0,
            'name': ''
        },
        name: '',
        description: ''
    }, card.skill);
    card.skill.type.name = (!card.skill.type.name) ? '' : card.skill.type.name;
    
    card.awakenWord = card.is_awaken ? '覺醒前' : '覺醒後';
    card.awakenName = (!card.awaken || !card.awaken.name) ? '不明' : card.awaken.name;
    card.time = toDateTimeString(toDate(card.time), ver);
    
    for (let i in card.gashas) {
        let g = card.gashas[i];
        g.start = toDateTimeString(toDate(g.start), ver);
        g.over = toDateTimeString(toDate(g.over), ver);
    }
    
    if (card.event) {
        card.event.start = toDateTimeString(toDate(card.event.start), ver);
        card.event.over = toDateTimeString(toDate(card.event.over), ver);
    }
    return card;
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
    name: 'CardPage',
    components: {
        MainPage,
        MyTr,
        MyTh,
        MyTd,
    },
    inject: ['$api'],
    props: ['card_id'],
    data() {
        return {
            card: [getDefaultCard(), getDefaultCard()],
            japanese: true,
            notBoth: false,
            gashaTitles: ['類型', '名稱', '開始', '結束']
        };
    },
    created: function() {
        this.$api.getCard(this.card_id).then((res)=> {
            const tmpCard = res.data;
            for (let i=0; i<tmpCard.length; ++i) {
                tmpCard[i] = fixData(tmpCard[i], i);
            }
            this.card = tmpCard;
            this.initialize();
        })
    },
    methods: {
        initialize: function() {
            if (!this.card[0] || !this.card[1]) this.notBoth = true;
            if (!this.card[0]) {
                this.japanese = false;
            }
            
        },
        changeLanguage: function() {
            this.japanese = !this.japanese;
        },
        cardClass(rare) {
            rare = parseInt(rare / 2);
            switch (rare) {
                case 3:
                    return 'card_ssr';
                case 2:
                    return 'card_sr';
                case 1:
                    return 'card_r';
            }
            if (rare == 0) {
                switch (this.shown.idol.idol_type) {
                    case 'Princess':
                        return 'card_n_pr';
                    case 'Fairy':
                        return 'card_n_fa';
                    case 'Angel':
                        return 'card_n_an';
                }
            }
            return '';
        },
    },
    computed: {
        shown: function() {
            return this.japanese ? this.card[0] : this.card[1];
        },
        panelWord: function() {
            return this.japanese ? '中文版' : '日文版'
        }, 
        styleList: function() {
            return  {
              'background': this.shown.idol.color + '33'
            };
        }
    },
    watch: {
    }
}
</script>

<style>
.card_image {
  max-height: 250px;
}
</style>
