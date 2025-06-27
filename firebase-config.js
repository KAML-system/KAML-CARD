// Firebase Configuration and Initialization
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, addDoc, getDocs, doc, getDoc, updateDoc, deleteDoc, query, where } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { getStorage, ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-storage.js";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBKvr6ZI_M_s_hk3Ch2ivWBuY5jSI9QxDo",
  authDomain: "kaml-membership-system.firebaseapp.com",
  projectId: "kaml-membership-system",
  storageBucket: "kaml-membership-system.firebasestorage.app",
  messagingSenderId: "1083658943439",
  appId: "1:1083658943439:web:70d45c869a0af1bdeab0ba",
  measurementId: "G-P952KYS3ZZ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);
const storage = getStorage(app);

// Export Firebase services
window.firebaseServices = {
  db,
  auth,
  storage,
  // Firestore functions
  collection,
  addDoc,
  getDocs,
  doc,
  getDoc,
  updateDoc,
  deleteDoc,
  query,
  where,
  // Auth functions
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  // Storage functions
  ref,
  uploadBytes,
  getDownloadURL
};

// Default admin credentials (for initial setup)
window.defaultAdmins = [
  { username: 'admin', password: 'kaml12024', email: 'admin@kaml.org.kw' },
  { username: 'manager', password: 'kaml123', email: 'manager@kaml.org.kw' }
];

console.log('Firebase initialized successfully');

