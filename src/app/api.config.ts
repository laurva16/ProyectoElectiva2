// src/app/api.config.ts
export const API_CONFIG = {
  AWS_URL: 'https://8g12ab6b23.execute-api.us-east-1.amazonaws.com/dev/api',
  LOCAL_URL: 'http://localhost:5000/api',
  
  get BASE_URL(): string {
    return this.AWS_URL;  // ← Usar AWS
  }
};