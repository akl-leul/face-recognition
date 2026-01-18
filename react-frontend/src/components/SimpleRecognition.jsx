import React, { useState, useEffect } from 'react';
import {
  Camera,
  User,
  UserPlus,
  AlertCircle,
  Check,
  Loader,
  CameraOff
} from 'lucide-react';

import {
  simpleRecognize,
  simpleEnroll,
  getSimpleStatus,
  startCamera,
  stopCamera
} from '../utils/api';

export function SimpleRecognitionComponent() {
  const [cameraActive, setCameraActive] = useState(false);
  const [userName, setUserName] = useState('');
  const [recognitionResult, setRecognitionResult] = useState('');
  const [faceImage, setFaceImage] = useState('');
  const [loading, setLoading] = useState(false);
  const [enrolledUsers, setEnrolledUsers] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await getSimpleStatus();
      if (response.data.success) {
        setCameraActive(response.data.camera_active);
        setEnrolledUsers(response.data.users || []);
      }
    } catch (err) {
      console.error('Error fetching status:', err);
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

  const handleStartCamera = async () => {
    try {
      setLoading(true);
      await startCamera();
      setCameraActive(true);
      setRecognitionResult('');
      setFaceImage('');
    } catch (err) {
      setError('Failed to start camera: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleStopCamera = async () => {
    try {
      setLoading(true);
      await stopCamera();
      setCameraActive(false);
      setRecognitionResult('');
      setFaceImage('');
    } catch (err) {
      setError('Failed to stop camera: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleRecognize = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const response = await simpleRecognize();

      if (response.data.success) {
        setRecognitionResult(response.data.result);
        setFaceImage(response.data.face_image);
        setSuccess('Face processed successfully');

        // Speak if recognized
        if (response.data.name && response.data.name !== 'Unknown') {
          speakName(response.data.name);
        }
      } else {
        setRecognitionResult(response.data.result);
      }
    } catch (err) {
      setError('Recognition failed: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async () => {
    if (!userName.trim()) {
      setError('Please enter a user name');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const response = await simpleEnroll(userName);

      if (response.data.success) {
        setSuccess(response.data.message);
        setUserName('');
        await fetchStatus();
      } else {
        setError(response.data.error || 'Enrollment failed');
      }
    } catch (err) {
      setError('Enrollment failed: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-4 py-6">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Camera & Recognition */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center mb-6">
                  <Camera className="h-8 w-8 text-blue-600 mr-3" />
                  <h1 className="text-2xl font-bold text-gray-900">
                    Simple Face Recognition
                  </h1>
                </div>

                <div className="flex space-x-4 mb-6">
                  {!cameraActive ? (
                    <button
                      onClick={handleStartCamera}
                      disabled={loading}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md"
                    >
                      {loading ? (
                        <>
                          <Loader className="w-4 h-4 mr-2 animate-spin" />
                          Starting...
                        </>
                      ) : (
                        <>
                          <Camera className="w-4 h-4 mr-2" />
                          Start Camera
                        </>
                      )}
                    </button>
                  ) : (
                    <button
                      onClick={handleStopCamera}
                      disabled={loading}
                      className="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md"
                    >
                      {loading ? (
                        <>
                          <Loader className="w-4 h-4 mr-2 animate-spin" />
                          Stopping...
                        </>
                      ) : (
                        <>
                          <Camera className="w-4 h-4 mr-2" />
                          Stop Camera
                        </>
                      )}
                    </button>
                  )}

                  <button
                    onClick={handleRecognize}
                    disabled={!cameraActive || loading}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
                  >
                    {loading ? (
                      <>
                        <Loader className="w-4 h-4 mr-2 animate-spin" />
                        Recognizing...
                      </>
                    ) : (
                      <>
                        <User className="w-4 h-4 mr-2" />
                        Recognize Face
                      </>
                    )}
                  </button>
                </div>

                <div className="bg-gray-100 rounded-lg overflow-hidden mb-6">
                  {cameraActive ? (
                    <img
                      src="/video_feed"
                      className="w-full h-96 object-cover"
                      alt="Camera Feed"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-96">
                      <CameraOff className="h-12 w-12 text-gray-400" />
                    </div>
                  )}
                </div>

                {recognitionResult && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-blue-700">{recognitionResult}</p>
                    {faceImage && (
                      <img
                        src={faceImage}
                        alt="Detected Face"
                        className="w-32 h-32 mt-4 rounded-lg"
                      />
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Status */}
          <div className="space-y-6">
            <div className="bg-white shadow rounded-lg p-6">
              <p>Camera: {cameraActive ? 'Active' : 'Inactive'}</p>
              <p>Enrolled Users: {enrolledUsers.length}</p>
            </div>
          </div>
        </div>

        {error && (
          <div className="fixed bottom-4 right-4 bg-red-50 border p-4 rounded-lg">
            <AlertCircle className="inline mr-2" />
            {error}
          </div>
        )}

        {success && (
          <div className="fixed bottom-4 right-4 bg-green-50 border p-4 rounded-lg">
            <Check className="inline mr-2" />
            {success}
          </div>
        )}
      </div>
    </div>
  );
}

export default SimpleRecognitionComponent;
