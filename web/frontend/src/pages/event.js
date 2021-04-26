import { createApp } from 'vue'
import EventPage from '../components/EventPage.vue'
import { AjaxAPI } from '../api'

createApp(EventPage, {
    event_type: parseInt(document.querySelector('#event_type_json').text),
    event_id: parseInt(document.querySelector('#event_id_json').text),
}).provide('$api', new AjaxAPI()).mount('#app');
