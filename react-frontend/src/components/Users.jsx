import React, { useState, useEffect } from 'react';
import { Users, UserPlus, Trash2, Edit, Eye, EyeOff, RefreshCw } from 'lucide-react';
import { apiCall, getEnrolledUsers, deleteUser, updateUser } from '../utils/api';

export function UsersComponent({ onNavigate }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingUser, setEditingUser] = useState(null);
  const [editFormData, setEditFormData] = useState({});

  // Fetch users on component mount
  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await getEnrolledUsers();
      // The API returns an array directly: ["user1", "user2"]
      if (response.data) {
        const usersList = Array.isArray(response.data) ? response.data : (response.data.users || []);

        const userObjects = usersList.map((name, index) => ({
          id: index + 1,
          name: name,
          face_images: ['face_data'] // Placeholder
        }));
        setUsers(userObjects);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userName) => {
    if (
      window.confirm(
        `Are you sure you want to delete user "${userName}"? This action cannot be undone.`
      )
    ) {
      try {
        setLoading(true);
        await deleteUser(userName);
        await fetchUsers(); // Refresh the list
      } catch (error) {
        console.error('Error deleting user:', error);
        alert('Failed to delete user: ' + (error.response?.data?.error || error.message));
      } finally {
        setLoading(false);
      }
    }
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setEditFormData({ name: user.name, originalName: user.name });
  };

  const handleSaveUser = async () => {
    try {
      setLoading(true);
      await updateUser(editFormData.originalName, editFormData.name);
      setEditingUser(null);
      setEditFormData({});
      await fetchUsers(); // Refresh users list
    } catch (error) {
      console.error('Error saving user:', error);
      alert('Failed to update user: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCancelEdit = () => {
    setEditingUser(null);
    setEditFormData({});
  };

  return (
    <div className="px-4 py-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center">
                <Users className="h-8 w-8 text-blue-600 mr-3" />
                <h1 className="text-2xl font-bold text-gray-900">
                  Enrolled Users
                </h1>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-sm text-gray-500">
                  {users.length} users enrolled
                </span>
                <button
                  onClick={fetchUsers}
                  disabled={loading}
                  className="p-2 text-gray-500 hover:text-gray-700 transition-colors disabled:opacity-50"
                  title="Refresh users"
                >
                  <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                </button>
              </div>
            </div>

            {/* Users Grid */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {loading ? (
                <div className="col-span-full text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-500">Loading users...</p>
                </div>
              ) : users.length === 0 ? (
                <div className="col-span-full text-center py-12">
                  <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No users enrolled yet</p>
                  <p className="text-sm text-gray-400 mt-2">
                    Use enrollment system to add users
                  </p>
                </div>
              ) : (
                users.map((user, index) => (
                  <div
                    key={user.id ?? index}
                    className="bg-white overflow-hidden shadow rounded-lg"
                  >
                    <div className="p-6">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          {user.face_images?.length ? (
                            <div className="h-16 w-16 bg-gray-200 rounded-full flex items-center justify-center">
                              <Eye className="h-8 w-8 text-gray-600" />
                            </div>
                          ) : (
                            <div className="h-16 w-16 bg-gray-200 rounded-full flex items-center justify-center">
                              <EyeOff className="h-8 w-8 text-gray-400" />
                            </div>
                          )}
                        </div>

                        <div className="flex-1">
                          <h3 className="text-lg font-medium text-gray-900">
                            {user.name}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {user.face_images?.length
                              ? `${user.face_images.length} face images`
                              : 'No face data'}
                          </p>
                          <p className="text-xs text-gray-400">
                            User ID: {user.id ?? index + 1}
                          </p>
                        </div>
                      </div>

                      <div className="flex justify-end space-x-2 mt-4">
                        <button
                          onClick={() => handleEditUser(user)}
                          className="p-2 text-blue-600 hover:text-blue-800 transition-colors"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteUser(user.name)}
                          className="p-2 text-red-600 hover:text-red-800 transition-colors"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Add User Button */}
            <div className="mt-6">
              <button
                onClick={() => onNavigate && onNavigate('enrollment')}
                className="w-full flex justify-center items-center px-4 py-2 rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <UserPlus className="w-5 h-5 mr-2" />
                Enroll New User
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Edit User Modal */}
      {editingUser && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Edit User: {editingUser.name}
              </h3>
              <button
                onClick={handleCancelEdit}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  User Name
                </label>
                <input
                  type="text"
                  value={editFormData.name || ''}
                  onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                  className="w-full border rounded-md p-2"
                  placeholder="Enter user name"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={handleCancelEdit}
                className="bg-gray-300 px-4 py-2 rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveUser}
                disabled={!editFormData.name || editFormData.name === editFormData.originalName}
                className="bg-blue-600 text-white px-4 py-2 rounded-md disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UsersComponent;
