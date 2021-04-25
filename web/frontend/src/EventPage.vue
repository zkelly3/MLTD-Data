<template>
<MainPage>
<template v-slot:navbar>
<button class="btn btn-outline-light ms-auto" v-on:click="changeLanguage()" :disabled="notBoth">{{ panelWord }}</button>
</template>

<div class="row">
<nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/events">所有活動</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ shown.name }}</li>
  </ol>
</nav>
</div>
<div class="row"><div class="col">
  <table class="table align-middle" id="event"><tbody>
    <tr class="text-center"><td colspan="2"><img class="img-fluid event_image" :src="shown.img_url || defaultEvent" onerror="standby(this)"/></td></tr>
    <tr><th>名稱</th><td>{{ shown.name }}</td></tr>
    <tr><th>開始時間</th><td>{{ shown.start }}</td></tr>
    <tr><th>結束時間</th><td>{{ shown.over }}</td></tr>
    <tr v-if="shown.event_abbr == 'PST'"><th>上位 (排名報酬) 卡</th><td>
      <div class="row gy-2 row-cols-1">
        <div class="col" v-for="card in shown.cards['0']" :key="card.name">
          <a :href="card.url">
            <div class="card_icon me-2" :class="cardClass(card)">
              <img :src="card.img_url"/>
            </div>{{ card.name }}
          </a>
        </div>
      </div>
    </td></tr>
    <tr v-if="shown.event_abbr == 'PST'"><th>下位 (累積報酬) 卡</th><td>
      <div class="row gy-2 row-cols-1">
        <div class="col" v-for="card in shown.cards['1']" :key="card.name">
          <a :href="card.url">
            <div class="card_icon me-2" :class="cardClass(card)">
              <img :src="card.img_url"/>
            </div>{{ card.name }}
          </a>
        </div>
      </div>
    </td></tr>
    <tr v-if="shown.event_abbr == 'PST'"><th>其他報酬卡</th><td>
      <div class="row gy-2 row-cols-1">
        <div class="col" v-for="card in shown.cards['2']" :key="card.name">
          <a :href="card.url">
            <div class="card_icon me-2" :class="cardClass(card)">
              <img :src="card.img_url"/>
            </div>{{ card.name }}
          </a>
        </div>
      </div>
    </td></tr>
    <tr v-if="shown.event_abbr == 'COL'"><th>累積報酬卡</th><td>
      <div class="row gy-2 row-cols-1">
        <div class="col" v-for="card in shown.cards" :key="card.name">
          <a :href="card.url">
            <div class="card_icon me-2" :class="cardClass(card)">
              <img :src="card.img_url"/>
            </div>{{ card.name }}
          </a>
        </div>
      </div>
    </td></tr>
    <tr v-if="shown.event_abbr == 'OTH'"><th>活動報酬卡</th><td>
      <div class="row gy-2 row-cols-1">
        <div class="col" v-for="card in shown.cards" :key="card.name">
          <a :href="card.url">
            <div class="card_icon me-2" :class="cardClass(card)">
              <img :src="card.img_url"/>
            </div>{{ card.name }}
          </a>
        </div>
      </div>
    </td></tr>
    <tr><th>備註</th><td>{{ shown.comment }}</td></tr>
  </tbody></table>
  <div v-if="shown.event_abbr == 'ANN'">
    <h4>每日任務報酬</h4>
    <table class="table align-middle" id="event">
      <tr v-for="(val, key) in shown.cards" :key="key">
        <th>{{ val.mission_date }}</th><td v-for="card in val.data" :key="card.name">
        <a :href="card.url" :title="card.name">
          <div class="card_icon me-2" :class="cardClass(card)">
            <img :src="card.img_url"/>
          </div>{{ card.idol_name }}
        </a>
        </td>
      </tr>
    </table>
  </div>
</div></div>
</MainPage>
</template>

<script>
import MainPage from './components/MainPage.vue'

export default {
    name: 'EventPage',
    components: {
        MainPage,
    },
    props: ['event_json'],
    data() {
        return {
            gameEvent: this.event_json,
            japanese: true,
            notBoth: false,
            defaultEvent: '/static/images/default/no_event_banner.jpg'
        };
    },
    created: function() {
        this.initialize();
    },
    methods: {
        initialize: function() {
            if (!this.gameEvent[0] || !this.gameEvent[1]) this.notBoth = true;
            if (!this.gameEvent[0]) this.japanese = false;
        },
        changeLanguage: function() {
            this.japanese = !this.japanese;
        },
        cardClass(card) {
            var rare = parseInt(card.rare / 2);
            switch (rare) {
                case 3:
                    return 'card_ssr';
                case 2:
                    return 'card_sr';
                case 1:
                    return 'card_r';
            }
            if (rare == 0) {
                switch (card.idol_type) {
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
            return this.japanese ? this.gameEvent[0] : this.gameEvent[1];
        },
        panelWord: function() {
            return this.japanese ? '中文版' : '日文版'
        }
    },
    watch: {
    }
}
</script>

<style>
.event_image {
  max-height: 250px;
}
</style>