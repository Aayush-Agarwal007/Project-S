// Request notification permission
function requestNotificationPermission() {
  // Check current permission status
  if (Notification.permission === 'granted') {
    console.log('Notification permission already granted');
    getFCMToken();
  } else {
    Notification.requestPermission().then((permission) => {
      if (permission === 'granted') {
        console.log('Notification permission granted');
        getFCMToken();
      } else {
        console.log('Notification permission denied');
      }
    }).catch((error) => {
      console.error('Error requesting notification permission:', error);
    });
  }
}

// Get FCM token
function getFCMToken() {
  const messaging = firebase.messaging();
  messaging.getToken({ vapidKey: "BAOrz7iV192QWq_zywws2HZo6sHp354aHXvbkLOTMUbr3slRfh9sdvLNLvHxSAOquwhS11Oo45Wlx1z9eypfA_E" })
    .then((currentToken) => {
      if (currentToken) {
        console.log('FCM Token:', currentToken); // Log the token for debugging
        // Save token to user's profile in Firestore
        const user = firebase.auth().currentUser ;
        if (user) {
          firebase.firestore().collection('users').doc(user.uid).set({
            fcmToken: currentToken
          }, { merge: true })
          .then(() => {
            console.log('FCM Token saved to Firestore');
          })
          .catch((error) => {
            console.error('Error saving FCM Token to Firestore:', error);
          });
        } else {
          console.log('No user is currently logged in');
        }
      } else {
        console.log('No FCM token available. Request permission to generate one.');
      }
    })
    .catch((error) => {
      console.error('Error retrieving FCM token:', error);
    });
}

// Call this when user logs in
firebase.auth().onAuthStateChanged((user) => {
  if (user) {
    requestNotificationPermission();
  }
});
