import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { ThemeProvider } from './components/theme-provider'
import { Toaster } from './components/ui/toaster'
import { IntlayerProviderWrapper } from './providers'
import './index.css'

async function enableMocking(): Promise<void> {
  // Only enable in mock mode
  if (import.meta.env.VITE_MOCK_API !== 'true') {
    return
  }

  const { initMockWorker } = await import('./mocks')
  await initMockWorker()
}

enableMocking().then(() => {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <IntlayerProviderWrapper>
        <BrowserRouter>
          <ThemeProvider defaultTheme="dark" storageKey="truthound-theme">
            <App />
            <Toaster />
          </ThemeProvider>
        </BrowserRouter>
      </IntlayerProviderWrapper>
    </React.StrictMode>
  )
})
