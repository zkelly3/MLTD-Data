import { createApp } from 'vue'
import EventsPage from '../components/EventsPage.vue'
import { AjaxAPI } from '../api'

createApp(EventsPage).provide('$api', new AjaxAPI()).mount('#app');