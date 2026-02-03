import { signInWithEmailAndPassword } from "firebase/auth";
import { getFirebaseAuth } from "../firebase";

export async function firebaseEmailLogin(email, password) {
  const auth = getFirebaseAuth();
  if (!auth) {
    throw new Error("Firebase auth not configured");
  }
  const userCred = await signInWithEmailAndPassword(auth, email, password);
  const idToken = await userCred.user.getIdToken();
  return { idToken, user: userCred.user };
}
