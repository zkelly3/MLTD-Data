function fixData(idol, ver) {
    if (!idol) return;
    
    deleteNull(idol.info);
    idol.info = $.extend({
        name: '不明',
        idol_type: '不明',
        age: '不明',
        height: '不明',
        weight: '不明'
    }, idol.info);
        
    for (let i in idol.cards) {
        let card = idol.cards[i];
        deleteNull(card);
        idol.cards[i] = $.extend({
            id: 0,
            name: '不明',
            rare: '不明',
            time: null,
            img_url: '#',
            url: '#'
        }, card);
        idol.cards[i].time = toDateString(toDate(card.time), ver);
    }
}
$(function() {
    var idol_json = JSON.parse($('#idol_json').text());
    for (let i = 0; i < idol_json.length; ++i) {
        fixData(idol_json[i], i);
    }
    
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            idol: idol_json,
            japanese: true,
            notBoth: false,
            cardTitles: ['名稱', '稀有度', '實裝時間']
        },
        created: function() {
            this.initialize();
        },
        methods: {
            initialize: function() {
                if (!this.idol[0] || !this.idol[1]) this.notBoth = true;
                if (!this.idol[0]) this.japanese = false;
            },
            changeLanguage: function() {
                this.japanese = !this.japanese;
            }
        },
        computed: {
            shown: function() {
                return this.japanese ? this.idol[0] : this.idol[1];
            },
            panelWord: function() {
                return this.japanese ? '中文版' : '日文版'
            }, 
            fltCards() {
                // 保留以便之後寫稀有度 filter
                var self = this;
                var res = self.cards.slice();
                res = res.filter(card => {
                    if (self.japanese) {
                        return card['jp_time'];
                    }
                    else {
                        return card['as_time'];
                    }
                });
                return res;
            }
        },
        watch: {
            /*filters(v) {
                this.$emit('input', v);
            }*/
        }
    });
});
