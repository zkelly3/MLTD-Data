<template>
<MainPage>
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
    <tbody><tr v-for="event in pageFltEvents" :key="event.start">
        <td><a :href="event.url">{{ event.name }}</a></td>
        <td>{{ event.start }}</td>
        <td>{{ event.over }}</td>
    </tr></tbody>
    </table>
    <div class="row g-1">
    <div class="col-lg-2">
        <select class="form-select" v-model.number="paging.purPage">
        <option v-for="opt in paging.onePageList" :key="opt" :value="opt">{{ opt }}</option>
        </select>
    </div>
    <nav aria-label="event_pagination">
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
    name: 'EventsPage',
    components: {
        MainPage,
    },
    props: ['events_json', 'types_json'],
    data() {
        return {
            events: this.events_json,
            japanese: true,
            notBoth: false,
            filters: {
                eventType: {
                    'type': 'option',
                    'label': '活動類型',
                    'enabled': false,
                    'options': this.types_json,
                    'selected': '',
                },
                eventName: {
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
            if (!this.events[0] || !this.events[1]) this.notBoth = true;
            if (!this.events[0]) this.japanese = false;
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
        pageFltEvents() {
            var self = this;
            var res = self.fltEvents.slice();
            var first = (self.paging.current-1) * (self.paging.purPage);
            var last = (self.paging.current) * (self.paging.purPage);
            res = res.filter((gameEvent, index) => {
                return (index >= first) && (index < last);
            });
            return res;
        },
        panelWord() {
            return this.japanese ? '中文版' : '日文版'
        },
        totalPage() {
            return parseInt((this.fltEvents.length-1) / this.paging.purPage) + 1
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
        pageFltEvents: function() {
            this.paging.current = Math.min(this.paging.current, this.totalPage);
        }
    }
}
</script>