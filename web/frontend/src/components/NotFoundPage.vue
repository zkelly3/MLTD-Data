<template>
<MainPage :pageNotFound="true">
</MainPage>
</template>

<script>
import MainPage from './MainPage.vue'

export default {
    name: 'NotFoundPage',
    components: {
        MainPage,
    },
};
</script>