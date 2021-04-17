function toDate(timestamp) {
    return (!timestamp) ? null : new Date(timestamp * 1000);
}
function toDateString(time, ver) {
    // ver 0: jp, 1: as
    if (ver) return (!time) ? '尚未更新' : time.toLocaleDateString("ja-JP", {timeZone: 'Japan', hour12: false})
    else return (!time) ? '尚未更新' : time.toLocaleDateString("ja-JP", {timeZone: 'Asia/Taipei', hour12: false})
}

function fixData(idol, ver) {
    if (!idol) return;
    
    idol.info = $.extend({
        name: '未知',
        idol_type: '未知',
        age: '不明',
        height: '不明',
        weight: '不明',
    }, idol.info);
    
    for (let i in idol.cards) {
        let card = idol.cards[i];
        card.name = (!card.name) ? '未知' : card.name;
        card.time = toDateString(toDate(card.time), ver);
    }
}
$(function() {
    var idol_json = JSON.parse($('#idol_json').text());
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
                if (!this.idol[0]) {
                    this.japanese = false;
                }
                for (let i in this.idol) {
                    fixData(this.idol[i], i);
                }
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
