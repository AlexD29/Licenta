import React, { useState } from 'react';
import './Signup.css';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';  // Import useNavigate

function Signup() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');

  const navigate = useNavigate();  // Use useNavigate hook

  const handleSubmit = async (e) => {
    e.preventDefault();

    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    const passwordRegex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$/;
    if (!passwordRegex.test(password)) {
      setError('Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, and one number');
      return;
    }

    console.log("Email:", email);
    console.log("Password:", password);


    try {
        const response = await axios.post('http://localhost:8000/api/signup', {
          email,
          password,
        });
    
        console.log('Signup successful', response.data);

        navigate('/');
    
        // Reset form and error
        setEmail('');
        setPassword('');
        setConfirmPassword('');
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
      <h2>Signup</h2>
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
        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>
        {error && <p className="error">{error}</p>}
        <button type="submit" className="btn-signup">Signup</button>
      </form>
      <div className="auth-switch">
        <p>Already have an account? <a href="/login">Login</a></p>
      </div>
    </div>
  );
}

export default Signup;
