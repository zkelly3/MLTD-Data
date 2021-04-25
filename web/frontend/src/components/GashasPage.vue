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
        <td><a :href="gasha.url">{{ gasha.name }}</a></td>
        <td>{{ gasha.start }}</td>
        <td>{{ gasha.over }}</td>
    </tr></tbody>
    </table>
    <div class="row g-1">
    <div class="col-lg-2">
        <select class="form-select" v-model.number="paging.purPage">
        <option v-for="opt in paging.onePageList" :value="opt" :key="opt">{{ opt }}</option>
        </select>
    </div>
    <nav aria-label="gasha_pagination">
        <ul class="pagination justify-content-end">
        <li :class="{'page-item': true, disabled: calcPagination.noPrev}">
            <a class="page-link" href="#" v-on:click="prevPage()" :aria-disabled="calcPagination.noPrev">Previous</a>
        </li>
        <li v-for="page in calcPagination.pages" :key="page.val" :class="{'page-item': true, active: page.isCurrent}">
            <span class="page-link" v-if="page.isCurrent">{{ page.val }}</span>
            <a class="page-link" href="#" v-on:click="changePage(page.val)" v-else>{{ page.val }}</a>
        </li>
        <li :class="{'page-item': true, disabled: calcPagination.noNext}">
            <a class="page-link" href="#" v-on:click="nextPage()" :aria-disabled="calcPagination.noNext">Next</a>
        </li>
        </ul>
    </nav>
    </div>
</MainPage>
</template>

<script>
import MainPage from './MainPage.vue'

export default {
    name: 'GashasPage',
    components: {
        MainPage,
    },
    props: ['gashas_json', 'types_json'],
    data() {
        return {
            gashas: this.gashas_json,
            japanese: true,
            notBoth: false,
            filters: {
                'gashaType': {
                    'type': 'check',
                    'label': '卡池類型',
                    'enabled': true,
                    'options': this.types_json,
                    'selected': [],
                },
                'gashaName': {
                    'type': 'search',
                    'label': '搜尋',
                    'enabled': true,
                    'value': '',
                }
            },
            paging: {
                onePageList: [10, 20, 50, 100],
                purPage: 20,
                current: 1
            }
        };
    },
    created: function() {
        this.initialize();
    },
    methods: {
        initialize: function() {
            if (!this.gashas[0] || !this.gashas[1]) this.notBoth = true;
            if (!this.gashas[0]) this.japanese = false;
            
            for (let i in this.filters.gashaType.options[0]) {
                let val = this.filters.gashaType.options[0][i].val;
                if (val !== 'SPC') this.filters.gashaType.selected.push(val);
            }
        },
        changeLanguage: function() {
            this.japanese = !this.japanese;
        },
        shownOptions: function(options) {
            return this.japanese ? options[0] : options[1];
        },
        changePage(page) {
            this.paging.current = page;
        }, 
        prevPage() {
            this.changePage(this.paging.current-1);
        },
        nextPage() {
            this.changePage(this.paging.current+1);
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
        pageFltGashas() {
            var self = this;
            var res = self.fltGashas.slice();
            var first = (self.paging.current-1) * (self.paging.purPage);
            var last = (self.paging.current) * (self.paging.purPage);
            res = res.filter((gasha, index) => {
                return (index >= first) && (index < last);
            });
            return res;
        },
        panelWord() {
            return this.japanese ? '中文版' : '日文版'
        },
        totalPage() {
            return parseInt((this.fltGashas.length-1) / this.paging.purPage) + 1
        },
        calcPagination() {
            var res = {};
            var last = this.totalPage;
            var first = 1;
            
            res.noPrev = (this.paging.current) === first;
            res.noNext = (this.paging.current) === last;
            
            res.pages = [];
            if (this.totalPage <= 5) {
                for (let i=1; i<= this.totalPage; i++) {
                    res.pages.push({
                        'val': i,
                        'isCurrent': (i === this.paging.current), 
                    });
                }
            }
            else if (this.paging.current <= 3) {
                for (let i=1; i<=5; i++) {
                    res.pages.push({
                        'val': i,
                        'isCurrent': (i === this.paging.current), 
                    });
                }
            }
            else if ((this.paging.current+2) > this.totalPage) {
                for (let i=this.totalPage-4; i<=this.totalPage; i++) {
                    res.pages.push({
                        'val': i,
                        'isCurrent': (i === this.paging.current), 
                    });
                }
            }
            else {
                for (let i=this.paging.current-2; i<=this.paging.current+2; i++) {
                    res.pages.push({
                        'val': i,
                        'isCurrent': (i === this.paging.current), 
                    });
                }
            }
            return res;
        }
    },
    watch: {
        pageFltGashas: function() {
            this.paging.current = Math.min(this.paging.current, this.totalPage);
        }
    }
}
</script>