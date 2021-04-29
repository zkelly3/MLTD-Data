<template>
<div class="row g-1">
    <div class="col-lg-2">
        <select class="form-select" v-model.number="paging.purPage">
        <option v-for="opt in paging.onePageList" :key="opt" :value="opt">{{ opt }}</option>
        </select>
    </div>
    <nav aria-label="pagination">
        <ul class="pagination justify-content-end">
        <li :class="{'page-item': true, disabled: calcPagination.noPrev}">
            <button class="page-link" v-on:click="prevPage()" :aria-disabled="calcPagination.noPrev">Previous</button>
        </li>
        <li v-for="page in calcPagination.pages" :key="page.val" :class="{'page-item': true, active: page.isCurrent}">
            <span class="page-link" v-if="page.isCurrent">{{ page.val }}</span>
            <button class="page-link" v-on:click="changePage(page.val)" v-else>{{ page.val }}</button>
        </li>
        <li :class="{'page-item': true, disabled: calcPagination.noNext}">
            <button class="page-link" v-on:click="nextPage()" :aria-disabled="calcPagination.noNext">Next</button>
        </li>
        </ul>
    </nav>
</div>
</template>

<script>
export default {
    props: ['list', 'purPageInit', 'currentInit'],
    emits: ['filtered_list'],
    data() {
        return {
            paging: {
                onePageList: [10, 20, 50, 100],
                purPage: this.purPageInit,
                current: this.currentInit,
            },
        };
    },
    methods: {
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
        totalPage() {
            return parseInt((this.list.length-1) / this.paging.purPage) + 1
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
        pageFltData() {
            var self = this;
            var res = self.list.slice();
            var first = (self.paging.current-1) * (self.paging.purPage);
            var last = (self.paging.current) * (self.paging.purPage);
            res = res.filter((e, index) => {
                return (index >= first) && (index < last);
            });
            return res;
        },
    },
    watch: {
        pageFltData() {
            this.paging.current = Math.min(this.paging.current, this.totalPage);
            this.$emit('filtered_list', this.pageFltData);
        }
    }
}
</script>