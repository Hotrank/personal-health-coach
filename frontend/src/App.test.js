beforeAll(() => {
  window.HTMLElement.prototype.scrollIntoView = jest.fn();
});


import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App, { ChatWindow } from './App';


jest.mock('@react-oauth/google', () => ({
  GoogleLogin: ({ onSuccess }) => (
    <button onClick={() => onSuccess({ credential: 'fake-token' })}>Mock Google Login</button>
  ),
  googleLogout: jest.fn(),
}));

jest.mock('jwt-decode', () => ({
  jwtDecode: () => ({ name: 'Test User' }),
}));

jest.mock('react-markdown', () => (props) => <div>{props.children}</div>);

beforeEach(() => {
  global.fetch = jest.fn();
});

afterEach(() => {
  jest.clearAllMocks();
});

describe('App', () => {
  test('renders login section initially', () => {
    render(<App />);
    expect(screen.getByText(/Mock Google Login/i)).toBeInTheDocument();
  });

  test('successful login updates UI and verifies token', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, name: 'Test User' }),
    });

    render(<App />);

    fireEvent.click(screen.getByText(/Mock Google Login/i));

    // Wait for welcome message to appear
    const welcomeText = await screen.findByText(/Welcome, Test User/i);
    expect(welcomeText).toBeInTheDocument();

    // Ensure fetch was called to verify token
    expect(fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/verify-token', expect.any(Object));
  });

  test('logout resets state and shows login again', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, name: 'Test User' }),
    });

    const { getByText, queryByText } = render(<App />);

    fireEvent.click(getByText(/Mock Google Login/i));
    await screen.findByText(/Welcome, Test User/i);

    // Click logout button
    fireEvent.click(getByText(/Logout/i));

    // Login button should be back
    expect(getByText(/Mock Google Login/i)).toBeInTheDocument();
    expect(queryByText(/Welcome, Test User/i)).not.toBeInTheDocument();
  });

  test('submitting empty chat input does nothing', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, name: 'Test User' }),
    });

    render(<App />);
    fireEvent.click(screen.getByText(/Mock Google Login/i));
    await screen.findByText(/Welcome, Test User/i);

    const input = screen.getByPlaceholderText(/Type a message/i);
    fireEvent.change(input, { target: { value: '   ' } }); // whitespace only

    fireEvent.click(screen.getByText(/Send/i));

    // No messages besides the initial
    expect(screen.queryByText(/You:/i)).not.toBeInTheDocument();
  });

  test('renders chat messages with correct sender classes and labels', () => {
    // Render ChatWindow directly for this test
    const ChatWindow = require('./App').ChatWindow;

    const messages = [
      { sender: 'user', text: 'Hello' },
      { sender: 'bot', text: 'Hi there!' },
    ];

    const { container } = render(<ChatWindow messages={messages} endRef={React.createRef()} />);

    // User message
    expect(container.querySelector('.message.user')).toHaveTextContent('You:Hello');

    // Bot message
    expect(container.querySelector('.message.bot')).toHaveTextContent('Coach:Hi there!');
  });
});
