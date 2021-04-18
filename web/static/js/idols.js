function greater_equal(a, b) {
    return a >= b;
}
function less_equal(a, b) {
    return a <= b;
}
function exact(a, b) {
    return a == b;
}

function fixData(idols) {
    for (let i in idols) {
        let idol = idols[i];
        
        let toDelete = []
        for (let key in idol) {
            if (idol[key] === null) toDelete.push(key);
        }
        for (let i in toDelete) delete idol[toDelete[i]];
        
        idols[i] = $.extend({
            name: '不明',
            idol_type: '不明',
            age: '不明',
            height: '不明',
            weight: '不明'
        }, idol);
    }    
}

$(function() {
    var idols_json = JSON.parse($('#idols_json').text());
    for (let i = 0; i < idols_json.length; ++i) {
        fixData(idols_json[i]);
    }
    
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            idols: idols_json,
            idolinfo: [{'text': '姓名', 'val': 'name'},
                {'text': '陣營', 'val': 'idol_type'},
                {'text': '年齡', 'val': 'age'},
                {'text': '身高', 'val': 'height'},
                {'text': '體重', 'val': 'weight'}],
            sorts: {
                'key': '',
                'reverse': false
            },
            filters: {
                'chkage': false,
                'chkheight': false,
                'chkweight': false,
                'askage': 18,
                'askheight': 150,
                'askweight': 40,
                'agedir': greater_equal,
                'heightdir': greater_equal,
                'weightdir': greater_equal
            },
            diroptions: [
                {'text': '以上', 'val': greater_equal},
                {'text': '整', 'val': exact},
                {'text': '以下', 'val': less_equal},
            ],
            japanese: true,
            notBoth: false,
        },
        created: function() {
            this.initialize();
        },
        methods: {
            initialize: function() {
                if (!this.idols[0] || !this.idols[1]) this.notBoth = true;
                if (!this.idols[0]) this.japanese = false;
            },
            changeLanguage: function() {
                this.japanese = !this.japanese;
            },
            sortKey: function(key) {
                if (this.sorts.key == key) {
                    if (this.sorts.reverse) {
                        this.sorts.key = '';
                        this.sorts.reverse = false;
                    }
                    else this.sorts.reverse = true;
                }
                else {
                    this.sorts.key = key;
                    this.sorts.reverse = false;
                }
            }
        },
        computed: {
            shown() {
                return this.japanese ? this.idols[0] : this.idols[1];
            },
            panelWord: function() {
                return this.japanese ? '中文版' : '日文版'
            }, 
            fltIdols() {
                var self = this;
                var res = self.shown.slice();
                if (self.filters.chkage) {
                    res = res.filter(idol => {
                        if (isNaN(parseInt(idol.age))) return false;
                        return self.filters.agedir(idol.age, self.filters.askage);
                    });
                }
                if (self.filters.chkheight) {
                    res = res.filter(idol => {
                        if (isNaN(parseInt(idol.height))) return false;
                        return self.filters.heightdir(idol.height, self.filters.askheight);
                    });
                }
                if (self.filters.chkweight) {
                    res = res.filter(idol => {
                        if (isNaN(parseInt(idol.weight))) return false;
                        return self.filters.weightdir(idol.weight, self.filters.askweight);
                    });
                }
                return res;
            },
            sortedIdols() {
                var self = this;
                var res = self.fltIdols.slice();
                
                if (self.sorts.key === '') return res;
                else {
                    return res.sort(function(a, b) {
                        let key = self.sorts.key;
                        let reverse = self.sorts.reverse;
                        
                        let ak = a[key];
                        let bk = b[key];
                        let r = reverse ? -1 : 1;
                        return ((ak > bk) ? (1 * r) : (ak < bk) ? (-1 * r) : 0); 
                    });
                }
            }
        },
        watch: {
            /*filters(v) {
                this.$emit('input', v);
            }*/
        }
    });
});
