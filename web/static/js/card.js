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
            gashaTitles: ['類型', '名稱', '開始', '結束']
        },
        created: function() {
            this.initialize();
        },
        methods: {
            initialize: function() {
                if (!this.card[0] || !this.card[1]) this.notBoth = true;
                if (!this.card[0]) {
                    this.japanese = false;
                }
                for (let i = 0; i < this.card.length; ++i) {
                    this.fixData(this.card[i]);
                }
            },
            fixData: function(card) {
                if (!card) return;
                card.name = card.name ? card.name : '未知'
                card.idolName = (!card.idol) ? '未知' : card.idol.name;
                card.idolUrl = (!card.idol) ? '#' : card.idol.url;
                card.idolColor = (!card.idol || !card.idol.color) ? '#ffffff33' : card.idol.color + '33';
                card.aquireType = (!card.aquire) ? '未知' : card.aquire.type;
                card.aquireTitle = (!card.aquire) ? '未知' : card.aquire.title ? card.aquire.title : '尚未更新';
                card.awakenWord = card.is_awaken ? '覺醒前' : '覺醒後';
                this.hasAwaken = card.awaken ? true : false;
                card.awakenName = (!this.hasAwaken || !card.awaken.name) ? '尚未更新' : card.awaken.name;
                card.time = (!card.time) ? '尚未更新' : card.is_jp ? new Date(card.time * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(card.time * 1000).toLocaleString('zh-TW', { timeZone: 'Asia/Taipei', hour12: false});
                card.skillType = (!card.skill || !card.skill.type || !card.skill.type.name) ? '' : card.skill.type.name;
                card.skillName = (!card.skill || !card.skill.name) ? '' : card.skill.name;
                card.skillDesc = (!card.skill || !card.skill.description) ? '' : card.skill.description;
                card.flavor = card.flavor ? card.flavor : '尚未更新'
                
                for (let i in card.gashas) {
                    let g = card.gashas[i];
                    g.start = (!g.start) ? '尚未更新' : card.is_jp ? new Date(g.start * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(g.start * 1000).toLocaleString('zh-TW', { timeZone: 'Asia/Taipei', hour12: false});
                    g.over = (!g.over) ? '尚未更新' : card.is_jp ? new Date(g.over * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(g.over * 1000).toLocaleString('zh-TW', { timeZone: 'Asia/Taipei', hour12: false});
                }
                
                if (card.event) {
                    card.event.start = (!card.event.start) ? '尚未更新' : card.is_jp ? new Date(card.event.start * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(card.event.start * 1000).toLocaleString('zh-TW', { timeZone: 'Asia/Taipei', hour12: false});
                    card.event.over = (!card.event.over) ? '尚未更新' : card.is_jp ? new Date(card.event.over * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(card.event.over * 1000).toLocaleString('zh-TW', { timeZone: 'Asia/Taipei', hour12: false});
                }
            },
            changeLanguage: function() {
                this.japanese = !this.japanese;
            }
        },
        computed: {
            shown: function() {
                return this.japanese ? this.card[0] : this.card[1];
            },
            panelWord: function() {
                return this.japanese ? '中文版' : '日文版'
            }, 
            styleList: function() {
                return  {
                  'background': this.shown.idolColor  
                };
            }
        },
        watch: {
        }
    });
});