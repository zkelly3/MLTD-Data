<template>
<MainPage>
    <template v-slot:navbar>
        <button class="btn btn-outline-light ms-auto" v-on:click="changeView()" :disabled="notBoth">
            <i :class="[viewMode == 'table_view' ? 'bi-grid' : 'bi-list']"></i>
        </button>
        <button class="btn btn-outline-light ms-2" v-on:click="changeLanguage()" :disabled="notBoth">{{ panelWord }}</button>
    </template>

    <div class="row">
        <nav aria-label="breadcrumb" style="--bs-breadcrumb-divider: '>';">
            <ol class="breadcrumb">
                <li class="breadcrumb-item active" aria-current="page">所有偶像</li>
            </ol>
        </nav>
    </div>
    <label>篩選</label>
    <div class="row g-1">
        <div class="col-lg-4" v-for="(attr, key) in filters" :key="key">
            <div class="input-group">
                <div class="input-group-text">
                    <input class="form-check-input me-1" type="checkbox" :id="'check-'+key" v-model="attr.enabled" />
                    <label class="form-check-label" for="'check-'+key">{{ attr.label }}</label>
                </div>
                <input class="form-control" type="number" v-model.number="attr.value" min="0" step="1" max="100" />
                <select class="form-select" v-model="attr.direction">
                    <option v-for="opt in diroptions" :key="opt.val" :value="opt.val">{{ opt.text }}</option>
                </select>
            </div>
        </div>
    </div>

    <table class="table mt-3 align-middle" id="idols" v-if="viewMode == 'table_view'">
        <thead class="table-light">
            <tr>
                <th v-for="info in idolinfo" :key="info.val">
                    <a href="#" v-on:click="sortKey(info.val)" :class="{ active: sorts.key === info.val }">{{ info.text }}</a>
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="idol in sortedIdols" :key="idol.name">
                <td><a :href="idol.url"><img class="idol_icon me-2" :src="idol.img_url" />{{ idol.name }}</a></td>
                <td>{{ idol.idol_type }}</td>
                <td>{{ idol.age }}</td>
                <td>{{ idol.height }}</td>
                <td>{{ idol.weight }}</td>
            </tr>
        </tbody>
    </table>

    <div class="row row-cols-lg-6 row-cols-md-4 row-cols-2" v-if="viewMode == 'card_view'">
        <div class="col mt-3" v-for="idol in sortedIdols" :key="idol.name">
            <div class="card">
                <a class="stretched-link" :href="idol.url">
                    <img :src="idol.img_url" class="card-img-top" />
                </a>
                <div class="card-body">

                    <div class="card-title">{{ idol.name }}</div>
                </div>

            </div>
        </div>
    </div>
</MainPage>
</template>

<script>
import MainPage from './MainPage.vue'

function greater_equal(a, b) {
    return a >= b;
}
function less_equal(a, b) {
    return a <= b;
}
function exact(a, b) {
    return a == b;
}

export default {
        name: 'IdolsPage',
    components: {
        MainPage,
    },
    props: ['idols_json'],
        data() {
            return {
                idols: this.idols_json,
                idolinfo: [{'text': '姓名', 'val': 'name'},
                    {'text': '陣營', 'val': 'idol_type'},
                    {'text': '年齡', 'val': 'age'},
                    {'text': '身高', 'val': 'height'},
                    {'text': '體重', 'val': 'weight'}],
                sorts: {
                    'key': '',
                    'reverse': false
                },
                filters: {
                    'age': {
                    'label': '年齡',
                    'enabled': false, 'value': 18, 'direction': greater_equal
                    },
                    'height': {
                    'label': '身高',
                    'enabled': false, 'value': 150, 'direction': greater_equal
                    },
                    'weight': {
                    'label': '體重',
                    'enabled': false, 'value': 40, 'direction': greater_equal
                    },
                },
                diroptions: [
                    {'text': '以上', 'val': greater_equal},
                    {'text': '整', 'val': exact},
                    {'text': '以下', 'val': less_equal},
                ],
                japanese: true,
                notBoth: false,
                viewMode: 'table_view'
            };
        },
        created: function() {
            this.initialize();
        },
        methods: {
            initialize: function() {
                if (!this.idols[0] || !this.idols[1]) this.notBoth = true;
                if (!this.idols[0]) this.japanese = false;
            },
            changeLanguage: function() {
                this.japanese = !this.japanese;
            },
            sortKey: function(key) {
                if (this.sorts.key == key) {
                    if (this.sorts.reverse) {
                        this.sorts.key = '';
                        this.sorts.reverse = false;
                    }
                    else this.sorts.reverse = true;
                }
                else {
                    this.sorts.key = key;
                    this.sorts.reverse = false;
                }
            },
            changeView: function() {
                this.viewMode = this.viewMode == 'table_view' ? 'card_view' : 'table_view';
            }
        },
        computed: {
            shown() {
                return this.japanese ? this.idols[0] : this.idols[1];
            },
            panelWord: function() {
                return this.japanese ? '中文版' : '日文版'
            }, 
            fltIdols() {
                var self = this;
                var res = self.shown.slice();
                for (let key in self.filters) {
                  let attr = self.filters[key]
                  if (attr.enabled) {
                    res = res.filter(idol => {
                        if (isNaN(parseInt(idol[key]))) return false;
                        return attr.direction(idol[key], attr.value);
                    });
                  }
                }
                return res;
            },
            sortedIdols() {
                var self = this;
                var res = self.fltIdols.slice();
                
                if (self.sorts.key === '') return res;
                else {
                    return res.sort(function(a, b) {
                        let key = self.sorts.key;
                        let reverse = self.sorts.reverse;
                        
                        let ak = a[key];
                        let bk = b[key];
                        let r = reverse ? -1 : 1;
                        return ((ak > bk) ? (1 * r) : (ak < bk) ? (-1 * r) : 0); 
                    });
                }
            }
        },
        watch: {
        }
    }
</script>

<style>
.idol_icon {
  height: 40px;
}
</style>