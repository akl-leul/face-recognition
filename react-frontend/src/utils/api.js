import axios from 'axios';

const API_BASE_URL = '';

export const apiCall = async (endpoint, method = 'GET', data = null) => {
  try {
    const config = {
      method,
      url: `${API_BASE_URL}${endpoint}`,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (data && (method === 'POST' || method === 'PUT')) {
      config.data = data;
    }

    const response = await axios(config);
    return response;
  } catch (error) {
    console.error(`API Error (${method} ${endpoint}):`, error);
    throw error;
  }
};

export const startCamera = () => apiCall('/api/start_camera', 'POST');
export const stopCamera = () => apiCall('/api/stop_camera', 'POST');
export const recognizeFace = () => apiCall('/api/recognize', 'POST');
export const getSystemStatus = () => apiCall('/api/status');
export const getAttendanceRecords = () => apiCall('/api/attendance');
export const getEnrolledUsers = () => apiCall('/api/users');

// Enrollment functions
export const startEnrollment = (userName) => apiCall('/api/enrollment/start', 'POST', { name: userName });
export const captureEnrollment = (userName) => apiCall('/api/enrollment/capture', 'POST', { name: userName });
export const cancelEnrollment = () => apiCall('/api/enrollment/cancel', 'POST');

// User CRUD functions
export const deleteUser = (userName) => apiCall(`/api/users/${encodeURIComponent(userName)}`, 'DELETE');
export const updateUser = (userName, newName) => apiCall(`/api/users/${encodeURIComponent(userName)}`, 'PUT', { name: newName });

// Simple recognition functions
export const simpleRecognize = () => apiCall('/api/simple/recognize', 'POST');
export const simpleEnroll = (userName) => apiCall('/api/simple/enroll', 'POST', { name: userName });
export const getSimpleStatus = () => apiCall('/api/simple/status');
