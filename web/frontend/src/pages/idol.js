import { createApp } from 'vue'
import IdolPage from '../components/IdolPage.vue'
import { deleteNull, toDate, toDateString } from '../general'

function fixData(idol, ver) {
    if (!idol) return;
    
    deleteNull(idol.info);
    idol.info = Object.assign({
        name: '不明',
        idol_type: '不明',
        age: '不明',
        height: '不明',
        weight: '不明'
    }, idol.info);
        
    for (let i in idol.cards) {
        let card = idol.cards[i];
        deleteNull(card);
        idol.cards[i] = Object.assign({
            id: 0,
            name: '不明',
            rare: -1,
            time: null,
            img_url: '#',
            url: '#'
        }, card);
        idol.cards[i].time = toDateString(toDate(card.time), ver);
    }
}

var idol_json = JSON.parse(document.querySelector('#idol_json').text);
for (let i = 0; i < idol_json.length; ++i) {
    fixData(idol_json[i], i);
}

createApp(IdolPage, {
  idol_json: idol_json,
}).mount('#app');
