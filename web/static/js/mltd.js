function greater_equal(a, b) {
    return a >= b;
}
function less_equal(a, b) {
    return a <= b;
}
function exact(a, b) {
    return a == b;
}

$(function() {
    var idols_info = JSON.parse($('#idols_json').text());
    var app = new Vue({
        el: '#app',
        props: {
        },
        data: {
            idols: idols_info,
            idolinfo: [{'text': '', 'val': ''},
                {'text': '姓名', 'val': 'jp_name'},
                {'text': '陣營', 'val': 'i_type'},
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
        },
        created: function() {
        },
        methods: {
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
            },
            makeLink: function(id) {
                return '/idol/' + id;
            }
        },
        computed: {
            fltIdols() {
                var self = this;
                var res = self.idols.slice();
                if (self.filters.chkage) {
                    res = res.filter(idol => {
                        if (isNaN(parseInt(idol.age)) || idol.age == null) return false;
                        return self.filters.agedir(idol.age, self.filters.askage);
                    });
                }
                if (self.filters.chkheight) {
                    res = res.filter(idol => {
                        if (isNaN(parseInt(idol.height)) || idol.height == null) return false;
                        return self.filters.heightdir(idol.height, self.filters.askheight);
                    });
                }
                if (self.filters.chkweight) {
                    res = res.filter(idol => {
                        if (isNaN(parseInt(idol.weight)) || idol.weight == null) return false;
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
