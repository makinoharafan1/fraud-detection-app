/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_APP_API_PORT: string;
  }
  
  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
  