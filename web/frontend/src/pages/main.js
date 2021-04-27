import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { AjaxAPI } from '../api'
import IdolsPage from '../components/IdolsPage.vue'
import CardsPage from '../components/CardsPage.vue'
import EventsPage from '../components/EventsPage.vue'
import GashasPage from '../components/GashasPage.vue'
import IdolPage from '../components/IdolPage.vue'
import CardPage from '../components/CardPage.vue'
import EventPage from '../components/EventPage.vue'
import GashaPage from '../components/GashaPage.vue'

const routes = [
    { path: '/', component: IdolsPage, meta: {title: '偶像列表'} },
    { path: '/idols', component: IdolsPage, meta: {title: '偶像列表'} },
    { path: '/cards', component: CardsPage, meta: {title: '卡片列表'} },
    { path: '/events', component: EventsPage, meta: {title: '活動列表'} },
    { path: '/gashas', component: GashasPage, meta: {title: '卡池列表'} },
    { path: '/idol/:idol_id', component: IdolPage, props: true, meta: {title: '偶像'} },
    { path: '/card/:card_id', component: CardPage, props: true, meta: {title: '卡片'} },
    { path: '/event/:event_type/:event_id', component: EventPage, props: true, meta: {title: '活動'} },
    { path: '/gasha/:gasha_id', component: GashaPage, props: true, meta: {title: '卡池'} },
];

const router = createRouter({
    history: createWebHistory(),
    routes: routes,
});

router.beforeEach(async (to) => {
    if (to.meta.title) {
        if (to.params.card_id) {
            let $api = new AjaxAPI();
            let res = await $api.getCardTitle(to.params.card_id);
            document.title = res.data;
        }
        else {
            document.title = to.meta.title + ' - ポンコマス';
        }
    }
    else {
        document.title = 'ポンコマス';
    }
});

createApp({}).use(router).provide('$api', new AjaxAPI()).mount('#app');