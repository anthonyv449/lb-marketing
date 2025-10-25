import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import "./index.css";
import SimpleMarketingDashboard from './simpleUI.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SimpleMarketingDashboard />
  </StrictMode>,
)
