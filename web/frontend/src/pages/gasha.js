import { createApp } from 'vue'
import GashaPage from '../components/GashaPage.vue'
import { toDate, toDateTimeString } from '../general'

function fixData(gasha, ver) {
    if (!gasha) return;
    
    gasha.name = (!gasha.name) ? '不明' : gasha.name;
    gasha.start = toDateTimeString(toDate(gasha.start), ver);
    gasha.over = toDateTimeString(toDate(gasha.over), ver);
    
    for (let i in gasha.pick_up) {
        let card = gasha.pick_up[i];
        card.name = (!card.name) ? '不明' : card.name;
    }
    
    for (let i in gasha.others) {
        let card = gasha.others[i];
        card.name = (!card.name) ? '不明' : card.name;
    }
}

var gasha_json = JSON.parse(document.querySelector('#gasha_json').text);
for (let i = 0; i < gasha_json.length; ++i) {
    fixData(gasha_json[i], i);
}

createApp(GashaPage, {
  gasha_json: gasha_json,
}).mount('#app');