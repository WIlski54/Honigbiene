import { defineConfig } from 'vite';

export default defineConfig({
  // Relative Pfade: läuft auch unter einem Unterpfad (z. B. /static/film/bienenmodell/ im Arbeitsblatt).
  base: './',
  server: { host: '127.0.0.1', port: 5173, strictPort: true },
  build: {
    rollupOptions: {
      output: { manualChunks: { three: ['three', 'three/addons/loaders/GLTFLoader.js', 'three/addons/controls/OrbitControls.js', 'three/addons/environments/RoomEnvironment.js'] } },
    },
  },
});
