function greater_equal(a, b) {
    return a >= b;
}
function less_equal(a, b) {
    return a <= b;
}
function exact(a, b) {
    return a == b;
}

$(function() {
    var info_json = JSON.parse($('#info_json').text());
    var cards_json = JSON.parse($('#cards_json').text());
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            info: info_json,
            cards: cards_json,
            japanese: true,
            panelWord: '中文版',
            cardInfo: ['', '名稱', '稀有度', '實裝時間']
        },
        created: function() {
        },
        methods: {
            changeLanguage: function() {
                this.japanese = !this.japanese;
                this.panelWord = this.japanese ? '中文版' : '日文版'
            }
        },
        computed: {
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
