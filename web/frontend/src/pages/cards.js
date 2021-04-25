import { createApp } from 'vue'
import CardsPage from '../components/CardsPage.vue'

function fixData(cards) {
    for (let i in cards) {
        cards[i].name = (!cards[i].name) ? '不明' : cards[i].name;
    }    
}

var cards_json = JSON.parse(document.querySelector('#cards_json').text);
for (let i = 0; i < cards_json.length; ++i) {
    fixData(cards_json[i]);
}

var filters_json = JSON.parse(document.querySelector('#filters_json').text);
var sorts_json = JSON.parse(document.querySelector('#sorts_json').text);
var idols_json = JSON.parse(document.querySelector('#idols_json').text);

createApp(CardsPage, {
    cards_json: cards_json,
    filters_json: filters_json,
    sorts_json: sorts_json,
    idols_json: idols_json,
}).mount('#app');