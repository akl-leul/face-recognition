import React, { useState, useEffect } from 'react';
import { Camera, User, X, Check, AlertCircle, Loader } from 'lucide-react';
import { startEnrollment, captureEnrollment, cancelEnrollment } from '../utils/api';

export function EnrollmentComponent({ onEnrollmentComplete }) {
  const [isEnrolling, setIsEnrolling] = useState(false);
  const [userName, setUserName] = useState('');
  const [currentPose, setCurrentPose] = useState('');
  const [poseIndex, setPoseIndex] = useState(0);
  const [totalPoses, setTotalPoses] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleStartEnrollment = async () => {
    if (!userName.trim()) {
      setError('Please enter a user name');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      const response = await startEnrollment(userName);
      
      if (response.data.success) {
        setIsEnrolling(true);
        setCurrentPose(response.data.current_pose);
        setPoseIndex(response.data.pose_index);
        setTotalPoses(response.data.total_poses);
        setSuccess(response.data.message);
      }
    } catch (error) {
      setError('Failed to start enrollment: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCapture = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      const response = await captureEnrollment(userName);
      
      if (response.data.success) {
        if (response.data.complete) {
          setSuccess(response.data.message);
          setIsEnrolling(false);
          setUserName('');
          setCurrentPose('');
          setPoseIndex(0);
          
          // Notify parent component
          if (onEnrollmentComplete) {
            onEnrollmentComplete();
          }
        } else {
          setCurrentPose(response.data.next_pose);
          setPoseIndex(response.data.pose_index);
          setSuccess(response.data.message);
        }
      }
    } catch (error) {
      setError('Capture failed: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    try {
      await cancelEnrollment();
      setIsEnrolling(false);
      setUserName('');
      setCurrentPose('');
      setPoseIndex(0);
      setError('');
      setSuccess('');
    } catch (error) {
      setError('Failed to cancel enrollment');
    }
  };

  return (
    <div className="px-4 py-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center mb-6">
              <User className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">
                Face Enrollment
              </h1>
            </div>

            {/* Error and Success Messages */}
            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
                <div className="flex">
                  <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
                  <span className="text-red-700">{error}</span>
                </div>
              </div>
            )}

            {success && (
              <div className="mb-4 bg-green-50 border border-green-200 rounded-md p-4">
                <div className="flex">
                  <Check className="h-5 w-5 text-green-400 mr-2" />
                  <span className="text-green-700">{success}</span>
                </div>
              </div>
            )}

            {!isEnrolling ? (
              /* Start Enrollment Form */
              <div className="space-y-4">
                <div>
                  <label htmlFor="userName" className="block text-sm font-medium text-gray-700 mb-2">
                    User Name
                  </label>
                  <input
                    type="text"
                    id="userName"
                    value={userName}
                    onChange={(e) => setUserName(e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter user name"
                    disabled={loading}
                  />
                </div>
                
                <button
                  onClick={handleStartEnrollment}
                  disabled={loading || !userName.trim()}
                  className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <Loader className="w-4 h-4 mr-2 animate-spin" />
                      Starting...
                    </>
                  ) : (
                    <>
                      <Camera className="w-4 h-4 mr-2" />
                      Start Enrollment
                    </>
                  )}
                </button>
              </div>
            ) : (
              /* Enrollment Process */
              <div className="space-y-6">
                {/* Progress */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">Progress</span>
                    <span className="text-sm text-gray-500">
                      {poseIndex + 1} / {totalPoses}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${((poseIndex + 1) / totalPoses) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Current Pose Instructions */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <div className="text-center">
                    <Camera className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-blue-900 mb-2">
                      {currentPose}
                    </h3>
                    <p className="text-blue-700">
                      Position your face as shown above and click "Capture Face"
                    </p>
                  </div>
                </div>

                {/* Video Feed Placeholder */}
                <div className="bg-gray-100 rounded-lg overflow-hidden">
                  <img
                    src="/video_feed"
                    className="w-full h-96 object-cover"
                    alt="Enrollment Camera Feed"
                    onError={(e) => {
                      console.error('Video feed error:', e);
                    }}
                  />
                </div>

                {/* Control Buttons */}
                <div className="flex space-x-4">
                  <button
                    onClick={handleCapture}
                    disabled={loading}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md font-medium transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <Loader className="w-4 h-4 mr-2 animate-spin" />
                        Capturing...
                      </>
                    ) : (
                      <>
                        <Camera className="w-4 h-4 mr-2" />
                        Capture Face
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={handleCancel}
                    disabled={loading}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md font-medium transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    <X className="w-4 h-4 mr-2" />
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default EnrollmentComponent;
