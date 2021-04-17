function fixData(card) {
    if (!card) return;
    card.name = card.name ? card.name : '未知';
    card.idol = $.extend({
        name: '未知',
        url: "#",
        color: '#ffffff'
    }, card.idol);
    card.aquire = $.extend({
        type: '未知',
        title: '尚未更新',
    }, card.aquire);
    card.awakenWord = card.is_awaken ? '覺醒前' : '覺醒後';
    card.awakenName = (!card.awaken || !card.awaken.name) ? '尚未更新' : card.awaken.name;
    card.time = (!card.time) ? '尚未更新' : card.is_jp ? new Date(card.time * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(card.time * 1000).toLocaleString('ja-JP', { timeZone: 'Asia/Taipei', hour12: false});
    card.skillType = (!card.skill || !card.skill.type || !card.skill.type.name) ? '' : card.skill.type.name;
    card.skillName = (!card.skill || !card.skill.name) ? '' : card.skill.name;
    card.skillDesc = (!card.skill || !card.skill.description) ? '' : card.skill.description;
    card.flavor = card.flavor ? card.flavor : '尚未更新'
    
    for (let i in card.gashas) {
        let g = card.gashas[i];
        g.start = (!g.start) ? '尚未更新' : card.is_jp ? new Date(g.start * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(g.start * 1000).toLocaleString('ja-JP', { timeZone: 'Asia/Taipei', hour12: false});
        g.over = (!g.over) ? '尚未更新' : card.is_jp ? new Date(g.over * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(g.over * 1000).toLocaleString('ja-JP', { timeZone: 'Asia/Taipei', hour12: false});
    }
    
    if (card.event) {
        card.event.start = (!card.event.start) ? '尚未更新' : card.is_jp ? new Date(card.event.start * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(card.event.start * 1000).toLocaleString('ja-JP', { timeZone: 'Asia/Taipei', hour12: false});
        card.event.over = (!card.event.over) ? '尚未更新' : card.is_jp ? new Date(card.event.over * 1000).toLocaleString('ja-JP', { timeZone: 'Japan', hour12: false}) : new Date(card.event.over * 1000).toLocaleString('ja-JP', { timeZone: 'Asia/Taipei', hour12: false});
    }
}
$(function() {
    var card_json = JSON.parse($('#card_json').text());
    for (let i = 0; i < card_json.length; ++i) {
        fixData(card_json[i]);
    }
    Vue.component('my-tr', {
        template: '<div class="row g-0 border-bottom"><slot></slot></div>'
    });
    Vue.component('my-th', {
        template: '<div class="col-xl-2 col-sm-3 p-2"><slot></slot></div>'
    });
    Vue.component('my-td', {
        template: '<div class="col-xl-10 col-sm-9 p-2"><slot></slot></div>'
    });
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            card: card_json,
            japanese: true,
            notBoth: false,
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
                  'background': this.shown.idol.color + '33'
                };
            }
        },
        watch: {
        }
    });
});
