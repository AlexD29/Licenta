import React, { useState } from 'react';
import './Login.css';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';  // Import useNavigate

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const navigate = useNavigate();  // Use useNavigate hook

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    if (!password) {
      setError('Password is required');
      return;
    }

    try {
        const response = await axios.post('http://localhost:8000/api/login', {
          email,
          password,
        });
    
        console.log('Login successful', response.data);

        // Navigate to "/"
        navigate('/');
    
        // Reset form and error
        setEmail('');
        setPassword('');
        setError('');
      } catch (error) {
        if (error.response && error.response.data) {
          setError(error.response.data.error || 'An error occurred');
        } else {
          setError('An error occurred');
        }
      }
    };

  return (
    <div className="auth-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="text"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <p className="error">{error}</p>}
        <button type="submit" className="btn-login">Login</button>
      </form>
      <div className="auth-switch">
        <p>Don't have an account? <a href="/signup">Signup</a></p>
      </div>
    </div>
  );
}

export default Login;
