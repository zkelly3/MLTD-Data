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


$(function() {
    var event_json = JSON.parse($('#event_json').text());
    for (let i = 0; i < event_json.length; ++i) {
        fixData(event_json[i], i);
    }
    
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            gameEvent: event_json,
            japanese: true,
            notBoth: false,
            defaultEvent: '/static/images/default/no_event_banner.jpg'
        },
        created: function() {
            this.initialize();
        },
        methods: {
            initialize: function() {
                if (!this.gameEvent[0] || !this.gameEvent[1]) this.notBoth = true;
                if (!this.gameEvent[0]) this.japanese = false;
            },
            changeLanguage: function() {
                this.japanese = !this.japanese;
            }
        },
        computed: {
            shown: function() {
                return this.japanese ? this.gameEvent[0] : this.gameEvent[1];
            },
            panelWord: function() {
                return this.japanese ? '中文版' : '日文版'
            }
        },
        watch: {
        }
    });
});