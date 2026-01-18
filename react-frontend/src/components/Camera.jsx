import React, { useState, useEffect, useRef } from 'react';
import { Camera as CameraIcon, CameraOff, User, AlertCircle } from 'lucide-react';
import { startCamera as startCam, stopCamera as stopCam, recognizeFace as recognize } from '../utils/api';

function CameraComponent() {
  const [cameraActive, setCameraActive] = useState(false);
  const [recognitionResult, setRecognitionResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const imgRef = useRef(null);

  useEffect(() => {
    return () => {
      if (imgRef.current) {
        imgRef.current.src = '';
      }
    };
  }, []);

  const handleStartCamera = async () => {
    try {
      setLoading(true);
      const response = await startCam();

      if (response?.data?.success) {
        setCameraActive(true);
        setRecognitionResult(null);
      } else {
        throw new Error('Backend rejected camera start');
      }
    } catch (error) {
      console.error('Error starting camera:', error);
      setRecognitionResult({ success: false, error: 'Failed to start camera' });
    } finally {
      setLoading(false);
    }
  };

  const handleStopCamera = async () => {
    try {
      setLoading(true);
      const response = await stopCam();

      if (response?.data?.success) {
        setCameraActive(false);
        if (imgRef.current) imgRef.current.src = '';
      }
    } catch (error) {
      console.error('Error stopping camera:', error);
    } finally {
      setLoading(false);
    }
  };

  const recognizeFace = async () => {
    if (!cameraActive) return;

    try {
      setLoading(true);
      const response = await recognize();

      if (response?.data?.success) {
        setRecognitionResult({
          success: true,
          identity: response.data.identity,
          confidence: response.data.confidence,
          timestamp: response.data.timestamp
        });
      } else {
        setRecognitionResult({
          success: false,
          error: response.data?.error || 'Recognition failed'
        });
      }
    } catch (error) {
      console.error(error);
      setRecognitionResult({ success: false, error: 'Network error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-4 py-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center mb-6">
              <CameraIcon className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">
                Face Recognition Camera
              </h1>
            </div>

            {/* Camera Status */}
            <div className="mb-6">
              <div
                className={`flex items-center p-4 rounded-md ${cameraActive ? 'bg-green-50' : 'bg-red-50'
                  }`}
              >
                {cameraActive ? (
                  <CameraIcon className="h-6 w-6 text-green-600" />
                ) : (
                  <CameraOff className="h-6 w-6 text-red-600" />
                )}
                <div className="ml-3">
                  <h3 className="text-lg font-medium">
                    Camera Status: {cameraActive ? 'Active' : 'Inactive'}
                  </h3>
                </div>
              </div>
            </div>

            {/* Video Feed */}
            <div className="mb-6 bg-gray-100 rounded-lg overflow-hidden">
              {cameraActive ? (
                <img
                  ref={imgRef}
                  src="/video_feed"
                  className="w-full h-96 object-cover"
                  alt="Live Camera Feed"
                  onError={(e) => {
                    console.error('Video feed error:', e);
                    e.target.src = '';
                  }}
                  onLoad={() => {
                    console.log('Video feed loaded successfully');
                  }}
                />
              ) : (
                <div className="flex items-center justify-center h-96">
                  <CameraOff className="h-12 w-12 text-gray-400" />
                </div>
              )}
            </div>

            {/* Controls */}
            <div className="flex space-x-4 mb-6">
              {!cameraActive ? (
                <button
                  onClick={handleStartCamera}
                  disabled={loading}
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-md transition-colors hover:bg-green-700"
                >
                  Start Camera
                </button>
              ) : (
                <button
                  onClick={handleStopCamera}
                  disabled={loading}
                  className="flex-1 bg-red-600 text-white px-4 py-2 rounded-md transition-colors hover:bg-red-700"
                >
                  Stop Camera
                </button>
              )}

              <button
                onClick={recognizeFace}
                disabled={!cameraActive || loading}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md transition-colors hover:bg-blue-700 disabled:bg-gray-400"
              >
                Recognize Face
              </button>
            </div>

            {/* Recognition Result */}
            {recognitionResult && (
              <div
                className={`p-4 rounded-md ${recognitionResult.success
                    ? 'bg-green-50'
                    : 'bg-red-50'
                  }`}
              >
                <div className="flex items-center">
                  {recognitionResult.success ? (
                    <User className="h-6 w-6 text-green-600" />
                  ) : (
                    <AlertCircle className="h-6 w-6 text-red-600" />
                  )}
                  <div className="ml-3">
                    {recognitionResult.success ? (
                      <>
                        <p className="font-semibold text-green-800">Identity: {recognitionResult.identity}</p>
                        <p className="text-sm text-green-700">Confidence: {recognitionResult.confidence}</p>
                        <p className="text-xs text-green-600">Time: {recognitionResult.timestamp}</p>
                      </>
                    ) : (
                      <p className="text-red-700 font-medium">Error: {recognitionResult.error}</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default CameraComponent;
