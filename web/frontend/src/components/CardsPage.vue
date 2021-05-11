<template>
<MainPage :pageNotFound="pageNotFound">
  <template v-slot:navbar>
  <button class="btn btn-outline-light ms-auto" v-on:click="changeLanguage()" :disabled="notBoth">{{ panelWord }}</button>
  </template>

  <div class="row">
<nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
  <ol class="breadcrumb">
    <li class="breadcrumb-item active" aria-current="page">所有卡片</li>
  </ol>
</nav>
</div>
<div class="row g-1">
  <div class="col-2">
    <button type="button" class="btn btn-outline-primary" data-bs-toggle="modal" data-bs-target="#filterModal">篩選條件</button>
  </div>
  <div class="col-4">
    <button type="button" class="btn btn-outline-primary" data-bs-toggle="modal" data-bs-target="#sortModal">排序方式</button>
    <span>依{{ sortText }}排序</span>
  </div>
</div>
<table class="table mt-3 align-middle">
  <tbody><tr v-for="card in pageFltCards" :key="card.name">
    <td><router-link :to="card.url">
      <CardIcon class="me-2" :card="fixCard(card)"/>{{ card.name }}
    </router-link></td>
    <td>{{ showTime(card.time) }}</td>
  </tr></tbody>
</table>
<Pagination :list="sortedCards" :purPageInit=20 :currentInit=1 @filtered_list="val => { pageFltCards = val; }"/> 

<div class="modal fade" id="filterModal" tabindex="-1" aria-labelledby="filterModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="exampleModalLabel">選擇篩選條件</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <div class="row gy-2 row-cols-1" v-for="(attr, key) in shownFilters" :key="key">
          <div class="col">
            <b>{{ attr.label }}</b>
          </div>
          <div class="col" v-if="attr.type === 'check'">
            <div class="form-check me-2 d-inline-block" v-for="opt in attr.options" :key="opt.val">
              <input class="form-check-input" type="checkbox" :value="opt.val" :id="'check-'+opt.val" v-model="attr.selected"/>
              <label class="form-check-label" :for="'check-'+opt.val">
                {{ opt.text }}
              </label>
            </div>
          </div>
          <div class="col" v-if="attr.type === 'idol_check'">
            <div class="row gy-2 row-col-1">
              <div class="col-10">
                <div class="form-check me-2 d-inline-block" v-for="opt in attr.type_options" :key="opt">
                  <input class="form-check-input" type="checkbox" :id="'check-'+opt" :checked="attr.type_selected.includes(opt)" v-on:change="toggleTypeSelected(attr, opt)"/>
                  <label class="form-check-label" :for="'check-'+opt">
                    {{ opt }}
                  </label>
                </div>
              </div>
              <div class="col-10">
              <div class="form-check">
                <input class="form-check-input" type="checkbox" id="check-one-idol" :checked="attr.idol_enabled" v-on:change="setIdolEnabled(attr, !attr.idol_enabled)"/>
                <label role="button" for="check-one-idol" class="form-select d-inline-block" style="width: auto" data-bs-target="#idolModal" data-bs-toggle="modal" data-bs-dismiss="modal" v-on:click="setIdolEnabled(attr, true)">
                  {{ shownIdols[attr.idol_selected.toString()].name }}
                </label>
              </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<div class="modal fade" id="idolModal" tabindex="-1" aria-labelledby="idolModalLabel" data-bs-backdrop="static" data-bs-keyboard="false" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="exampleModalLabel">偶像列表</h5>
        <button type="button" class="btn-close" data-bs-target="#filterModal" data-bs-toggle="modal" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <div class="row row-cols-lg-6 row-cols-4 gy-2">
          <div class="col" v-for="(idol, key) in shownIdols" :key="key">
              <div class="card">
                <a class="stretched-link" v-on:click="selectIdol(idol.id)" data-bs-target="#filterModal" data-bs-toggle="modal" data-bs-dismiss="modal" href="#">
                  <img :src="idol.img_url" class="card-img-top"/>
                </a>
                <div class="card-body p-1 text-center">{{ idol.name }}</div>
              </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<div class="modal fade" id="sortModal" tabindex="-1" aria-labelledby="sortModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title me-2">選擇排序方式</h5>
        <button type="button" class="btn btn-secondary btn-sm" v-on:click="sortReverse()">{{ sortPanelWord }}</button>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <div class="row g-1">
          <div class="col form-check" v-for="attr in shownSorts" :key="attr.val">
            <input class="form-check-input" type="radio" v-model="sorts.sortKey" :value="attr.val" :id="'radio-'+attr.val">
            <label class="form-check-label" :for="'radio-'+attr.val">
              {{ attr.text }}
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</MainPage>
</template>

<script>
import CardIcon from './CardIcon'
import MainPage from './MainPage.vue'
import Pagination from './Pagination'
import { toDate, toDateString } from '../general'

function getDefaultSorts() {
    return [{
        'val': 'time',
        'text': '',
    }];
}

function getDefaultIdols() {
    return {
        '1': {
            'id': 1,
            'name': '',
        },
    }
}

function fixData(cards) {
    for (let i in cards) {
        cards[i].name = (!cards[i].name) ? '不明' : cards[i].name;
    }    
}

