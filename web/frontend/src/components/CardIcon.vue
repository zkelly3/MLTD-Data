<template>
  <div class="card_icon" :class="cardClass">
    <img :src="card.img_url"/>
  </div>
</template>

<script>
export default {
    name: 'CardIcon',
    props: ['card'],
    computed: {
        cardClass() {
            var rare = parseInt(this.card.rare / 2);
            switch (rare) {
                case 3:
                    return 'card_ssr';
                case 2:
                    return 'card_sr';
                case 1:
                    return 'card_r';
            }
            if (rare == 0) {
                switch (this.card.idol_type) {
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
    }
}
</script>

<style lang="scss">
@import "/src/variables.scss";

.card_icon {
  display: inline-block;
  position: relative;
  height: 50px;
  width: 50px;
}
.card_icon img {
  height: 100%;
  width: 100%;
}
.card_icon:after {
  content: '';
  position: absolute;
  height: 100%;
  width: 100%;
  left: 0;
  top: 0;
  z-index: 100;
  background-size: contain;
}
.card_ssr:after {
  background-image: url('/static/images/card_icon_mark/rare_SSR.png');
}
.card_sr:after {
  background-image: url('/static/images/card_icon_mark/rare_SR.png');
}
.card_r:after {
  background-image: url('/static/images/card_icon_mark/rare_R.png');
}
.card_n_pr:after {
  border: 2px $princess-color solid;
  border-radius: 5px;
}
.card_n_fa:after {
  border: 2px $fairy-color solid;
  border-radius: 5px;
}
.card_n_an:after {
  border: 2px $angel-color solid;
  border-radius: 5px;
}
</style>
