import 'bootstrap';
import 'bootstrap-icons/font/bootstrap-icons.css'
import './style.scss'

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { AjaxAPI } from './api'
import HomePage from './components/HomePage.vue'
import IdolsPage from './components/IdolsPage.vue'
import CardsPage from './components/CardsPage.vue'
import EventsPage from './components/EventsPage.vue'
import GashasPage from './components/GashasPage.vue'
import SongsPage from './components/SongsPage.vue'
import IdolPage from './components/IdolPage.vue'
import CardPage from './components/CardPage.vue'
import EventPage from './components/EventPage.vue'
import GashaPage from './components/GashaPage.vue'
import SongPage from './components/SongPage.vue'
import GroupPage from './components/GroupPage.vue'
import PSTCardPage from './components/PSTCardPage.vue'
import SSRCardPage from './components/SSRCardPage.vue'
import NotFoundPage from './components/NotFoundPage.vue'

const routes = [
    { path: '/', component: HomePage, meta: {title: '首頁'} },
    { path: '/idols', component: IdolsPage, meta: {title: '偶像列表'} },
    { path: '/cards', component: CardsPage, meta: {title: '卡片列表'} },
    { path: '/events', component: EventsPage, meta: {title: '活動列表'} },
    { path: '/gashas', component: GashasPage, meta: {title: '卡池列表'} },
    { path: '/songs', component: SongsPage, meta: {title: '曲目列表'} },
    { path: '/idol/:idol_id', component: IdolPage, props: true },
    { path: '/card/:card_id', component: CardPage, props: true },
    { path: '/event/:event_id', component: EventPage, props: true },
    { path: '/gasha/:gasha_id', component: GashaPage, props: true },
    { path: '/song/:song_id', component: SongPage, props: true},
    { path: '/group/:group_id', component: GroupPage, props: true},
    { path: '/pst', component: PSTCardPage, meta: {title: '上下位卡片整理'} },
    { path: '/ssr', component: SSRCardPage, meta: {title: 'SSR 卡片整理'} },
    { path: '/:pathMatch(.*)*', component: NotFoundPage },
];

const router = createRouter({
    history: createWebHistory(),
    routes: routes,
});

function setTitle(title) {
    if (title) {
        document.title = title + ' - ポンコマス';
    } else {
        document.title = 'ポンコマス';
    }
}

router.beforeEach(async (to) => {
    setTitle(to.meta.title || '');
});

createApp({}).use(router)
    .provide('$api', new AjaxAPI())
    .provide('$setTitle', setTitle)
    .mount('#app');
