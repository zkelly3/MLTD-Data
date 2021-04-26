import { createApp } from 'vue'
import IdolPage from '../components/IdolPage.vue'
import { AjaxAPI } from '../api'

var idol_id_json = parseInt(document.querySelector('#idol_id_json').text);

createApp(IdolPage, {
  idol_id: idol_id_json,
}).provide('$api', new AjaxAPI()).mount('#app');
