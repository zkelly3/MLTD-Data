<template>
<MainPage :pageNotFound="pageNotFound">
  <template v-slot:navbar>
  <button class="btn btn-outline-light ms-auto" v-on:click="changeLanguage()" :disabled="notBoth">{{ panelWord }}</button>
  </template>

  <div class="row">
  <nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
    <ol class="breadcrumb">
      <li class="breadcrumb-item"><router-link to="/events">所有活動</router-link></li>
      <li class="breadcrumb-item active" aria-current="page">{{ shown.name }}</li>
    </ol>
  </nav>
  </div>
  <div class="row"><div class="col">
    <table class="table align-middle" id="event"><tbody>
      <tr class="text-center"><td colspan="2"><img class="img-fluid event_image" :src="shown.img_url || defaultEvent" v-on:error="replaceByDefault"/></td></tr>
      <tr><th>名稱</th><td>{{ shown.name }}</td></tr>
      <tr><th>開始時間</th><td>{{ shown.start }}</td></tr>
      <tr><th>結束時間</th><td>{{ shown.over }}</td></tr>
      <tr v-if="shown.event_abbr == 'PST'"><th>上位 (排名報酬) 卡</th><td>
        <div class="row gy-2 row-cols-1">
          <div class="col" v-for="card in shown.cards['0']" :key="card.name">
            <router-link :to="card.url">
              <CardIcon class="me-2" :card="card" />{{ card.name }}
            </router-link>
          </div>
        </div>
      </td></tr>
      <tr v-if="shown.event_abbr == 'PST'"><th>下位 (累積報酬) 卡</th><td>
        <div class="row gy-2 row-cols-1">
          <div class="col" v-for="card in shown.cards['1']" :key="card.name">
            <router-link :to="card.url">
              <CardIcon class="me-2" :card="card" />{{ card.name }}
            </router-link>
          </div>
        </div>
      </td></tr>
      <tr v-if="shown.event_abbr == 'PST'"><th>其他報酬卡</th><td>
        <div class="row gy-2 row-cols-1">
          <div class="col" v-for="card in shown.cards['2']" :key="card.name">
            <router-link :to="card.url">
              <CardIcon class="me-2" :card="card" />{{ card.name }}
            </router-link>
          </div>
        </div>
      </td></tr>
      <tr v-if="shown.event_abbr == 'COL'"><th>累積報酬卡</th><td>
        <div class="row gy-2 row-cols-1">
          <div class="col" v-for="card in shown.cards" :key="card.name">
            <router-link :to="card.url">
              <CardIcon class="me-2" :card="card" />{{ card.name }}
            </router-link>
          </div>
        </div>
      </td></tr>
      <tr v-if="shown.event_abbr == 'OTH'"><th>活動報酬卡</th><td>
        <div class="row gy-2 row-cols-1">
          <div class="col" v-for="card in shown.cards" :key="card.name">
            <router-link :to="card.url">
              <CardIcon class="me-2" :card="card" />{{ card.name }}
            </router-link>
          </div>
        </div>
      </td></tr>
      <tr v-if="shown.has_song"><th>活動相關樂曲</th><td>
        <div class="row gy-2 row-cols-1">
          <div class="col" v-for="song in shown.songs" :key="song.name">
            <router-link :to="song.url">
            <img class="song_icon me-2" :src="song.img_url"/>{{ song.name }}</router-link>
          </div>
        </div>
      </td></tr>
      <tr><th>備註</th><td>{{ shown.comment }}</td></tr>
    </tbody></table>
    <div v-if="shown.event_abbr == 'ANN'">
      <h4>每日任務報酬</h4>
      <table class="table align-middle" id="event"><tbody>
        <tr v-for="(val, key) in shown.cards" :key="key">
          <th>{{ val.mission_date }}</th><td v-for="card in val.data" :key="card.name">
          <router-link :to="card.url" :title="card.name">
            <CardIcon class="me-2" :card="card" />{{ card.idol_name }}
          </router-link>
          </td>
        </tr>
      </tbody></table>
    </div>
  </div></div>
</MainPage>
</template>

<script>
import CardIcon from './CardIcon.vue'
import MainPage from './MainPage.vue'
import { toDate, toDateString, toDateTimeString } from '../general'

function getDefaultEvent() {
    return {
        name: '不明',
        start: null,
        over: null,
    }
}

function fixData(gameEvent, ver) {
    if (!gameEvent) return;
    
    gameEvent.name = (!gameEvent.name) ? '不明' : gameEvent.name;
    gameEvent.startTime = toDate(gameEvent.start);
    gameEvent.start = toDateTimeString(gameEvent.startTime, ver);
    gameEvent.over = toDateTimeString(toDate(gameEvent.over), ver);
    
    if (gameEvent.cards !== null && Array.isArray(gameEvent.cards)) {
        for (let i in gameEvent.cards) {
            let card = gameEvent.cards[i];
            card.name = (!card.name) ? '不明' : card.name;
        }
    }
    else if (gameEvent.event_abbr == 'ANN') {
        for (let i in gameEvent.cards) {
            for (let j in gameEvent.cards[i].data) {
                let card = gameEvent.cards[i].data[j];
                card.name = (!card.name) ? '不明' : card.name;
            }
        }
    }
    else if (gameEvent.cards !== null) {
        for (let i in gameEvent.cards) {
            for (let j in gameEvent.cards[i]) {
                let card = gameEvent.cards[i][j];
                card.name = (!card.name) ? '不明' : card.name;
            }
        }
    }
    
    if (gameEvent.event_abbr === 'ANN') {
        for (let i in gameEvent.cards) {
            gameEvent.cards[i].mission_date = toDateString(toDate(gameEvent.cards[i].mission_date), ver);
        }
    }
}

export default {
    name: 'EventPage',
    components: {
        CardIcon,
        MainPage,
    },
    inject: ['$api', '$setTitle'],
    props: ['event_id'],
    data() {
        return {
            gameEvent: [getDefaultEvent(), getDefaultEvent()],
            japanese: true,
            notBoth: false,
            defaultEvent: '/static/images/default/no_event_banner.jpg',
            pageNotFound: false,
        };
    },
    mounted() {
        this.updatePage();
    },
    methods: {
        updatePage: function() {
            this.$api.getEvent(this.event_id).then((res) => {
                const tmpEvent = res.data;
                for (let i=0; i<tmpEvent.length; ++i) {
                    fixData(tmpEvent[i], i);
                }
                this.gameEvent = tmpEvent;
                this.initialize();
                this.$setTitle(this.shown.name);
            }).catch((err) => {
                if (err.response && err.response.status === 404) {
                    this.pageNotFound = true;
                }
            });
        },
        initialize: function() {
            if (!this.gameEvent[0] || !this.gameEvent[1]) this.notBoth = true;
            if (!this.gameEvent[0]) this.japanese = false;
        },
        changeLanguage: function() {
            this.japanese = !this.japanese;
        },
        replaceByDefault(e) {
          e.target.src = '/static/images/default/no_event_banner.jpg';
        }
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
        'event_type': function() { this.updatePage(); },
        'event_id': function() { this.updatePage(); },
    }
}
</script>

<style>
.event_image {
  max-height: 250px;
}
.song_icon {
  height: 50px;
}
</style>
