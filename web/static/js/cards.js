function fixData(cards, ver) {
    for (let i in cards) {
        cards[i].name = (!cards[i].name) ? '不明' : cards[i].name;
    }    
}

$(function() {
    var cards_json = JSON.parse($('#cards_json').text());
    for (let i = 0; i < cards_json.length; ++i) {
        fixData(cards_json[i], i);
    }
    
    var filters_json = JSON.parse($('#filters_json').text());
    var sorts_json = JSON.parse($('#sorts_json').text());
    var idols_json = JSON.parse($('#idols_json').text());
    
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            cards: cards_json,
            japanese: true,
            notBoth: false,
            filters: filters_json,
            sorts: {
                sortKey: 'time',
                reverse: true,
                options: sorts_json,
            },
            idols: idols_json,
            paging: {
                onePageList: [10, 20, 50, 100],
                purPage: 20,
                current: 1,
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
            idolClass(idol) {
                switch (idol.idol_type) {
                    case 'Princess':
                        return 'idol_pr'
                    case 'Fairy':
                        return 'idol_fa'
                    case 'Angel':
                        return 'idol_an'
                    case 'Guest':
                        return 'idol_gu'
                }
            },
            selectIdol(idol_id) {
                this.shownFilters.belong.idol_selected = idol_id
            },
            setIdolEnabled(filter, enabled) {
                filter.idol_enabled = enabled;
                if (filter.idol_enabled) {
                    filter.type_selected.splice(0);
                }
            },
            toggleTypeSelected(filter, opt) {
                const index = filter.type_selected.indexOf(opt);
                if (index !== -1) {
                  filter.type_selected.splice(index, 1);
                } else {
                    filter.idol_enabled = false;
                    filter.type_selected.push(opt);
                }
            },
            sortReverse() {
                this.sorts.reverse = !this.sorts.reverse;
            },
            showTime(time) {
                return this.japanese ? toDateString(toDate(time), 0) : toDateString(toDate(time), 1);
            }
        },
        computed: {
            shown() {
                return this.japanese ? this.cards[0] : this.cards[1];
            },
            shownFilters() {
                return this.japanese ? this.filters[0] : this.filters[1];
            },
            shownSorts() {
                return this.japanese ? this.sorts.options[0] : this.sorts.options[1];
            },
            sortText() {
                for (let i in this.shownSorts) {
                    if (this.shownSorts[i].val === this.sorts.sortKey) {
                        return this.shownSorts[i].text;
                    }
                }
                return '';
            },
            shownIdols() {
                return this.japanese ? this.idols[0] : this.idols[1];
            },
            fltCards() {
                var self = this;
                var res = self.shown.slice();
                
                for (let key in self.shownFilters) {
                    attr = self.shownFilters[key];
                    if (attr.type === 'check') {
                        res = res.filter(card => {
                            return !attr.selected.length || attr.selected.includes(card[attr.key]);
                        });
                    }
                    else if (attr.type === 'idol_check') {
                        if (attr.idol_enabled) {
                            res = res.filter(card => {
                                return attr.idol_selected === card[attr.idol_key];
                            });
                        }
                        else {
                            res = res.filter(card => {
                                return !attr.type_selected.length || attr.type_selected.includes(card[attr.type_key]);
                            });
                        }
                    }
                    else if (attr.type === 'search') {
                        res = res.filter(gameEvent => {
                            return attr.value === '' || gameEvent.name.toLowerCase().includes(attr.value.toLowerCase());
                        });
                    }
                }
                
                return res;
            },
            sortedCards() {
                var self = this;
                var res = self.fltCards.slice();
                
                if (self.sorts.sortKey === '') return res;
                return res.sort(function(a, b) {
                    let key = self.sorts.sortKey;
                    let reverse = self.sorts.reverse;
                    
                    let ak = a[key];
                    let bk = b[key];
                    let r = reverse ? -1 : 1;
                    return ((ak > bk) ? (1 * r) : (ak < bk) ? (-1 * r) : (a.fake_id > b.fake_id) ? (1 * r) : (a.fake_id < b.fake_id) ? (-1 * r) : 0); 
                });
            },
            pageFltCards() {
                var self = this;
                var res = self.sortedCards.slice();
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
            sortPanelWord() {
                return this.sorts.reverse && this.japanese ? '昇順' : this.sorts.reverse ? '遞增' : this.japanese ? '降順' : '遞減';
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
            },
        },
        watch: {
            pageFltCards: function() {
                this.paging.current = Math.min(this.paging.current, this.totalPage);
            },
        }
    });
});
