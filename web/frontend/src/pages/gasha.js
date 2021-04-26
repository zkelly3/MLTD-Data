import { createApp } from 'vue'
import GashaPage from '../components/GashaPage.vue'
import { AjaxAPI } from '../api'

createApp(GashaPage, {
  gasha_id: parseInt(document.querySelector('#gasha_id_json').text)
}).provide('$api', new AjaxAPI()).mount('#app');