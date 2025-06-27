// Authentication system for KAML membership system

class AuthSystem {
    constructor() {
        this.currentUser = null;
        this.firebaseReady = false;
        this.init();
    }

    async init() {
        // Wait for Firebase to be ready
        await this.waitForFirebase();
        
        // Check if user is already logged in
        this.checkAuthState();
    }

    waitForFirebase() {
        return new Promise((resolve) => {
            const checkFirebase = () => {
                if (window.firebaseServices) {
                    this.firebaseReady = true;
                    resolve();
                } else {
                    setTimeout(checkFirebase, 100);
                }
            };
            checkFirebase();
        });
    }

    checkAuthState() {
        const { auth, onAuthStateChanged } = window.firebaseServices;
        
        onAuthStateChanged(auth, (user) => {
            this.currentUser = user;
            this.updateUI();
        });
    }

    async signInWithEmail(email, password) {
        if (!this.firebaseReady) {
            throw new Error('Firebase not ready');
        }

        const { auth, signInWithEmailAndPassword } = window.firebaseServices;
        
        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            this.currentUser = userCredential.user;
            return userCredential;
        } catch (error) {
            console.error('Sign in error:', error);
            throw this.getArabicErrorMessage(error.code);
        }
    }

    async signOut() {
        if (!this.firebaseReady) return;

        const { auth, signOut } = window.firebaseServices;
        
        try {
            await signOut(auth);
            this.currentUser = null;
            window.location.href = './login.html';
        } catch (error) {
            console.error('Sign out error:', error);
        }
    }

    async createAdminAccount(email, password, adminData) {
        if (!this.firebaseReady) {
            throw new Error('Firebase not ready');
        }

        const { auth, createUserWithEmailAndPassword, db, doc, setDoc } = window.firebaseServices;
        
        try {
            // Create user account
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;

            // Save admin data to Firestore
            await setDoc(doc(db, 'admins', user.uid), {
                ...adminData,
                uid: user.uid,
                email: email,
                role: 'admin',
                createdAt: new Date(),
                isActive: true
            });

            return userCredential;
        } catch (error) {
            console.error('Create admin error:', error);
            throw this.getArabicErrorMessage(error.code);
        }
    }

    async isAdmin(user = null) {
        if (!this.firebaseReady) return false;
        
        const currentUser = user || this.currentUser;
        if (!currentUser) return false;

        const { db, doc, getDoc } = window.firebaseServices;
        
        try {
            const adminDoc = await getDoc(doc(db, 'admins', currentUser.uid));
            return adminDoc.exists() && adminDoc.data().isActive;
        } catch (error) {
            console.error('Check admin error:', error);
            return false;
        }
    }

    async requireAuth(redirectTo = './login.html') {
        if (!this.currentUser) {
            window.location.href = redirectTo;
            return false;
        }
        return true;
    }

    async requireAdmin(redirectTo = './login.html') {
        if (!await this.requireAuth(redirectTo)) return false;
        
        if (!await this.isAdmin()) {
            window.location.href = redirectTo;
            return false;
        }
        return true;
    }

    updateUI() {
        // Update UI based on auth state
        const authElements = document.querySelectorAll('[data-auth]');
        const adminElements = document.querySelectorAll('[data-admin]');
        
        authElements.forEach(element => {
            const authType = element.getAttribute('data-auth');
            if (authType === 'required' && !this.currentUser) {
                element.style.display = 'none';
            } else if (authType === 'guest' && this.currentUser) {
                element.style.display = 'none';
            } else {
                element.style.display = '';
            }
        });

        // Check admin elements
        if (this.currentUser) {
            this.isAdmin().then(isAdmin => {
                adminElements.forEach(element => {
                    element.style.display = isAdmin ? '' : 'none';
                });
            });
        } else {
            adminElements.forEach(element => {
                element.style.display = 'none';
            });
        }
    }

    getArabicErrorMessage(errorCode) {
        const errorMessages = {
            'auth/user-not-found': 'المستخدم غير موجود',
            'auth/wrong-password': 'كلمة المرور غير صحيحة',
            'auth/email-already-in-use': 'البريد الإلكتروني مستخدم بالفعل',
            'auth/weak-password': 'كلمة المرور ضعيفة',
            'auth/invalid-email': 'البريد الإلكتروني غير صحيح',
            'auth/too-many-requests': 'تم تجاوز عدد المحاولات المسموح',
            'auth/network-request-failed': 'خطأ في الاتصال بالشبكة',
            'auth/invalid-credential': 'بيانات الدخول غير صحيحة'
        };
        
        return errorMessages[errorCode] || 'حدث خطأ غير متوقع';
    }

    // Utility methods
    getCurrentUser() {
        return this.currentUser;
    }

    isLoggedIn() {
        return !!this.currentUser;
    }
}

// Initialize auth system
window.authSystem = new AuthSystem();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthSystem;
}

