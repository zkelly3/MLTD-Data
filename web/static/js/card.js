$(function() {
    var card_json = JSON.parse($('#card_json').text());
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            card: card_json,
            japanese: true,
            notBoth: false,
            hasFrom: true,
            hasAwaken: true,
            gashaTitles: ['類型', '名稱', '開始', '結束'],
            panelWord: '中文版'
        },
        created: function() {
            this.initialize();
        },
        methods: {
            initialize: function() {
                if (!this.card[0] || !this.card[1]) this.notBoth = true;
                if (!this.card[0]) {
                    this.japanese = false;
                    this.panelWord = this.japanese ? '中文版' : '日文版'
                }
                for (let i = 0; i < this.card.length; ++i) {
                    this.fixData(this.card[i]);
                }
            },
            fixData: function(card) {
                if (!card) return;
                card.name = card.name ? card.name : '未知'
                card.idolName = (!card.idol) ? '未知' : card.idol.name;
                card.idolUrl = (!card.idol) ? '#' : '/idol/' + card.idol.id;
                card.aquireType = (!card.aquire) ? '未知' : card.aquire.type;
                card.aquireTitle = (!card.aquire) ? '未知' : card.aquire.title ? card.aquire.title : '尚未更新';
                card.awakenWord = card.is_awaken ? '覺醒前' : '覺醒後';
                this.hasAwaken = card.awaken ? true : false;
                card.awakenName = (!this.hasAwaken || !card.awaken.name) ? '尚未更新' : card.awaken.name;
                card.time = (!card.time) ? '尚未更新' : this.japanese ? new Date(card.time * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(card.time * 1000).toLocaleString('zh-TW', { timeZone: 'Asia/Taipei', hour12: false});
                
                for (let i in card.gashas) {
                    let g = card.gashas[i];
                    g.start = (!g.start) ? '尚未更新' : this.japanese ? new Date(g.start * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(g.start * 1000).toLocaleString('zh-TW', { timeZone: 'Asia/Taipei', hour12: false});
                    g.over = (!g.over) ? '尚未更新' : this.japanese ? new Date(g.over * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(g.over * 1000).toLocaleString('zh-TW', { timeZone: 'Asia/Taipei', hour12: false});
                }
            },
            changeLanguage: function() {
                this.japanese = !this.japanese;
                this.panelWord = this.japanese ? '中文版' : '日文版'
            }
        },
        computed: {
            shown: function() {
                return this.japanese ? this.card[0] : this.card[1];
            }
        },
        watch: {
        }
    });
});