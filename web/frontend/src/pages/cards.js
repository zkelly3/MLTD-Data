import { createApp } from 'vue'
import CardsPage from '../components/CardsPage.vue'
import { AjaxAPI } from '../api'

createApp(CardsPage).provide('$api', new AjaxAPI()).mount('#app');