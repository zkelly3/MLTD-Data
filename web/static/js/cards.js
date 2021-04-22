function fixData(cards, ver) {
    for (let i in cards) {
        cards[i].name = (!cards[i].name) ? '不明' : cards[i].name;
        cards[i].time = toDateString(toDate(cards[i].time), ver);
    }    
}

$(function() {
    var cards_json = JSON.parse($('#cards_json').text());
    for (let i = 0; i < cards_json.length; ++i) {
        fixData(cards_json[i], i);
    }
    
    var filters_json = JSON.parse($('#filters_json').text());
    
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            cards: cards_json,
            japanese: true,
            notBoth: false,
            filters: filters_json,
            paging: {
                onePageList: [10, 20, 50, 100],
                purPage: 20,
                current: 1
            }
        },
        created: function() {
            this.initialize();
        },
        methods: {
            initialize: function() {
                if (!this.cards[0] || !this.cards[1]) this.notBoth = true;
                if (!this.cards[0]) this.japanese = false;
            },
            changeLanguage: function() {
                this.japanese = !this.japanese;
            },
            shownOptions: function(options) {
                return this.japanese ? options[0] : options[1];
            },
            changePage(page) {
                this.paging.current = page;
            }, 
            prevPage() {
                this.changePage(this.paging.current-1);
            },
            nextPage() {
                this.changePage(this.paging.current+1);
            },
            cardClass(card) {
                var rare = card.rare;
                switch (rare) {
                    case 3:
                        return 'card_ssr';
                    case 2:
                        return 'card_sr';
                    case 1:
                        return 'card_r';
                }
                if (rare == 0) {
                    switch (card.idol_type) {
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
            shown() {
                return this.japanese ? this.cards[0] : this.cards[1];
            },
            shownFilters() {
                return this.japanese ? this.filters[0] : this.filters[1];
            },
            fltCards() {
                var self = this;
                var res = self.shown.slice();
                
                for (let key in self.shownFilters) {
                  attr = self.shownFilters[key];
                  if (attr.enabled) {
                    if (attr.type === 'check') {
                        res = res.filter(card => {
                            return !attr.selected.length || attr.selected.includes(card[attr.key]);
                        });
                    }
                    else if (attr.type === 'search') {
                        res = res.filter(gameEvent => {
                            return attr.value === '' || gameEvent.name.toLowerCase().includes(attr.value.toLowerCase());
                        });
                    }
                  }
                }
                
                return res;
            },
            pageFltCards() {
                var self = this;
                var res = self.fltCards.slice();
                var first = (self.paging.current-1) * (self.paging.purPage);
                var last = (self.paging.current) * (self.paging.purPage);
                res = res.filter((card, index) => {
                    return (index >= first) && (index < last);
                });
                return res;
            },
            panelWord() {
                return this.japanese ? '中文版' : '日文版'
            },
            totalPage() {
                return parseInt((this.fltCards.length-1) / this.paging.purPage) + 1
            },
            calcPagination() {
                var res = {};
                var last = this.totalPage;
                var first = 1;
                
                res.noPrev = (this.paging.current) === first;
                res.noNext = (this.paging.current) === last;
                
                res.pages = [];
                if (this.totalPage <= 5) {
                    for (let i=1; i<= this.totalPage; i++) {
                        res.pages.push({
                            'val': i,
                            'isCurrent': (i === this.paging.current), 
                        });
                    }
                }
                else if (this.paging.current <= 3) {
                    for (let i=1; i<=5; i++) {
                        res.pages.push({
                            'val': i,
                            'isCurrent': (i === this.paging.current), 
                        });
                    }
                }
                else if ((this.paging.current+2) > this.totalPage) {
                    for (let i=this.totalPage-4; i<=this.totalPage; i++) {
                        res.pages.push({
                            'val': i,
                            'isCurrent': (i === this.paging.current), 
                        });
                    }
                }
                else {
                    for (let i=this.paging.current-2; i<=this.paging.current+2; i++) {
                        res.pages.push({
                            'val': i,
                            'isCurrent': (i === this.paging.current), 
                        });
                    }
                }
                return res;
            }
        },
        watch: {
            pageFltCards: function() {
                this.paging.current = Math.min(this.paging.current, this.totalPage);
            }
        }
    });
});
