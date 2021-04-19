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
                'type': {
                    'type': 'option',
                    'label': '活動類型',
                    'enabled': false,
                    'options': types_json,
                    'selected': '',
                },
            },
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
                    res = res.filter(gameEvent => {
                        return attr.selected === '' || gameEvent.event_abbr === attr.selected;
                    });
                  }
                }
                return res;
            },
            panelWord: function() {
                return this.japanese ? '中文版' : '日文版'
            }
        },
        watch: {
            /*filters(v) {
                this.$emit('input', v);
            }*/
        }
    });
});
