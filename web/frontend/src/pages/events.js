import { createApp } from 'vue'
import EventsPage from '../components/EventsPage.vue'
import { toDate, toDateString } from '../general'

function fixData(events, ver) {
    for (let i in events) {
        events[i].name = (!events[i].name) ? '不明' : events[i].name;
        events[i].start = toDateString(toDate(events[i].start), ver);
        events[i].over = toDateString(toDate(events[i].over), ver);
    }    
}

var events_json = JSON.parse(document.querySelector('#events_json').text);
for (let i = 0; i < events_json.length; ++i) {
    fixData(events_json[i], i);
}
var types_json = JSON.parse(document.querySelector('#types_json').text);

createApp(EventsPage, {
  events_json: events_json,
  types_json: types_json,
}).mount('#app');