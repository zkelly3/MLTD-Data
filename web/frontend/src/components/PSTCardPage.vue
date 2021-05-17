<template>
  <MainPage :pageNotFound="pageNotFound">
  <template v-slot:navbar>
  <button class="btn btn-outline-light ms-auto" v-on:click="changeLanguage()" :disabled="notBoth">{{ panelWord }}</button>
  </template>

  <div class="row">
  <nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
    <ol class="breadcrumb">
      <li class="breadcrumb-item active" aria-current="page">上下位整理</li>
    </ol>
  </nav>
  </div>

  <div class="row g-1 mb-2 row-cols-xl-4 row-cols-lg-3 row-cols-md-2 row-cols-1">
    <div class="col" v-for="(attr, key) in filters" :key="key"><div class="input-group">
      <div class="input-group-text">
        <input class="form-check-input me-1" type="checkbox" :id="'check-'+key" v-model="attr.enabled" />
        <label class="form-check-label" for="'check-'+key">{{ attr.label }}</label>
      </div>
      <div class="input-group-text form-control" style="backgroundColor: white;" v-if="attr.type === 'check'">
        <div class="form-check me-2" v-for="opt in attr.options" :key="opt.val">
          <input class="form-check-input" type="checkbox" :value="opt.val" :id="'check-'+opt.val" v-model="attr.selected">
          <label class="form-check-label" :for="'check-'+opt.val">
            {{ opt.text }}
          </label>
        </div>
      </div>
    </div></div>
    <div class="col"><div class="input-group h-100">
      <label class="input-group-text">排序依據</label>
      <select class="form-select" v-model="sorts.sortKey">
        <option v-for="attr in sorts.options" :key="attr.val" :value="attr.val">
          {{ attr.text }}
        </option>
      </select>
      <button type="button" class="btn btn-secondary btn-sm" v-on:click="sortReverse()">{{ sortPanelWord }}</button>
    </div></div>
  </div>

  <table class="table mt-3 align-middle">
    <tbody><tr v-for="(idol, index) in sortCards" :key="idol.id">
      <td><a href="#" v-on:click="changeIdol(index)" data-bs-toggle="modal" data-bs-target="#idolModal">{{ idol.name }}</a></td>
      <td>{{idol.cards.length}}張</td>
      <td v-if="idol.cards && idol.cards.length > 0">{{ showTime(idol.cards[0].time) }}</td><td v-else></td>
      <td v-if="idol.cards && idol.cards.length > 0"><router-link :to="idol.cards[0].url" :title="idol.cards[0].event_name"><CardIcon class="me-2" :card="fixCard(idol.cards[0])"/>{{ idol.cards[0].name }}</router-link></td><td v-else></td>
    </tr></tbody>
  </table>

  <div class="modal fade" id="idolModal" tabindex="-1" aria-labelledby="idolModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="exampleModalLabel">所有上/下位卡片</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <PSTModal :cards="modalCards" :japanese="japanese"/>
        </div>
      </div>
    </div>
  </div>
  </MainPage>
</template>

<script>
import MainPage from './MainPage.vue'
import CardIcon from './CardIcon.vue'
import PSTModal from './PSTModal.vue'
import { toDate, toDateString } from '../general'

function fixData(idols) {
  for (let i in idols) {
    let idol = idols[i];
    for (let j in idol.cards) {
      let card = idol.cards[j];
      card.name = (!card.name) ? '未知' : card.name;
    }
  }
}

export default {
    name: 'PSTCardPage',
    components: {
        MainPage,
        CardIcon,
        PSTModal,
    },
    inject: ['$api'],
    props: [],
    data() {
        return {
            idols: [[], []],
            japanese: true,
            notBoth: false,
            pageNotFound: false,
            filters: {
                'cardType': {
                    'type': 'check',
                    'label': '卡片類型',
                    'enabled': true,
                    'options': [{'val': 0, 'text': '上位'}, {'val': 1, 'text': '下位'}],
                    'selected': [],
                },
            },
            sorts: {
                reverse: false,
                sortKey: '',
                options: [{'val': '', 'text': '預設'},
                    {'val': 'time', 'text': '最近實裝時間'},
                    {'val': 'count', 'text': '張數'},
                ],
            },
            currentIdol: 0,
        };
    },
    mounted() {
        this.updatePage();
    },
    methods: {
        updatePage: function() {
            this.$api.getIdolPSTCards().then((res) => {
                const tmpData = res.data;
                for (let i=0; i<tmpData.length; ++i) {
                    fixData(tmpData[i]);
                }
                this.idols = tmpData;
                if (!this.idols[0] || !this.idols[1]) this.notBoth = true;
                if (!this.idols[0]) this.japanese = false;
            });
        },
        changeLanguage: function() {
            this.japanese = !this.japanese;
        },
        shownOptions: function(options) {
            return this.japanese ? options[0] : options[1];
        },
        showTime(time) {
            return this.japanese ? toDateString(toDate(time), 0) : toDateString(toDate(time), 1);
        },
        fixCard: function(card) {
            return {...card, rare: parseInt(card.rare * 2 + (card.is_awaken ? 1 : 0))};
        },
        sortReverse() {
            this.sorts.reverse = !this.sorts.reverse;
        },
        changeIdol(index) {
            this.currentIdol = index;
        }
    },
    computed: {
        shown() {
            return this.japanese ? this.idols[0] : this.idols[1];
        },
        fltCards() {
            var self = this;
            var res = self.shown.slice();
            for (let key in self.filters) {
                let attr = self.filters[key]
                if (attr.enabled) {
                    if (attr.type === 'check') {
                        for (let i in res) {
                            let idol = Object.assign({}, res[i]);
                            idol.cards = idol.cards.filter(card => {
                                return attr.selected.length == 0 || attr.selected.includes(card.card_type);
                            });
                            res[i] = idol;
                        }
                    }
                }
            }
            return res;
        },
        sortCards() {
            var self = this;
            var res = self.fltCards.slice();
            
            return res.sort(function(a, b) {
                let key = self.sorts.sortKey;
                let reverse = self.sorts.reverse;
                let r = reverse ? -1 : 1;
                if (key === '') return (a.id > b.id) ?
                    (1 * r) : (a.id < b.id) ?
                    (-1 * r) : 0;
                else if (key === 'count') return (a.cards.length > b.cards.length) ? 
                    (1 * r) : (a.cards.length < b.cards.length) ?
                    (-1 * r) : (a.id > b.id) ?
                    (1 * r) : (a.id < b.id) ?
                    (-1 * r) : 0;
                else if (key === 'time') {
                    if (a.cards.length == 0 && b.cards.length == 0) return (a.id > b.id) ? (1 * r) : (a.id < b.id) ? (-1 * r) : 0;
                    if (a.cards.length == 0) return -1 * r;
                    if (b.cards.length == 0) return 1 * r;

                    let ak = a.cards[0][key];
                    let bk = b.cards[0][key];
                    return (ak > bk) ?
                        (1 * r) : (ak < bk) ?
                        (-1 * r) : (a.id > b.id) ?
                        (1 * r) : (a.id < b.id) ?
                        (-1 * r) : 0;
                }
                else return true;
            });
        },
        panelWord() {
            return this.japanese ? '中文版' : '日文版'
        },
        sortPanelWord() {
            return this.sorts.reverse && this.japanese ? '昇順' : this.sorts.reverse ? '遞增' : this.japanese ? '降順' : '遞減';
        },
        modalCards() {
          if (this.sortCards.length == 0) return [];
          return this.sortCards[this.currentIdol].cards;
        }
    },
    watch: {
    }
}
</script>
