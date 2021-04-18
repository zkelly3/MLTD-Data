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
    
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            events: events_json,
            japanese: true,
            notBoth: false,
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
            }
        },
        computed: {
            shown() {
                return this.japanese ? this.events[0] : this.events[1];
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
