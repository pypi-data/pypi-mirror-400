import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import Scenarios from './components/Scenarios'
import Runs from './components/Runs'
import Executors from './components/Executors'
import RunCreate from './components/RunCreate'
import ScenarioDetail from './components/ScenarioDetail'
import ResultDetail from './components/ResultDetail'
import CompareResults from './components/CompareResults'
import Datasets from './components/Datasets'
import DatasetDetail from './components/DatasetDetail'
import DatasetCreate from './components/DatasetCreate'
import DatasetAnalytics from './components/DatasetAnalytics'
import GlobalReport from './components/GlobalReport'
import ReviewQueue from './components/ReviewQueue'
import PairwiseCompare from './components/PairwiseCompare'
// Temporarily disabled - judgements data available elsewhere
// import Judgements from './components/Judgements'
import ActiveJobs from './components/ActiveJobs'
import Admin from './components/admin'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import WorkerStatusFooter from './components/WorkerStatusFooter'

function App() {
  return (
    <BrowserRouter>
      <div className="h-screen bg-canvas text-text-primary flex flex-col overflow-hidden">
        {/* Top navbar */}
        <Navbar />
        
        {/* Main layout with sidebar */}
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <Sidebar />
          
          {/* Main content area */}
          <main className="flex-1 overflow-y-auto px-6 py-6 pb-16">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/scenarios" element={<Scenarios />} />
              <Route path="/runs" element={<Runs />} />
              <Route path="/executors" element={<Executors />} />
              <Route path="/datasets" element={<Datasets />} />
              <Route path="/dataset/create" element={<DatasetCreate />} />
              <Route path="/dataset/:id" element={<DatasetDetail />} />
              <Route path="/dataset/:id/analytics" element={<DatasetAnalytics />} />
              <Route path="/run/create" element={<RunCreate />} />
              <Route path="/scenario/:id" element={<ScenarioDetail />} />
              <Route path="/result/:id" element={<ResultDetail />} />
              <Route path="/compare" element={<CompareResults />} />
              {/* Temporarily disabled - judgements data available elsewhere */}
              {/* <Route path="/judgements" element={<Judgements />} /> */}
              <Route path="/jobs" element={<ActiveJobs />} />
              <Route path="/report" element={<GlobalReport />} />
              <Route path="/review" element={<ReviewQueue />} />
              <Route path="/pairwise" element={<PairwiseCompare />} />
              <Route path="/admin" element={<Admin />} />
            </Routes>
          </main>
        </div>
        
        {/* Footer */}
        <WorkerStatusFooter />
      </div>
    </BrowserRouter>
  )
}

export default App
