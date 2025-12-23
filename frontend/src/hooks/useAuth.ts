// Minimal auth hook.
//
// The current Flask backend in this repository does not implement auth routes.
// For production, you should add auth (or an API gateway) before enabling
// multi-user features.

export const useAuth = () => {
  return {
    user: null,
    isAuthenticated: true,
    loading: false,
    login: async () => true,
    register: async () => true,
    logout: () => {},
  };
};