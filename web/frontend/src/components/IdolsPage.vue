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
    <ListFilter :list="shown" :filters="[
                       { key: 'age', label: '年齡', default_value: 18 },
                       { key: 'height', label: '身高', default_value: 150 },
                       { key: 'weight', 'label': '體重', default_value: 40 },
                       ]" @filtered_list="val => { fltIdols = val; }"/>

    <table class="table mt-3 align-middle" id="idols" v-if="viewMode == 'table_view'">
        <thead class="table-light">
            <tr>
                <th v-for="info in idolinfo" :key="info.val">
                    <a href="#" v-on:click="sortKey(info.val)" class="d-block" :class="{ active: sorts.key === info.val }">{{ info.text }}</a>
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="idol in sortedIdols" :key="idol.name">
                <td>
                    <router-link class="d-block" :to="idol.url">
                        <CardIcon class="me-2" :card="{...idol, rare: 0}" />{{ idol.name }}
                    </router-link>
                </td>
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
                <router-link class="stretched-link" :to="idol.url">
                    <img :src="idol.img_url" class="card-img-top" />
                </router-link>
                <div class="card-body">

                    <div class="card-title">{{ idol.name }}</div>
                </div>

            </div>
        </div>
    </div>
</MainPage>
</template>

<script>
import CardIcon from './CardIcon.vue'
import MainPage from './MainPage.vue'
import ListFilter from './ListFilter.vue'
import { deleteNull } from '../general'

function fixData(idols) {
    for (let i in idols) {
        let idol = idols[i];
        deleteNull(idol);
        idols[i] = Object.assign({
            name: '不明',
            idol_type: '不明',
            age: '不明',
            height: '不明',
            weight: '不明'
        }, idol);
    }    
}

export default {
        name: 'IdolsPage',
    components: {
        CardIcon, MainPage, ListFilter,
    },
    inject: ['$api'],
    props: [],
        data() {
            return {
                idols: [[], []],
                fltIdols: [],
                idolinfo: [{'text': '姓名', 'val': 'name'},
                    {'text': '陣營', 'val': 'idol_type'},
                    {'text': '年齡', 'val': 'age'},
                    {'text': '身高', 'val': 'height'},
                    {'text': '體重', 'val': 'weight'}],
                sorts: {
                    'key': '',
                    'reverse': false
                },
                japanese: true,
                notBoth: false,
                viewMode: 'table_view'
            };
        },
        mounted() {
            this.updatePage();
        },
        methods: {
            updatePage: function() {
                this.$api.getIdols().then((res) => {
                    const tmpIdols = res.data;
                    for (let i=0; i<tmpIdols.length; ++i) {
                        fixData(tmpIdols[i]);
                    }
                    this.idols = tmpIdols;
                    this.initialize();
                });
            },
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
  height: 50px;
}
</style>
