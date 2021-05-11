<template>
<MainPage :pageNotFound="pageNotFound">
    <template v-slot:navbar>
    <button class="btn btn-outline-light ms-auto" v-on:click="changeLanguage()" :disabled="notBoth">{{ panelWord }}</button>
    </template>

    <div class="row">
    <nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
    <ol class="breadcrumb">
        <li class="breadcrumb-item active" aria-current="page">所有活動</li>
    </ol>
    </nav>
    </div>
    <div class="row g-1">
    <div class="col-lg-4" v-for="(attr, key) in filters" :key="key"><div class="input-group">
        <div class="input-group-text">
            <input class="form-check-input me-1" type="checkbox" :id="'check-'+key" v-model="attr.enabled" />
            <label class="form-check-label" for="'check-'+key">{{ attr.label }}</label>
        </div>
        <input class="form-control" type="text" v-if="attr.type === 'search'" v-model="attr.value" placeholder="請輸入活動名稱"/>
        <select class="form-select" v-model="attr.selected" v-if="attr.type === 'option'">
            <option value="" disabled>選擇活動類型</option>
            <option v-for="opt in shownOptions(attr.options)" :key="opt.val" :value="opt.val">{{ opt.text }}</option>
        </select>
    </div></div>
    </div>
    <table class="table mt-3 align-middle" id="event">
    <tbody><tr v-for="event in pageFltEvents" :key="event.url">
        <td><router-link :to="event.url">{{ event.name }}</router-link></td>
        <td>{{ event.start }}</td>
        <td>{{ event.over }}</td>
    </tr></tbody>
    </table>
    <Pagination :list="fltEvents" :purPageInit=20 :currentInit=1 @filtered_list="val => { pageFltEvents = val; }"/>
</MainPage>
</template>

<script>
import MainPage from './MainPage.vue'
import Pagination from './Pagination'
import { toDate, toDateString } from '../general'

function fixData(events, ver) {
    for (let i in events) {
        events[i].name = (!events[i].name) ? '不明' : events[i].name;
        events[i].start = toDateString(toDate(events[i].start), ver);
        events[i].over = toDateString(toDate(events[i].over), ver);
    }    
}

export default {
    name: 'EventsPage',
    components: {
        MainPage,
        Pagination,
    },
    inject: ['$api'],
    props: [],
    data() {
        return {
            events: [[], []],
            japanese: true,
            notBoth: false,
            filters: {
                eventType: {
                    'type': 'option',
                    'label': '活動類型',
                    'enabled': false,
                    'options': [[], []],
                    'selected': '',
                },
                eventName: {
                    'type': 'search',
                    'label': '搜尋',
                    'enabled': true,
                    'value': '',
                }
            },
            pageFltEvents: [],
            pageNotFound: false,
        };
    },
    mounted() {
        this.updatePage();
    },
    methods: {
        updatePage: function() {
            this.$api.getEventTypes().then((res) => {
                this.filters.eventType.options = res.data;
            });
            this.$api.getEvents().then((res) => {
                const tmpEvents = res.data;
                for (let i=0; i<tmpEvents.length; ++i) {
                    fixData(tmpEvents[i], i);
                }
                this.events = tmpEvents;
                this.initialize();
            });
        },
        initialize: function() {
            if (!this.events[0] || !this.events[1]) this.notBoth = true;
            if (!this.events[0]) this.japanese = false;
        },
        changeLanguage: function() {
            this.japanese = !this.japanese;
        },
        shownOptions: function(options) {
            return this.japanese ? options[0] : options[1];
        },
    },
    computed: {
        shown() {
            return this.japanese ? this.events[0] : this.events[1];
        },
        fltEvents() {
            var self = this;
            var res = self.shown.slice();
            for (let key in self.filters) {
              let attr = self.filters[key]
              if (attr.enabled) {
                if (attr.type === 'option') {
                    res = res.filter(gameEvent => {
                        return attr.selected === '' || gameEvent.event_abbr === attr.selected;
                    });
                }
                else if (attr.type === 'search') {
                    res = res.filter(gameEvent => {
                        return attr.value === '' || gameEvent.name.toLowerCase().includes(attr.value.toLowerCase());
                    });
                }
              }
            }
            return res;
        },
        panelWord() {
            return this.japanese ? '中文版' : '日文版'
        },
    },
    watch: {
    }
}
</script>
