import { createApp } from 'vue'
import CardPage from '../components/CardPage.vue'
import { AjaxAPI } from '../api'

createApp(CardPage, {
  card_id: parseInt(document.querySelector('#card_id_json').text)
}).provide('$api', new AjaxAPI()).mount('#app');