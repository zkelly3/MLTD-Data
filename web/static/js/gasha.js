function standby(obj) {
  obj.src = '/static/images/default/no_gasha_banner.png';
}

function fixData(gasha, ver) {
    if (!gasha) return;
    
    gasha.name = (!gasha.name) ? '不明' : gasha.name;
    gasha.start = toDateTimeString(toDate(gasha.start), ver);
    gasha.over = toDateTimeString(toDate(gasha.over), ver);
    
    for (let i in gasha.pick_up) {
        let card = gasha.pick_up[i];
        card.name = (!card.name) ? '不明' : card.name;
    }
    
    for (let i in gasha.others) {
        let card = gasha.others[i];
        card.name = (!card.name) ? '不明' : card.name;
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
            },
            cardClass(card) {
                var rare = parseInt(card.rare / 2);
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