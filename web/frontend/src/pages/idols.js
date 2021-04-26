import { createApp } from 'vue'
import IdolsPage from '../components/IdolsPage.vue'
import { AjaxAPI } from '../api'

createApp(IdolsPage).provide('$api', new AjaxAPI()).mount('#app');