function fixData(gashas, ver) {
    for (let i in gashas) {
        gashas[i].name = (!gashas[i].name) ? '不明' : gashas[i].name;
        gashas[i].start = toDateString(toDate(gashas[i].start), ver);
        gashas[i].over = toDateString(toDate(gashas[i].over), ver);
    }    
}

$(function() {
    var gashas_json = JSON.parse($('#gashas_json').text());
    for (let i = 0; i < gashas_json.length; ++i) {
        fixData(gashas_json[i], i);
    }
    var types_json = JSON.parse($('#types_json').text());
    
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            gashas: gashas_json,
            japanese: true,
            notBoth: false,
            filters: {
                'gashaType': {
                    'type': 'check',
                    'label': '卡池類型',
                    'enabled': true,
                    'options': types_json,
                    'selected': [],
                },
                'gashaName': {
                    'type': 'search',
                    'label': '搜尋',
                    'enabled': true,
                    'value': '',
                }
            },
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
                if (!this.gashas[0] || !this.gashas[1]) this.notBoth = true;
                if (!this.gashas[0]) this.japanese = false;
                
                for (let i in this.filters.gashaType.options[0]) {
                    let val = this.filters.gashaType.options[0][i].val;
                    if (val !== 'SPC') this.filters.gashaType.selected.push(val);
                }
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
        },
        computed: {
            shown() {
                return this.japanese ? this.gashas[0] : this.gashas[1];
            },
            fltGashas() {
                var self = this;
                var res = self.shown.slice();
                for (let key in self.filters) {
                  attr = self.filters[key]
                  if (attr.enabled) {
                    if (attr.type === 'check') {
                        res = res.filter(gasha => {
                            return attr.selected.includes(gasha.gasha_abbr);
                        });
                    }
                    else if (attr.type === 'search') {
                        res = res.filter(gasha => {
                            return attr.value === '' || gasha.name.toLowerCase().includes(attr.value.toLowerCase());
                        });
                    }
                  }
                }
                return res;
            },
            pageFltGashas() {
                var self = this;
                var res = self.fltGashas.slice();
                var first = (self.paging.current-1) * (self.paging.purPage);
                var last = (self.paging.current) * (self.paging.purPage);
                res = res.filter((gasha, index) => {
                    return (index >= first) && (index < last);
                });
                return res;
            },
            panelWord() {
                return this.japanese ? '中文版' : '日文版'
            },
            totalPage() {
                return parseInt((this.fltGashas.length-1) / this.paging.purPage) + 1
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
            fltGashas: function() {
                this.paging.current = Math.min(this.paging.current, this.totalPage);
            }
        }
    });
});
