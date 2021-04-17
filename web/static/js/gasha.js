function standby(obj) {
  obj.src = '/static/images/default/no_gasha_banner.png';
}


function toDate(timestamp) {
    return (!timestamp) ? null : new Date(timestamp * 1000);
}
function toDateString(time, ver) {
    // ver 0: jp, 1: as
    if (ver === 0) return (!time) ? '尚未更新' : time.toLocaleDateString("ja-JP", {timeZone: 'Japan', hour12: false})
    else return (!time) ? '尚未更新' : time.toLocaleDateString("ja-JP", {timeZone: 'Asia/Taipei', hour12: false})
}
function toDateTimeString(time, ver) {
    // ver 0: jp, 1: as
    if (ver === 0) return (!time) ? '尚未更新' : time.toLocaleString("ja-JP", {timeZone: 'Japan', hour12: false})
    else return (!time) ? '尚未更新' : time.toLocaleString("ja-JP", {timeZone: 'Asia/Taipei', hour12: false})
}

function fixData(gasha, ver) {
    if (!gasha) return;
    gasha.name = (!gasha.name) ? '未知' : gasha.name;
    gasha.start = toDateTimeString(toDate(gasha.start), ver);
    gasha.over = toDateTimeString(toDate(gasha.over), ver);
    
    for (let i in gasha.pick_up) {
        let card = gasha.pick_up[i];
        card.name = (!card.name) ? '未知' : card.name;
    }
    
    for (let i in gasha.others) {
        let card = gasha.others[i];
        card.name = (!card.name) ? '未知' : card.name;
    }
}

$(function() {
    var gasha_json = JSON.parse($('#gasha_json').text());
    for (let i = 0; i < gasha_json.length; ++i) {
        fixData(gasha_json[i], i);
    }
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            gasha: gasha_json,
            japanese: true,
            notBoth: false,
            defaultEvent: '/static/images/default/no_gasha_banner.png'
        },
        created: function() {
            this.initialize();
        },
        methods: {
            initialize: function() {
                if (!this.gasha[0] || !this.gasha[1]) this.notBoth = true;
                if (!this.gasha[0]) {
                    this.japanese = false;
                }
            },
            changeLanguage: function() {
                this.japanese = !this.japanese;
            }
        },
        computed: {
            shown: function() {
                return this.japanese ? this.gasha[0] : this.gasha[1];
            },
            panelWord: function() {
                return this.japanese ? '中文版' : '日文版'
            }
        },
        watch: {
        }
    });
});