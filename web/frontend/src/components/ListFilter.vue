<template>
  <div class="row g-1">
      <div class="col-lg-4" v-for="filter in filters_" :key="filter.key">
          <div class="input-group">
              <div class="input-group-text">
                  <input class="form-check-input me-1" type="checkbox" :id="'check-'+filter.key" v-model="filter.enabled" />
                  <label class="form-check-label" for="'check-'+filter.key">{{ filter.label }}</label>
              </div>
              <input class="form-control" type="number" v-model.number="filter.value" min="0" step="1" max="100" />
              <select class="form-select" v-model="filter.direction">
                  <option v-for="opt in diroptions_" :key="opt.val" :value="opt.val">{{ opt.text }}</option>
              </select>
          </div>
      </div>
  </div>
</template>

<script>

function greater_equal(a, b) {
    return a >= b;
}
function less_equal(a, b) {
    return a <= b;
}
function exact(a, b) {
    return a == b;
}

// interface Filter {
//     key: string,
//     label: string,
//     default_value: number,
// }

export default {
    props: ['list', 'filters'],
    emits: ['filtered_list'],
    data() {
        return {
            filters_: this.filters.map(filter => ({
                key: filter.key,
                label: filter.label,
                enabled: false,
                value: filter.default_value,
                direction: greater_equal,
            })),
            diroptions_: [
                {'text': '以上', 'val': greater_equal},
                {'text': '整', 'val': exact},
                {'text': '以下', 'val': less_equal},
            ],
        };
    },
    computed: {
        filtered_list_() {
            let res = this.list;
            for (let filter of this.filters_) {
              if (filter.enabled) {
                res = res.filter(entry => {
                    if (isNaN(parseInt(entry[filter.key]))) return false;
                    return filter.direction(entry[filter.key], filter.value);
                });
              }
            }
            return res;
        },
    },
    watch: {
        filtered_list_() {
            this.$emit('filtered_list', this.filtered_list_);
        }
    }
}

</script>
