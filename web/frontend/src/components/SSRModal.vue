<template>
  <div class="row">
    <div class="col">
        <table class="table align-middle">
            <tbody>
                <tr v-for="card in cards" :key="card.id">
                    <td>{{ showTime(card.time) }}</td>
                    <td>{{ cardType(card) }}</td>
                    <td><router-link :to="card.url"><CardIcon class="me-2" :card="fixCard(card)"/>{{ card.name }}</router-link></td>
                </tr>
            </tbody>
        </table>
    </div>
  </div>
</template>

<script>
import CardIcon from './CardIcon.vue'
import { toDate, toDateString } from '../general'

export default {
    components: {
        CardIcon,
    },
    props: ['cards', 'japanese'],
    data() {
        return {
            
        };
    },
    methods: {
        showTime(time) {
            return this.japanese ? toDateString(toDate(time), 0) : toDateString(toDate(time), 1);
        },
        fixCard: function(card) {
            return {...card, rare: parseInt(card.rare * 2 + (card.is_awaken ? 1 : 0))};
        },
        cardType(card) {
            return (card.card_type === 0) ? '常駐' : (card.card_type === 1) ? '期間限定' : 'FES限定';
        },
    },
};
</script>