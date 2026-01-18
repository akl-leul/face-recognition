import React from 'react';
import { Calendar, Users, CheckCircle, XCircle, Clock } from 'lucide-react';

export function AttendanceComponent({ records }) {
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getStatusIcon = (decision) => {
    return decision === 'GRANTED' ? (
      <CheckCircle className="h-5 w-5 text-green-600" />
    ) : (
      <XCircle className="h-5 w-5 text-red-600" />
    );
  };

  const getStatusColor = (decision) => {
    return decision === 'GRANTED' 
      ? 'text-green-800 bg-green-100' 
      : 'text-red-800 bg-red-100';
  };

  const todayStats = records.filter(record => {
    const recordDate = new Date(record.timestamp).toDateString();
    const today = new Date().toDateString();
    return recordDate === today;
  });

  const todayGranted = todayStats.filter(r => r.decision === 'GRANTED').length;
  const todayDenied = todayStats.filter(r => r.decision === 'DENIED').length;

  return (
    <div className="px-4 py-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center mb-6">
              <div className="flex-shrink-0">
                <Calendar className="h-8 w-8 text-blue-600 mr-3" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Today
                  </dt>
                  <dd className="mt-1 text-3xl font-semibold text-gray-900">
                    {todayStats.length}
                  </dd>
                </dl>
              </div>
            </div>

            {/* Today's Stats */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-3 mb-6">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                      <Users className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Total Today
                        </dt>
                        <dd className="mt-1 text-3xl font-semibold text-gray-900">
                          {todayStats.length}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                      <CheckCircle className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Granted Today
                        </dt>
                        <dd className="mt-1 text-3xl font-semibold text-green-600">
                          {todayGranted}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-red-500 rounded-md p-3">
                      <XCircle className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Denied Today
                        </dt>
                        <dd className="mt-1 text-3xl font-semibold text-red-600">
                          {todayDenied}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Recognitions Card */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-purple-500 rounded-md p-3">
                    <Users className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Recent Recognitions
                      </dt>
                      <dd className="mt-1 text-3xl font-semibold text-gray-900">
                        0
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Attendance Table */}
            <div className="mt-8">
              <div className="flex items-center mb-4">
                <h2 className="text-lg font-medium text-gray-900">
                  Recent Attendance
                </h2>
                <div className="ml-2 text-sm text-gray-500">
                  Showing last {records.length} records
                </div>
              </div>

              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Decision
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Confidence
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Time
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {records.length === 0 ? (
                      <tr>
                        <td colSpan="4" className="px-6 py-4 text-center text-gray-500">
                          No attendance records found
                        </td>
                      </tr>
                    ) : (
                      records.map((record, index) => (
                        <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {record.user_name || 'Unknown'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(record.decision)}`}>
                              {getStatusIcon(record.decision)}
                              <span className="ml-2">{record.decision}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {record.confidence ? `${(record.confidence * 100).toFixed(1)}%` : 'N/A'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <div className="flex items-center">
                              <Clock className="h-4 w-4 mr-2" />
                              {formatTime(record.timestamp)}
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AttendanceComponent;
