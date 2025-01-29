<template>
  <div class="container">
    <div class="left-panel">
      <h2>Get Cue Information</h2>
      <form @submit.prevent="fetchInfo">
        <!--<input type="text" v-model="cueName" placeholder="Cue name" />-->
        <button type="submit">Fetch Info</button>
      </form>
      <br/>
      <h2>Download your files</h2>
      <form @submit.prevent="getFiles">
        <!--<input type="text" v-model="cueName" placeholder="Cue name" />-->
        <button type="submit">Get Files</button>
      </form>
      <br/>
      <h2><a href="/upload-cue/">Subir otra CUE</a></h2>
    </div>
      <div class="right-panel" v-if="response">
        <h3>Album Information:</h3>
        <p><strong>Album:</strong> {{ response.Album }}</p>
        <p><strong>DISCID:</strong> {{ response.DISCID }}</p>
        <p><strong>Fecha:</strong> {{ response.Fecha }}</p>
        <p><strong>Género:</strong> {{ response.Genero }}</p>
        <p><strong>Intérpretes:</strong> {{ response.Interpretes }}</p>
        <p><strong>Catálogo:</strong> {{ response.catalog }}</p>
        <p><strong>Archivo CUE:</strong> {{ response.cue_file }}</p>
        
        <h3>Tracks:</h3>
        <ul>
          <li v-for="(track, index) in response.tracks" :key="index">
            {{ track }}
          </li>
        </ul>
      </div>
  </div>
</template>
  
  <script>
  import axios from 'axios';
  import { backend } from '@/app.config';
  
  export default {
    data() {
      return {
        cueName: '',
        response: null,
      };
    },
    created(){
        this.cueName = this.$route.params.cueID
        this.fetchInfo()
    },
    methods: {
      async fetchInfo() {
        try {
          const res = await axios.get(`${backend}/info/${this.cueName}`);
          this.response = res.data;
        } catch (err) {
          console.error(err);
          this.response = { error: 'Error fetching cue information' };
        }
      },
      async getFiles() {
          try {
            const response = await axios.get(`${backend}/download/${this.cueName}`, {
              responseType: "blob", // Asegura que el archivo se reciba como blob
            });

            // Obtener el nombre del archivo del encabezado Content-Disposition
            const contentDisposition = response.headers["content-disposition"];
            let fileName = "downloaded_file"; // Valor por defecto

            if (contentDisposition) {
              const matches = contentDisposition.match(/filename="?([^"]+)"?/);
              if (matches && matches[1]) {
                fileName = matches[1];
              }
            }

            // Crear una URL para el archivo descargado
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement("a");
            link.href = url;

            // Establecer el nombre del archivo para la descarga
            link.setAttribute("download", fileName);
            document.body.appendChild(link);
            link.click();
            link.remove();

            this.message = `File "${fileName}" downloaded successfully!`;
        } catch (error) {
          console.error("Error downloading the file:", error);
          this.message =
            "There was an error downloading the file. Please try again later.";
        }
      },
    },
  };
  </script>


<style scoped>
.container {
  display: flex;
  justify-content: space-between;
}
.left-panel {
  margin-left: 16px;
  width: 40%;
}
.right-panel {
  width: 55%;
  border-left: 2px solid #ccc;
  padding-left: 20px;
}
</style>