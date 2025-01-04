<template>
  <div id="app">
    <router-view></router-view>
  </div>
  <!--<div id="app">
    <nav>
      <router-link to="/upload-cue">UploadCue</router-link>
      <router-link to="/upload-audio">UploadAudio</router-link>
      <router-link to="/info-cue">InfoCue</router-link>
    </nav>
    <router-view />
  </div>-->
</template>

<script>
export default {
  name: 'App',
};
</script>
