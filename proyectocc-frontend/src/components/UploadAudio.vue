<template>
    <div>
      <h2>Upload Audio File</h2>
      <form @submit.prevent="uploadAudio">
        <!--<input type="text" v-model="cueName" placeholder="Cue name" />-->
        <input type="file" @change="handleFileChange" />
        <button type="submit">Upload</button>
      </form>
      <div v-if="response">
        <h3>Response:</h3>
        <pre>{{ response }}</pre>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { backend } from '@/app.config';
  
  export default {
    data() {
      return {
        file: null,
        cueName: '',
        response: null,
      };
    },
    created(){
        this.cueName = this.$route.params.cueID
    },
    methods: {
      handleFileChange(event) {
        this.file = event.target.files[0];
      },
      async uploadAudio() {
        const formData = new FormData();
        formData.append('file', this.file);

        console.log(`${backend}/audio`)
  
        try {
            //const res = await axios.post(`${process.env.VUE_APP_API_MACHINE}/audio`, formData, {
            const res = await axios.post(`${backend}/audio`, formData, {
            //const res = await axios.post(`http://172.18.0.2:5000/audio`, formData, {
            //const res = await axios.post(`http://localhost:5000/audio`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
          this.response = res.data;
          this.$router.push(`/info-cue/${this.cueName}`);
          console.log(this.response['filename'])
          console.log(this.response)
        } catch (err) {
          console.error(err);
          this.response = { error: 'Error uploading audio file' };
        }
      },
    },
  };
  </script>
  