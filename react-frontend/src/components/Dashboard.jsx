import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Camera as CameraIcon, UserPlus, Zap } from 'lucide-react';
import { getEnrolledUsers, getSystemStatus, startCamera } from '../utils/api';

export function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    enrolledUsers: 0,
    cameraActive: false,
    recognitionActive: false
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [usersRes, statusRes] = await Promise.all([
        getEnrolledUsers(),
        getSystemStatus()
      ]);

      const usersList = Array.isArray(usersRes.data) ? usersRes.data : (usersRes.data.users || []);

      setStats({
        enrolledUsers: usersList.length,
        cameraActive: statusRes.data.camera_active,
        recognitionActive: statusRes.data.recognition_active
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartCameraAction = async () => {
    try {
      await startCamera();
      fetchDashboardData();
      navigate('/camera');
    } catch (error) {
      console.error('Failed to start camera:', error);
    }
  };

  return (
    <div className="px-4 py-6">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {/* Total Users Card */}
        <div
          onClick={() => navigate('/users')}
          className="bg-white overflow-hidden shadow rounded-lg cursor-pointer hover:shadow-md transition-shadow"
        >
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                <Users className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Users
                  </dt>
                  <dd className="mt-1 text-3xl font-semibold text-gray-900">
                    {stats.enrolledUsers}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Camera Status Card */}
        <div
          onClick={() => navigate('/camera')}
          className="bg-white overflow-hidden shadow rounded-lg cursor-pointer hover:shadow-md transition-shadow"
        >
          <div className="p-5">
            <div className="flex items-center">
              <div className={`flex-shrink-0 rounded-md p-3 ${stats.cameraActive ? 'bg-green-500' : 'bg-red-500'}`}>
                <CameraIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Camera Status
                  </dt>
                  <dd className={`mt-1 text-2xl font-semibold ${stats.cameraActive ? 'text-green-600' : 'text-red-600'}`}>
                    {stats.cameraActive ? 'Active' : 'Offline'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Recognition Status Card */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className={`flex-shrink-0 rounded-md p-3 ${stats.recognitionActive ? 'bg-purple-500' : 'bg-gray-400'}`}>
                <Zap className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Auto-Recognition
                  </dt>
                  <dd className={`mt-1 text-2xl font-semibold ${stats.recognitionActive ? 'text-purple-600' : 'text-gray-600'}`}>
                    {stats.recognitionActive ? 'Running' : 'Standby'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white overflow-hidden shadow rounded-lg lg:col-span-3">
          <div className="p-5">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Quick Actions
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <button
                onClick={handleStartCameraAction}
                className="flex justify-center items-center px-4 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors"
              >
                <CameraIcon className="w-5 h-5 mr-2" />
                Launch Camera
              </button>

              <button
                onClick={() => navigate('/enrollment')}
                className="flex justify-center items-center px-4 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 transition-colors"
              >
                <UserPlus className="w-5 h-5 mr-2" />
                Enroll New User
              </button>

              <button
                onClick={() => navigate('/users')}
                className="flex justify-center items-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
              >
                <Users className="w-5 h-5 mr-2" />
                Manage Users
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
