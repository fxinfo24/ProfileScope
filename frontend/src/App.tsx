// Main App Component for ProfileScope
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from '@/components/Dashboard';
import TasksList from '@/components/TasksList';
import TaskView from '@/components/TaskView';
import ResultView from '@/components/ResultView';
import Layout from '@/components/Layout';

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Layout />}>
            {/* Dashboard - Main entry point */}
            <Route index element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            
            {/* Tasks Management */}
            <Route path="/tasks" element={<TasksList />} />
            <Route path="/tasks/:id" element={<TaskView />} />
            <Route path="/tasks/:id/results" element={<ResultView />} />
            
            {/* Fallback */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>
      </div>
    </Router>
  );
};

export default App;