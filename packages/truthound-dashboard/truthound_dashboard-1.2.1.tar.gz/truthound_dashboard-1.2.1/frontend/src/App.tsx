import { Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import { DemoBanner } from './components/DemoBanner'
import { LoadingFallback } from './components/LoadingFallback'
import Dashboard from './pages/Dashboard'
import Sources from './pages/Sources'
import SourceDetail from './pages/SourceDetail'
import Rules from './pages/Rules'
import Validations from './pages/Validations'
import History from './pages/History'
import Profile from './pages/Profile'
import Drift from './pages/Drift'
import Schedules from './pages/Schedules'
import Notifications from './pages/Notifications'
import Glossary from './pages/Glossary'
import GlossaryDetail from './pages/GlossaryDetail'
import Catalog from './pages/Catalog'
import CatalogDetail from './pages/CatalogDetail'
import Activity from './pages/Activity'

function App() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <DemoBanner />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="sources" element={<Sources />} />
          <Route path="sources/:id" element={<SourceDetail />} />
          <Route path="sources/:id/rules" element={<Rules />} />
          <Route path="sources/:id/history" element={<History />} />
          <Route path="sources/:id/profile" element={<Profile />} />
          <Route path="validations/:id" element={<Validations />} />
          <Route path="drift" element={<Drift />} />
          <Route path="schedules" element={<Schedules />} />
          <Route path="notifications" element={<Notifications />} />
          {/* Phase 5: Business Glossary & Data Catalog */}
          <Route path="glossary" element={<Glossary />} />
          <Route path="glossary/:id" element={<GlossaryDetail />} />
          <Route path="catalog" element={<Catalog />} />
          <Route path="catalog/:id" element={<CatalogDetail />} />
          <Route path="activity" element={<Activity />} />
        </Route>
      </Routes>
    </Suspense>
  )
}

export default App
