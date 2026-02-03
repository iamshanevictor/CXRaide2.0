// Firebase bootstrap (not wired yet).
// Fill VITE_FIREBASE_* env vars (see client/.env.firebase.example) and import when ready.

import { initializeApp, getApps } from "firebase/app";
import { getAuth } from "firebase/auth";

function _getEnv(key) {
  return (
    (typeof window !== "undefined" && window.__ENV__ && window.__ENV__[key]) ||
    import.meta.env?.[key]
  );
}

const firebaseConfig = {
  apiKey: _getEnv("VITE_FIREBASE_API_KEY"),
  authDomain: _getEnv("VITE_FIREBASE_AUTH_DOMAIN"),
  projectId: _getEnv("VITE_FIREBASE_PROJECT_ID"),
  storageBucket: _getEnv("VITE_FIREBASE_STORAGE_BUCKET"),
  messagingSenderId: _getEnv("VITE_FIREBASE_MESSAGING_SENDER_ID"),
  appId: _getEnv("VITE_FIREBASE_APP_ID"),
  measurementId: _getEnv("VITE_FIREBASE_MEASUREMENT_ID"),
};

export function getFirebaseApp() {
  const hasConfig = Object.values(firebaseConfig).every(Boolean);
  if (!hasConfig) {
    console.warn("[Firebase] Config missing; skipping init");
    return null;
  }
  if (!getApps().length) {
    return initializeApp(firebaseConfig);
  }
  return getApps()[0];
}

export function getFirebaseAuth() {
  const app = getFirebaseApp();
  return app ? getAuth(app) : null;
}
