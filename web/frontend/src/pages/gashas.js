import { createApp } from 'vue'
import GashasPage from '../components/GashasPage.vue'
import { AjaxAPI } from '../api'

createApp(GashasPage).provide('$api', new AjaxAPI()).mount('#app');