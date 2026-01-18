import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { CameraComponent as Camera, UsersComponent as Users, Dashboard, SettingsComponent as Settings, EnrollmentComponent, SimpleRecognitionComponent } from './components/index';
import { Camera as CameraIcon, Users as UsersIcon, Layout } from 'lucide-react';
import { startCamera, stopCamera, getSystemStatus, getEnrolledUsers } from './utils/api';
import './App.css';

function AppContent() {
  const location = useLocation();
  const [systemStatus, setSystemStatus] = useState({
    cameraActive: false,
    recognitionActive: false,
    enrolledUsers: 0,
    lastRecognition: null
  });
  const [enrolledUsers, setEnrolledUsers] = useState([]);
  const lastSpokenName = useRef(null);

  useEffect(() => {
    fetchSystemStatus();
    fetchEnrolledUsers();
    const interval = setInterval(fetchSystemStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await getSystemStatus();
      setSystemStatus(response.data);

      const latest = response.data.latest_recognition;
      if (latest && latest.name && latest.name !== lastSpokenName.current) {
        speakName(latest.name);
        lastSpokenName.current = latest.name;
        setTimeout(() => { lastSpokenName.current = null; }, 5000);
      }
    } catch (error) {
      console.error('Error fetching system status:', error);
    }
  };

  const fetchEnrolledUsers = async () => {
    try {
      const response = await getEnrolledUsers();
      const users = Array.isArray(response.data) ? response.data : (response.data.users || []);
      setEnrolledUsers(users);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const handleEnrollmentComplete = () => {
    fetchEnrolledUsers();
  };

  const handleStartCamera = async () => {
    try {
      await startCamera();
      await fetchSystemStatus();
    } catch (error) {
      console.error('Error starting camera:', error);
    }
  };

  const handleStopCamera = async () => {
    try {
      await stopCamera();
      await fetchSystemStatus();
    } catch (error) {
      console.error('Error stopping camera:', error);
    }
  };

  const speakName = (name) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(`Welcome to my face detection system, Welcome again, , ${name}`);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      window.speechSynthesis.speak(utterance);
    }
  };

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-blue-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <CameraIcon className="w-6 h-6 mr-2" />
                <h1 className="text-xl font-bold">Face Recognition System</h1>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${systemStatus.cameraActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  Camera: {systemStatus.cameraActive ? 'Active' : 'Inactive'}
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {systemStatus.cameraActive ? (
                <button onClick={handleStopCamera} className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                  Stop Camera
                </button>
              ) : (
                <button onClick={handleStartCamera} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                  Start Camera
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <Link
              to="/"
              className={`px-3 py-4 rounded-md text-sm font-medium ${isActive('/') ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
            >
              <Layout className="w-5 h-5 inline mr-2" />
              Dashboard
            </Link>

            <Link
              to="/camera"
              className={`px-3 py-4 rounded-md text-sm font-medium ${isActive('/camera') ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
            >
              <CameraIcon className="w-5 h-5 inline mr-2" />
              Camera
            </Link>

            <Link
              to="/users"
              className={`px-3 py-4 rounded-md text-sm font-medium ${isActive('/users') ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
            >
              <UsersIcon className="w-5 h-5 inline mr-2" />
              Users
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {systemStatus.lastRecognition && (
          <div className="mb-6 bg-green-50 border-l-4 border-green-400 p-4 rounded-md">
            <div className="flex">
              <div className="flex-shrink-0">
                <UsersIcon className="h-5 w-5 text-green-400" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">Recognition Successful!</h3>
                <div className="mt-2 text-sm text-green-700">
                  <p className="font-medium">Identity: {systemStatus.lastRecognition.identity}</p>
                  <p>Confidence: {systemStatus.lastRecognition.confidence}</p>
                  <p>Time: {systemStatus.lastRecognition.timestamp}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/camera" element={<Camera />} />
          <Route path="/users" element={<Users />} />
          <Route path="/enrollment" element={<EnrollmentComponent onEnrollmentComplete={handleEnrollmentComplete} />} />
          <Route path="/simple-recognition" element={<SimpleRecognitionComponent />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
