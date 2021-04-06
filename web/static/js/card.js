$(function() {
    var card_json = JSON.parse($('#card_json').text());
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            card: card_json,
            shown: {},
            japanese: true,
            notBoth: false,
            hasFrom: true,
            hasAwaken: true,
            panelWord: '中文版'
        },
        created: function() {
            this.initialize();
            this.updateData();
        },
        methods: {
            initialize: function() {
                var timestamp = this.card.time;
                this.card.time = timestamp ? new Date(timestamp * 1000) : null;
                var as_timestamp = this.card.astime;
                this.card.astime = as_timestamp ? new Date(as_timestamp * 1000) : null;
                this.shown.idolUrl = this.card.idol ? this.card.idol.url : '#'
                this.shown.awakenWord = this.card.is_awaken ? '覺醒前' : '覺醒後'
                this.hasAwaken = this.card.awaken ? true : false;
                
                if (!this.card.name || !this.card.cnname) this.notBoth = true;
                if (!this.card.name) japanese = false;
                
            },
            updateData: function() {
                this.shown.name = this.japanese ? this.card.name : this.card.cnname;
                this.shown.idol = (!this.card.idol) ? '未知' : this.japanese ? this.card.idol.name : this.card.idol.cnname;
                this.shown.aquireType = (!this.card.aquire) ? '未知' : this.japanese ? this.card.aquire.type.jp : this.card.aquire.type.cn;
                this.shown.aquireTitle = (!this.card.aquire) ? '未知' : this.japanese && this.card.aquire.name ? this.card.aquire.name : this.japanese ? '尚未更新' : this.card.aquire.cnname ? this.card.aquire.cnname : '尚未更新'
                this.shown.awakenName = !this.card.awaken ? '尚未更新' : this.japanese && this.card.awaken.name ? this.card.awaken.name : this.japanese ? '尚未更新' : this.card.awaken.cnname ? this.card.awaken.cnname : '尚未更新'
                this.shown.time = this.japanese && this.card.time ? this.card.time.toLocaleString('jp-JP', { timeZone: 'Japan' }) : this.japanese ? '尚未更新' : this.card.astime ? this.card.astime.toLocaleString('zh-TW', { timeZone: 'Asia/Taipei' }) : '尚未更新'
            },
            changeLanguage: function() {
                this.japanese = !this.japanese;
                this.panelWord = this.japanese ? '中文版' : '日文版'
                this.updateData();
            }
        },
        computed: {
        },
        watch: {
        }
    });
});