import React, { useState } from 'react'; // 1. 🚨 Import useState
import { useAuth } from './hooks/useAuth';
import { Login } from './Components/Auth/Login';
import Register from './Components/Auth/register'; // 2. 🚨 Import your new Register component
import Dashboard from './Components/Medallion/Dashboard';

export default function App() {
  const { user, isAuthenticated, isLoading, login, logout, error } = useAuth();
  
  // 3. 🚨 Add the toggle state here
  const [showLogin, setShowLogin] = useState(true);

  if (isLoading) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'sans-serif' }}>
        <h2>📡 Connecting to Wireless Hub...</h2>
      </div>
    );
  }

  if (isAuthenticated && user) {
    return (
      <Dashboard 
        user={user} 
        setUser={(val) => {
          if (val === null) logout(); 
        }} 
      />
    );
  }

  // 4. 🚨 Replace the bottom return with the toggle!
  return showLogin ? (
    <Login
      onLogin={login}
      onSwitchToRegister={() => setShowLogin(false)}
      error={error || null}
      isLoading={isLoading}
    />
  ) : (
    <Register
      onSwitchToLogin={() => setShowLogin(true)}
      // Because your backend automatically logs the user in upon registration,
      // we can just reload the page to let your useAuth hook grab the new session!
      setUser={(newUser) => {
         if (newUser) window.location.reload(); 
      }}
    />
  );
}