<template>
<MainPage>
    <template v-slot:navbar>
    <button class="btn btn-outline-light ms-auto" v-on:click="changeLanguage()" :disabled="notBoth">{{ panelWord }}</button>
    </template>

    <div class="row">
    <nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
    <ol class="breadcrumb">
        <li class="breadcrumb-item active" aria-current="page">所有卡池</li>
    </ol>
    </nav>
    </div>
    <div class="row g-1 mb-2" v-for="(attr, key) in filters" :key="key">
    <div class="col"><div class="input-group">
        <div class="input-group-text">
            <input class="form-check-input me-1" type="checkbox" :id="'check-'+key" v-model="attr.enabled" />
            <label class="form-check-label" for="'check-'+key">{{ attr.label }}</label>
        </div>
        <input class="form-control" type="text" v-if="attr.type === 'search'" v-model="attr.value" placeholder="請輸入卡池名稱"/>
        <div class="input-group-text" style="backgroundColor: white;" v-if="attr.type === 'check'">
            <div class="form-check me-2" v-for="opt in shownOptions(attr.options)" :key="opt.val">
            <input class="form-check-input" type="checkbox" :value="opt.val" :id="'check-'+opt.val" v-model="attr.selected">
            <label class="form-check-label" :for="'check-'+opt.val">
                {{ opt.text }}
            </label>
            </div>
        </div>
    </div></div>
    </div>
    <table class="table mt-3 align-middle" id="gasha">
    <tbody><tr v-for="gasha in pageFltGashas" :key="gasha.start">
        <td><router-link :to="gasha.url">{{ gasha.name }}</router-link></td>
        <td>{{ gasha.start }}</td>
        <td>{{ gasha.over }}</td>
    </tr></tbody>
    </table>
    <Pagination :list="fltGashas" :purPageInit=20 :currentInit=1 @filtered_list="val => { pageFltGashas = val; }"/>
</MainPage>
</template>

<script>
import MainPage from './MainPage.vue'
import Pagination from './Pagination'
import { toDate, toDateString } from '../general'

function fixData(gashas, ver) {
    for (let i in gashas) {
        gashas[i].name = (!gashas[i].name) ? '不明' : gashas[i].name;
        gashas[i].start = toDateString(toDate(gashas[i].start), ver);
        gashas[i].over = toDateString(toDate(gashas[i].over), ver);
    }    
}

export default {
    name: 'GashasPage',
    components: {
        MainPage,
        Pagination,
    },
    inject: ['$api'],
    props: [],
    data() {
        return {
            gashas: [[], []],
            japanese: true,
            notBoth: false,
            filters: {
                'gashaType': {
                    'type': 'check',
                    'label': '卡池類型',
                    'enabled': true,
                    'options': [[], []],
                    'selected': [],
                },
                'gashaName': {
                    'type': 'search',
                    'label': '搜尋',
                    'enabled': true,
                    'value': '',
                }
            },
            pageFltGashas: [],
        };
    },
    mounted() {
        this.updatePage();
    },
    methods: {
        updatePage: function() {
            this.$api.getGashaTypes().then((res) => {
                this.filters.gashaType.options = res.data;
                
                for (let i in this.filters.gashaType.options[0]) {
                    let val = this.filters.gashaType.options[0][i].val;
                    if (val !== 'SPC') this.filters.gashaType.selected.push(val);
                }
            });
            this.$api.getGashas().then((res) => {
                const tmpGashas = res.data;
                for (let i=0; i<tmpGashas.length; ++i) {
                    fixData(tmpGashas[i], i);
                }
                this.gashas = tmpGashas;
                if (!this.gashas[0] || !this.gashas[1]) this.notBoth = true;
                if (!this.gashas[0]) this.japanese = false;
            });
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
            return this.japanese ? this.gashas[0] : this.gashas[1];
        },
        fltGashas() {
            var self = this;
            var res = self.shown.slice();
            for (let key in self.filters) {
                let attr = self.filters[key]
                if (attr.enabled) {
                    if (attr.type === 'check') {
                        res = res.filter(gasha => {
                            return attr.selected.includes(gasha.gasha_abbr);
                        });
                    }
                    else if (attr.type === 'search') {
                        res = res.filter(gasha => {
                            return attr.value === '' || gasha.name.toLowerCase().includes(attr.value.toLowerCase());
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
