import { createApp } from 'vue'
import IdolsPage from '../components/IdolsPage.vue'
import { deleteNull } from '../general'

function fixData(idols) {
    for (let i in idols) {
        let idol = idols[i];
        deleteNull(idol);
        idols[i] = Object.assign({
            name: '不明',
            idol_type: '不明',
            age: '不明',
            height: '不明',
            weight: '不明'
        }, idol);
    }    
}

var idols_json = JSON.parse(document.querySelector('#idols_json').text);
for (let i = 0; i < idols_json.length; ++i) {
    fixData(idols_json[i]);
}

createApp(IdolsPage, {
    idols_json: idols_json,
  }).mount('#app');