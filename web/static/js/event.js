function standby(obj) {
  obj.src = '/static/images/default/no_event_banner.jpg';
}

$(function() {
    var event_json = JSON.parse($('#event_json').text());
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
                if (!this.gameEvent[0]) {
                    this.japanese = false;
                }
                for (let i = 0; i < this.gameEvent.length; ++i) {
                    this.fixData(this.gameEvent[i]);
                }
            },
            fixData: function(gameEvent) {
                if (!gameEvent) return;
                gameEvent.name = gameEvent.name ? gameEvent.name : '未知';
                gameEvent.startTime = (!gameEvent.start) ? null : new Date(gameEvent.start * 1000);
                gameEvent.start = (!gameEvent.start) ? '--' : gameEvent.is_jp ? new Date(gameEvent.start * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(gameEvent.start * 1000).toLocaleString('ja-JP', { timeZone: 'Asia/Taipei', hour12: false});
                gameEvent.over = (!gameEvent.over) ? '--' : gameEvent.is_jp ? new Date(gameEvent.over * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(gameEvent.over * 1000).toLocaleString('ja-JP', { timeZone: 'Asia/Taipei', hour12: false});
                
                if (gameEvent.cards != null && Array.isArray(gameEvent.cards)) {
                    for (let i in gameEvent.cards) {
                        let card = gameEvent.cards[i];
                        card.name = (!card.name) ? '未知' : card.name;
                    }
                }
                else if (gameEvent.event_abbr == 'ANN') {
                    for (let i in gameEvent.cards) {
                        for (let j in gameEvent.cards[i].data) {
                            let card = gameEvent.cards[i].data[j];
                            card.name = (!card.name) ? '未知' : card.name;
                        }
                    }
                }
                else if (gameEvent.cards != null) {
                    for (let i in gameEvent.cards) {
                        for (let j in gameEvent.cards[i]) {
                            let card = gameEvent.cards[i][j];
                            card.name = (!card.name) ? '未知' : card.name;
                        }
                    }
                }
                
                if (gameEvent.event_abbr === 'ANN') {
                    for (let i in gameEvent.cards) {
                        gameEvent.cards[i].mission_date = (!gameEvent.cards[i].mission_date) ? null : new Date(gameEvent.cards[i].mission_date * 1000).toLocaleDateString("ja-JP", {timeZone: 'Asia/Taipei', hour12: false});
                    }
                }
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