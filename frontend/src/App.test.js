import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock external components and dependencies
jest.mock('@react-oauth/google', () => ({
  GoogleLogin: ({ onSuccess, onError }) => (
    <button onClick={onSuccess}>Mock Google Login</button>
  ),
  googleLogout: jest.fn(),
}));

jest.mock('jwt-decode', () => ({
  jwtDecode: () => ({ name: 'Test User' }),
}));

// Suppress console.error from ReactMarkdown missing props in test
jest.mock('react-markdown', () => (props) => <div>{props.children}</div>);

describe('App', () => {
  test('renders login section initially', () => {
    render(<App />);
    expect(screen.getByText(/Mock Google Login/i)).toBeInTheDocument();
  });
});
