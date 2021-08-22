<template>
    <div id="app" class="min-vh-100">
        <Nav/>
        <br>
        <router-view class="pb-5"/>
        <Footer/>
    </div>
</template>

<script>

import Nav from "./components/Nav";
import Footer from "./components/Footer";

export default {
    name: 'App',
    components: {
        Footer,
        Nav,
    },
    watch: {
        $route: {
            immediate: true,
            handler(to) {
                document.title = to.meta.title || 'Cards Against Online';
            }
        }
    }
}
</script>
