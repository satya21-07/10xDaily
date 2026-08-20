import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.dailyos.app',
  appName: '10xDaily',
  webDir: 'dist/mobile-app/browser',
  plugins: {
    GoogleAuth: {
      scopes: ['profile', 'email'],
      serverClientId: '663497949911-ntqrrseps5dc6o8oe7972mor0259af94.apps.googleusercontent.com',
      forceCodeForRefreshToken: true,
    }
  },
  server: {
    cleartext: true,
    androidScheme: 'http'
  }
};

export default config;
