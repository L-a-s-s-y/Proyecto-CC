<template>
    <div>
      <h2>Upload Audio File</h2>
      <form @submit.prevent="uploadAudio">
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
        if (this.file.type.substring(0,5)=="audio"){
          const formData = new FormData();
          formData.append('file', this.file);
    
          try {
            const res = await axios.post(`${backend}/audio`, formData, {
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
        } else {
          alert("The file must be an audio file!")
          this.$router.push(`/upload-audio/${this.cueName}`);
        }
      },
    },
  };
  </script>
  