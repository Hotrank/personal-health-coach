import ReactDOM from 'react-dom/client';
import App from './App';
import { GoogleOAuthProvider } from '@react-oauth/google';

const clientId = '30767248244-t7n4e1o3m224bot124ntltje4ir06vei.apps.googleusercontent.com';

const container = document.getElementById('root');
const root = ReactDOM.createRoot(container);

root.render(
  <GoogleOAuthProvider clientId={clientId}>
    <App />
  </GoogleOAuthProvider>
);
