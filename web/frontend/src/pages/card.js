import { createApp } from 'vue'
import CardPage from '../components/CardPage.vue'
import { deleteNull, toDate, toDateTimeString } from '../general'

function fixData(card, ver) {
    if (!card) return;
    deleteNull(card);
    card = Object.assign({
        id: 0,
        name: '不明',
        awaken: null,
        time: null,
        flavor: '尚未更新'
    }, card);
    
    deleteNull(card.idol);
    card.idol = Object.assign({
        name: '不明',
        url: "#",
        color: '#ffffff',
        idol_type: '',
    }, card.idol);
    
    deleteNull(card.aquire);
    card.aquire = Object.assign({
        type: '不明',
        title: '尚未更新',
    }, card.aquire);
    
    if (card.skill) deleteNull(card.skill);
    card.skill = Object.assign({
        type: {
            'id': 0,
            'name': ''
        },
        name: '',
        description: ''
    }, card.skill);
    card.skill.type.name = (!card.skill.type.name) ? '' : card.skill.type.name;
    
    card.awakenWord = card.is_awaken ? '覺醒前' : '覺醒後';
    card.awakenName = (!card.awaken || !card.awaken.name) ? '不明' : card.awaken.name;
    card.time = toDateTimeString(toDate(card.time), ver);
    
    for (let i in card.gashas) {
        let g = card.gashas[i];
        g.start = toDateTimeString(toDate(g.start), ver);
        g.over = toDateTimeString(toDate(g.over), ver);
    }
    
    if (card.event) {
        card.event.start = toDateTimeString(toDate(card.event.start), ver);
        card.event.over = toDateTimeString(toDate(card.event.over), ver);
    }
    return card;
}

var card_json = JSON.parse(document.querySelector('#card_json').text);
for (let i = 0; i < card_json.length; ++i) {
    card_json[i] = fixData(card_json[i], i);
}

createApp(CardPage, {
  card_json: card_json,
}).mount('#app');