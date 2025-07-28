// API service functions for connecting frontend to backend

const API_BASE_URL = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
}

interface PaginatedResponse<T> {
  success: boolean;
  message: string;
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Generic API function
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T> | PaginatedResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// User API functions
export const userAPI = {
  getAll: async (params?: { 
    skip?: number; 
    limit?: number; 
    role?: string; 
    is_active?: boolean; 
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set('skip', params.skip.toString());
    if (params?.limit !== undefined) searchParams.set('limit', params.limit.toString());
    if (params?.role) searchParams.set('role', params.role);
    if (params?.is_active !== undefined) searchParams.set('is_active', params.is_active.toString());
    
    const query = searchParams.toString();
    return apiRequest<any[]>(`/users/${query ? `?${query}` : ''}`);
  },
  
  getById: async (id: string) => {
    return apiRequest<any>(`/users/${id}`);
  },
  
  create: async (userData: any) => {
    return apiRequest<any>('/users/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },
  
  update: async (id: string, userData: any) => {
    return apiRequest<any>(`/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  },
  
  delete: async (id: string) => {
    return apiRequest<any>(`/users/${id}`, {
      method: 'DELETE',
    });
  },
  
  updateStatus: async (id: string, status: string) => {
    return apiRequest<any>(`/users/${id}/status?status=${status}`, {
      method: 'PATCH',
    });
  },
  
  getByRole: async (role: string) => {
    return apiRequest<any[]>(`/users/role/${role}`);
  },
  
  getActive: async () => {
    return apiRequest<any[]>('/users/active/all');
  },
};

// Customer API functions
export const customerAPI = {
  getAll: async (params?: { 
    skip?: number; 
    limit?: number; 
    is_active?: boolean; 
    search?: string; 
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set('skip', params.skip.toString());
    if (params?.limit !== undefined) searchParams.set('limit', params.limit.toString());
    if (params?.is_active !== undefined) searchParams.set('is_active', params.is_active.toString());
    if (params?.search) searchParams.set('search', params.search);
    
    const query = searchParams.toString();
    return apiRequest<any[]>(`/customers/${query ? `?${query}` : ''}`);
  },
  
  getById: async (id: string) => {
    return apiRequest<any>(`/customers/${id}`);
  },
  
  create: async (customerData: any) => {
    return apiRequest<any>('/customers/', {
      method: 'POST',
      body: JSON.stringify(customerData),
    });
  },
  
  update: async (id: string, customerData: any) => {
    return apiRequest<any>(`/customers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(customerData),
    });
  },
  
  delete: async (id: string) => {
    return apiRequest<any>(`/customers/${id}`, {
      method: 'DELETE',
    });
  },
  
  search: async (query: string) => {
    return apiRequest<any[]>(`/customers/search/${query}`);
  },
  
  getByEmail: async (email: string) => {
    return apiRequest<any>(`/customers/email/${email}`);
  },
  
  getByPhone: async (phone: string) => {
    return apiRequest<any>(`/customers/phone/${phone}`);
  },
};

// Ticket API functions
export const ticketAPI = {
  getAll: async (params?: { 
    skip?: number; 
    limit?: number; 
    status?: string; 
    priority?: string; 
    assigned_to?: string; 
    customer_id?: string; 
    channel?: string; 
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set('skip', params.skip.toString());
    if (params?.limit !== undefined) searchParams.set('limit', params.limit.toString());
    if (params?.status) searchParams.set('status', params.status);
    if (params?.priority) searchParams.set('priority', params.priority);
    if (params?.assigned_to) searchParams.set('assigned_to', params.assigned_to);
    if (params?.customer_id) searchParams.set('customer_id', params.customer_id);
    if (params?.channel) searchParams.set('channel', params.channel);
    
    const query = searchParams.toString();
    return apiRequest<any[]>(`/tickets/${query ? `?${query}` : ''}`);
  },
  
  getById: async (id: string) => {
    return apiRequest<any>(`/tickets/${id}`);
  },
  
  create: async (ticketData: any) => {
    return apiRequest<any>('/tickets/', {
      method: 'POST',
      body: JSON.stringify(ticketData),
    });
  },
  
  update: async (id: string, ticketData: any) => {
    return apiRequest<any>(`/tickets/${id}`, {
      method: 'PUT',
      body: JSON.stringify(ticketData),
    });
  },
  
  delete: async (id: string) => {
    return apiRequest<any>(`/tickets/${id}`, {
      method: 'DELETE',
    });
  },
  
  assign: async (id: string, userId: string) => {
    return apiRequest<any>(`/tickets/${id}/assign?user_id=${userId}`, {
      method: 'PATCH',
    });
  },
  
  resolve: async (id: string, resolution: string) => {
    return apiRequest<any>(`/tickets/${id}/resolve?resolution=${encodeURIComponent(resolution)}`, {
      method: 'PATCH',
    });
  },
  
  rate: async (id: string, rating: number, comment?: string) => {
    const params = new URLSearchParams();
    params.set('rating', rating.toString());
    if (comment) params.set('comment', comment);
    
    return apiRequest<any>(`/tickets/${id}/rate?${params.toString()}`, {
      method: 'PATCH',
    });
  },
  
  getByCustomer: async (customerId: string) => {
    return apiRequest<any[]>(`/tickets/customer/${customerId}`);
  },
  
  getByAssignee: async (userId: string) => {
    return apiRequest<any[]>(`/tickets/assignee/${userId}`);
  },
  
  getByStatus: async (status: string) => {
    return apiRequest<any[]>(`/tickets/status/${status}`);
  },
};

// Goals API functions
export const goalAPI = {
  getAll: async (params?: { 
    skip?: number; 
    limit?: number; 
    user_id?: string; 
    team_id?: string; 
    is_active?: boolean; 
    unit?: string; 
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set('skip', params.skip.toString());
    if (params?.limit !== undefined) searchParams.set('limit', params.limit.toString());
    if (params?.user_id) searchParams.set('user_id', params.user_id);
    if (params?.team_id) searchParams.set('team_id', params.team_id);
    if (params?.is_active !== undefined) searchParams.set('is_active', params.is_active.toString());
    if (params?.unit) searchParams.set('unit', params.unit);
    
    const query = searchParams.toString();
    return apiRequest<any[]>(`/goals/${query ? `?${query}` : ''}`);
  },
  
  getById: async (id: string) => {
    return apiRequest<any>(`/goals/${id}`);
  },
  
  create: async (goalData: any) => {
    return apiRequest<any>('/goals/', {
      method: 'POST',
      body: JSON.stringify(goalData),
    });
  },
  
  update: async (id: string, goalData: any) => {
    return apiRequest<any>(`/goals/${id}`, {
      method: 'PUT',
      body: JSON.stringify(goalData),
    });
  },
  
  delete: async (id: string) => {
    return apiRequest<any>(`/goals/${id}`, {
      method: 'DELETE',
    });
  },
  
  updateProgress: async (id: string, currentValue: number) => {
    return apiRequest<any>(`/goals/${id}/progress?current_value=${currentValue}`, {
      method: 'PATCH',
    });
  },
  
  getByUser: async (userId: string) => {
    return apiRequest<any[]>(`/goals/user/${userId}`);
  },
  
  getByTeam: async (teamId: string) => {
    return apiRequest<any[]>(`/goals/team/${teamId}`);
  },
  
  getActive: async () => {
    return apiRequest<any[]>('/goals/active/all');
  },
};

// Attendance API functions
export const attendanceAPI = {
  getAll: async (params?: { 
    skip?: number; 
    limit?: number; 
    user_id?: string; 
    status?: string; 
    date_from?: string; 
    date_to?: string; 
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set('skip', params.skip.toString());
    if (params?.limit !== undefined) searchParams.set('limit', params.limit.toString());
    if (params?.user_id) searchParams.set('user_id', params.user_id);
    if (params?.status) searchParams.set('status', params.status);
    if (params?.date_from) searchParams.set('date_from', params.date_from);
    if (params?.date_to) searchParams.set('date_to', params.date_to);
    
    const query = searchParams.toString();
    return apiRequest<any[]>(`/attendance/${query ? `?${query}` : ''}`);
  },
  
  getById: async (id: string) => {
    return apiRequest<any>(`/attendance/${id}`);
  },
  
  create: async (attendanceData: any) => {
    return apiRequest<any>('/attendance/', {
      method: 'POST',
      body: JSON.stringify(attendanceData),
    });
  },
  
  update: async (id: string, attendanceData: any) => {
    return apiRequest<any>(`/attendance/${id}`, {
      method: 'PUT',
      body: JSON.stringify(attendanceData),
    });
  },
  
  delete: async (id: string) => {
    return apiRequest<any>(`/attendance/${id}`, {
      method: 'DELETE',
    });
  },
  
  checkIn: async (userId: string, timestamp?: string) => {
    const params = new URLSearchParams();
    params.set('user_id', userId);
    if (timestamp) params.set('timestamp', timestamp);
    
    return apiRequest<any>(`/attendance/checkin?${params.toString()}`, {
      method: 'POST',
    });
  },
  
  checkOut: async (userId: string, timestamp?: string) => {
    const params = new URLSearchParams();
    params.set('user_id', userId);
    if (timestamp) params.set('timestamp', timestamp);
    
    return apiRequest<any>(`/attendance/checkout?${params.toString()}`, {
      method: 'POST',
    });
  },
  
  getByUser: async (userId: string, dateFrom?: string, dateTo?: string) => {
    const params = new URLSearchParams();
    if (dateFrom) params.set('date_from', dateFrom);
    if (dateTo) params.set('date_to', dateTo);
    
    const query = params.toString();
    return apiRequest<any[]>(`/attendance/user/${userId}${query ? `?${query}` : ''}`);
  },
  
  getByUserDate: async (userId: string, date: string) => {
    return apiRequest<any>(`/attendance/user/${userId}/date/${date}`);
  },
};

// Monitoring API functions
export const monitoringAPI = {
  getMetrics: async (params?: { 
    skip?: number; 
    limit?: number; 
    category?: string; 
    user_id?: string; 
    name?: string; 
    date_from?: string; 
    date_to?: string; 
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set('skip', params.skip.toString());
    if (params?.limit !== undefined) searchParams.set('limit', params.limit.toString());
    if (params?.category) searchParams.set('category', params.category);
    if (params?.user_id) searchParams.set('user_id', params.user_id);
    if (params?.name) searchParams.set('name', params.name);
    if (params?.date_from) searchParams.set('date_from', params.date_from);
    if (params?.date_to) searchParams.set('date_to', params.date_to);
    
    const query = searchParams.toString();
    return apiRequest<any[]>(`/monitoring/metrics${query ? `?${query}` : ''}`);
  },
  
  getMetricById: async (id: string) => {
    return apiRequest<any>(`/monitoring/metrics/${id}`);
  },
  
  createMetric: async (metricData: any) => {
    return apiRequest<any>('/monitoring/metrics', {
      method: 'POST',
      body: JSON.stringify(metricData),
    });
  },
  
  deleteMetric: async (id: string) => {
    return apiRequest<any>(`/monitoring/metrics/${id}`, {
      method: 'DELETE',
    });
  },
  
  getByCategory: async (category: string) => {
    return apiRequest<any[]>(`/monitoring/metrics/category/${category}`);
  },
  
  getByUser: async (userId: string) => {
    return apiRequest<any[]>(`/monitoring/metrics/user/${userId}`);
  },
  
  getByTimeRange: async (startDate: string, endDate: string) => {
    return apiRequest<any[]>(`/monitoring/metrics/timerange?start_date=${startDate}&end_date=${endDate}`);
  },
  
  getLatest: async (limit: number = 100) => {
    return apiRequest<any[]>(`/monitoring/metrics/latest?limit=${limit}`);
  },
  
  getDashboard: async () => {
    return apiRequest<any>('/monitoring/dashboard');
  },
};

// Health check
export const healthAPI = {
  check: async () => {
    return apiRequest<any>('/health');
  },
};

export default {
  userAPI,
  customerAPI,
  ticketAPI,
  goalAPI,
  attendanceAPI,
  monitoringAPI,
  healthAPI,
};