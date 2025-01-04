import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import UploadCue from './components/UploadCue.vue';
import UploadAudio from './components/UploadAudio.vue';
import InfoCue from './components/InfoCue.vue';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/upload-cue', component: UploadCue },
        { path: '/upload-audio/:cueID', component: UploadAudio },
        { path: '/info-cue/:cueID', component: InfoCue },
    ]
});
const app = createApp(App);

app.use(router)

app.mount('#app');
