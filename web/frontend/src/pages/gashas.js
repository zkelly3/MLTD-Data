import { createApp } from 'vue'
import GashasPage from '../components/GashasPage.vue'
import { toDate, toDateString } from '../general'

function fixData(gashas, ver) {
    for (let i in gashas) {
        gashas[i].name = (!gashas[i].name) ? '不明' : gashas[i].name;
        gashas[i].start = toDateString(toDate(gashas[i].start), ver);
        gashas[i].over = toDateString(toDate(gashas[i].over), ver);
    }    
}

var gashas_json = JSON.parse(document.querySelector('#gashas_json').text);
for (let i = 0; i < gashas_json.length; ++i) {
    fixData(gashas_json[i], i);
}
var types_json = JSON.parse(document.querySelector('#types_json').text);

createApp(GashasPage, {
  gashas_json: gashas_json,
  types_json: types_json,
}).mount('#app');