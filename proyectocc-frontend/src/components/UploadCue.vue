<template>
    <div>
      <h2>Upload .cue File</h2>
      <form @submit.prevent="uploadCue">
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
        response: null,
      };
    },
    methods: {
      handleFileChange(event) {
        this.file = event.target.files[0];
      },
      async uploadCue() {
        const formData = new FormData();
        formData.append('file', this.file);
  
        try {
          const res = await axios.post(`${backend}/cue`, formData, {
            headers: { 'Content-Type': 'multipart/form-data',},
          });
          this.response = res.data;
          this.$router.push(`/upload-audio/${this.response['filename']}`);
        } catch (err) {
          console.log(err);
          this.response = { error: 'Error uploading .cue file' };
        }
      },
    },
  };
  </script>
  