export default {
    name: 'CardsPage',
    components: {
        CardIcon,
        MainPage,
        Pagination,
    },
    inject: ['$api'],
    props: [],
    data() {
        return {
            cards: [[], []],
            japanese: true,
            notBoth: false,
            filters: [{}, {}],
            sorts: {
                sortKey: 'time',
                reverse: true,
                options: [getDefaultSorts(), getDefaultSorts()],
            },
            idols: [getDefaultIdols(), getDefaultIdols()],
            pageFltCards: [],
            pageNotFound: false,
        };
    },
    mounted() {
        this.updatePage();
    },
    methods: {
        updatePage: function() {
            this.$api.getCardFilters().then((res) => {
                this.filters = res.data;
            });
            this.$api.getCardSorts().then((res) => {
                this.sorts.options = res.data;
            });
            this.$api.getCardIdols().then((res) => {
                this.idols = res.data;
            });
            this.$api.getCards().then((res) => {
                const tmpCards = res.data;
                for (let i=0; i<tmpCards.length; ++i) {
                    fixData(tmpCards[i]);
                }
                this.cards = tmpCards;
                this.initialize();
            });
        },
        initialize: function() {
            if (!this.cards[0] || !this.cards[1]) this.notBoth = true;
            if (!this.cards[0]) this.japanese = false;
        },
        changeLanguage: function() {
            this.japanese = !this.japanese;
        },
        shownOptions: function(options) {
            return this.japanese ? options[0] : options[1];
        },
        idolClass(idol) {
            switch (idol.idol_type) {
                case 'Princess':
                    return 'idol_pr'
                case 'Fairy':
                    return 'idol_fa'
                case 'Angel':
                    return 'idol_an'
                case 'Guest':
                    return 'idol_gu'
            }
        },
        selectIdol(idol_id) {
            this.shownFilters.belong.idol_selected = idol_id
        },
        setIdolEnabled(filter, enabled) {
            filter.idol_enabled = enabled;
            if (filter.idol_enabled) {
                filter.type_selected.splice(0);
            }
        },
        toggleTypeSelected(filter, opt) {
            const index = filter.type_selected.indexOf(opt);
            if (index !== -1) {
                filter.type_selected.splice(index, 1);
            } else {
                filter.idol_enabled = false;
                filter.type_selected.push(opt);
            }
        },
        sortReverse() {
            this.sorts.reverse = !this.sorts.reverse;
        },
        showTime(time) {
            return this.japanese ? toDateString(toDate(time), 0) : toDateString(toDate(time), 1);
        },
        fixCard: function(card) {
            return {...card, rare: parseInt(card.rare * 2 + (card.is_awaken ? 1 : 0))};
        },
    },
    computed: {
        shown() {
            return this.japanese ? this.cards[0] : this.cards[1];
        },
        shownFilters() {
            return this.japanese ? this.filters[0] : this.filters[1];
        },
        shownSorts() {
            return this.japanese ? this.sorts.options[0] : this.sorts.options[1];
        },
        sortText() {
            for (let i in this.shownSorts) {
                if (this.shownSorts[i].val === this.sorts.sortKey) {
                    return this.shownSorts[i].text;
                }
            }
            return '';
        },
        shownIdols() {
            return this.japanese ? this.idols[0] : this.idols[1];
        },
        fltCards() {
            var self = this;
            var res = self.shown.slice();
            
            for (let key in self.shownFilters) {
                let attr = self.shownFilters[key];
                if (attr.type === 'check') {
                    res = res.filter(card => {
                        return !attr.selected.length || attr.selected.includes(card[attr.key]);
                    });
                }
                else if (attr.type === 'idol_check') {
                    if (attr.idol_enabled) {
                        res = res.filter(card => {
                            return attr.idol_selected === card[attr.idol_key];
                        });
                    }
                    else {
                        res = res.filter(card => {
                            return !attr.type_selected.length || attr.type_selected.includes(card[attr.type_key]);
                        });
                    }
                }
                else if (attr.type === 'search') {
                    res = res.filter(gameEvent => {
                        return attr.value === '' || gameEvent.name.toLowerCase().includes(attr.value.toLowerCase());
                    });
                }
            }
            
            return res;
        },
        sortedCards() {
            var self = this;
            var res = self.fltCards.slice();
            
            if (self.sorts.sortKey === '') return res;
            return res.sort(function(a, b) {
                let key = self.sorts.sortKey;
                let reverse = self.sorts.reverse;
                
                let ak = a[key];
                let bk = b[key];
                let r = reverse ? -1 : 1;
                return ((ak > bk) ? (1 * r) : (ak < bk) ? (-1 * r) : (a.fake_id > b.fake_id) ? (1 * r) : (a.fake_id < b.fake_id) ? (-1 * r) : 0); 
            });
        },
        panelWord() {
            return this.japanese ? '中文版' : '日文版'
        },
        sortPanelWord() {
            return this.sorts.reverse && this.japanese ? '昇順' : this.sorts.reverse ? '遞增' : this.japanese ? '降順' : '遞減';
        },
    },
    watch: {
    }
}
</script>
