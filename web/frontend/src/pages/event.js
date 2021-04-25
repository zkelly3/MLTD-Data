import { createApp } from 'vue'
import EventPage from '../EventPage.vue'
import { toDate, toDateString } from '../general'

function standby(obj) {
  obj.src = '/static/images/default/no_event_banner.jpg';
}

function fixData(gameEvent, ver) {
    if (!gameEvent) return;
    
    gameEvent.name = (!gameEvent.name) ? '不明' : gameEvent.name;
    gameEvent.startTime = toDate(gameEvent.start);
    gameEvent.start = toDateTimeString(gameEvent.startTime, ver);
    gameEvent.over = toDateTimeString(toDate(gameEvent.over), ver);
    
    if (gameEvent.cards !== null && Array.isArray(gameEvent.cards)) {
        for (let i in gameEvent.cards) {
            let card = gameEvent.cards[i];
            card.name = (!card.name) ? '不明' : card.name;
        }
    }
    else if (gameEvent.event_abbr == 'ANN') {
        for (let i in gameEvent.cards) {
            for (let j in gameEvent.cards[i].data) {
                let card = gameEvent.cards[i].data[j];
                card.name = (!card.name) ? '不明' : card.name;
            }
        }
    }
    else if (gameEvent.cards !== null) {
        for (let i in gameEvent.cards) {
            for (let j in gameEvent.cards[i]) {
                let card = gameEvent.cards[i][j];
                card.name = (!card.name) ? '不明' : card.name;
            }
        }
    }
    
    if (gameEvent.event_abbr === 'ANN') {
        for (let i in gameEvent.cards) {
            gameEvent.cards[i].mission_date = toDateString(toDate(gameEvent.cards[i].mission_date), ver);
        }
    }
}

var event_json = JSON.parse($('#event_json').text());
for (let i = 0; i < event_json.length; ++i) {
    fixData(event_json[i], i);
}

createApp(EventPage, {
  event_json: event_json,
}).mount('#app');
