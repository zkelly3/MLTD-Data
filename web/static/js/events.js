function fixData(events, ver) {
    for (let i in events) {
        events[i].name = (!events[i].name) ? '不明' : events[i].name;
        events[i].start = toDateString(toDate(events[i].start), ver);
        events[i].over = toDateString(toDate(events[i].over), ver);
    }    
}

$(function() {
    var events_json = JSON.parse($('#events_json').text());
    for (let i = 0; i < events_json.length; ++i) {
        fixData(events_json[i], i);
    }
    var types_json = JSON.parse($('#types_json').text());
    
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            events: events_json,
            japanese: true,
            notBoth: false,
            filters: {
                eventType: {
                    'type': 'option',
                    'label': '活動類型',
                    'enabled': false,
                    'options': types_json,
                    'selected': '',
                },
                eventName: {
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
                if (!this.events[0] || !this.events[1]) this.notBoth = true;
                if (!this.events[0]) this.japanese = false;
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
                return this.japanese ? this.events[0] : this.events[1];
            },
            fltEvents() {
                var self = this;
                var res = self.shown.slice();
                for (let key in self.filters) {
                  attr = self.filters[key]
                  if (attr.enabled) {
                    if (attr.type === 'option') {
                        res = res.filter(gameEvent => {
                            return attr.selected === '' || gameEvent.event_abbr === attr.selected;
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
            pageFltEvents() {
                var self = this;
                var res = self.fltEvents.slice();
                var first = (self.paging.current-1) * (self.paging.purPage);
                var last = (self.paging.current) * (self.paging.purPage);
                res = res.filter((gameEvent, index) => {
                    return (index >= first) && (index < last);
                });
                return res;
            },
            panelWord() {
                return this.japanese ? '中文版' : '日文版'
            },
            totalPage() {
                return parseInt((this.fltEvents.length-1) / this.paging.purPage) + 1
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
            fltEvents: function() {
                this.paging.current = Math.min(this.paging.current, this.totalPage);
            }
        }
    });
});
