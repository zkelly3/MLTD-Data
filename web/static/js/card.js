function fixData(card, ver) {
    if (!card) return;
    deleteNull(card);
    card = $.extend({
        id: 0,
        name: '不明',
        awaken: null,
        time: null,
        flavor: '尚未更新'
    }, card);
    
    deleteNull(card.idol);
    card.idol = $.extend({
        name: '不明',
        url: "#",
        color: '#ffffff',
        idol_type: '',
    }, card.idol);
    
    deleteNull(card.aquire);
    card.aquire = $.extend({
        type: '不明',
        title: '尚未更新',
    }, card.aquire);
    
    if (card.skill) deleteNull(card.skill);
    card.skill = $.extend({
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
$(function() {
    var card_json = JSON.parse($('#card_json').text());
    for (let i = 0; i < card_json.length; ++i) {
        card_json[i] = fixData(card_json[i], i);
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
            },
            cardClass(rare) {
                rare = parseInt(rare / 2);
                switch (rare) {
                    case 3:
                        return 'card_ssr';
                    case 2:
                        return 'card_sr';
                    case 1:
                        return 'card_r';
                }
                if (rare == 0) {
                    switch (this.shown.idol.idol_type) {
                        case 'Princess':
                            return 'card_n_pr';
                        case 'Fairy':
                            return 'card_n_fa';
                        case 'Angel':
                            return 'card_n_an';
                    }
                }
                return '';
            },
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
