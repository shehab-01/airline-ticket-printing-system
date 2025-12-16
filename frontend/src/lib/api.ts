import axios from "axios";

// ============================================================================
// CONFIGURATION
// ============================================================================

const API_BASE_URL = "http://localhost:8080";

// ============================================================================
// TICKET / BATCH TYPES
// ============================================================================

export interface PassengerInfo {
  no?: number;
  pax_name: string;
  pnr: string;
  ticket_type: string;
  rsvn_cfmd?: string;
  status: "pending" | "generated" | "failed";
  pdf_filename?: string;
  error?: string;
}

export interface UploadResponse {
  batch_id: string;
  filename: string;
  total_passengers: number;
  status: string;
  message: string;
}

export interface BatchInfo {
  batch_id: string;
  excel_filename: string;
  created_at: string;
  status: "processing" | "completed" | "failed";
  total_passengers: number;
  generated: number;
  failed: number;
}

export interface BatchListResponse {
  batches: BatchInfo[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface BatchDetail extends BatchInfo {
  passengers: PassengerInfo[];
}

export interface BatchStatusResponse {
  batch_id: string;
  status: "processing" | "completed" | "failed";
  total_passengers: number;
  generated: number;
  failed: number;
  pending: number;
  progress_percentage: number;
  is_complete: boolean;
  passengers: PassengerInfo[];
}

export interface DashboardStats {
  total_batches: number;
  total_tickets_generated: number;
  success_rate: number;
}

export interface SystemStatus {
  libreoffice_available: boolean;
  libreoffice_path?: string;
  output_directory_exists: boolean;
  manifest_exists: boolean;
  total_batches: number;
}

// ============================================================================
// AGENCY TYPES
// ============================================================================

export interface Agency {
  id: string;
  agency_name: string;
  agency_owner: string;
  agency_address?: string;
  email?: string;
  telephone?: string;
  logo_filename?: string;
  logo_path?: string;
  created_at: string;
  updated_at: string;
}

export interface AgencyListResponse {
  agencies: Agency[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface AgencyStats {
  total_agencies: number;
}

// Helper interface
export interface AgencyFormData {
  agency_name: string;
  agency_owner: string;
  agency_address?: string;
  email?: string;
  telephone?: string;
  logo?: File | null;
}

// ============================================================================
// API CLIENTS
// ============================================================================

const ticketClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/ticket`,
  timeout: 60000, // 60s
});

const agencyClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/agency`,
  timeout: 30000, // 30s
});

// ============================================================================
// TICKET API EXPORTS
// ============================================================================

export const api = {
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await ticketClient.post<UploadResponse>(
      "/upload",
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );
    return response.data;
  },

  getBatches: async (page = 1, limit = 10) => {
    const response = await ticketClient.get<BatchListResponse>("/batches", {
      params: { page, limit },
    });
    return response.data;
  },

  getBatchDetails: async (batchId: string) => {
    const response = await ticketClient.get<BatchDetail>(`/batches/${batchId}`);
    return response.data;
  },

  getBatchStatus: async (batchId: string) => {
    const response = await ticketClient.get<BatchStatusResponse>(
      `/batches/${batchId}/status`
    );
    return response.data;
  },

  downloadSinglePdf: async (batchId: string, filename: string) => {
    const response = await ticketClient.get(
      `/download/pdf/${batchId}/${filename}`,
      { responseType: "blob" }
    );
    return response.data;
  },

  downloadBatchZip: async (batchId: string) => {
    const response = await ticketClient.get(`/download/batch/${batchId}`, {
      responseType: "blob",
    });
    return response.data;
  },

  deleteBatch: async (batchId: string) => {
    const response = await ticketClient.delete(`/batches/${batchId}`);
    return response.data;
  },

  getStats: async () => {
    const response = await ticketClient.get<DashboardStats>("/stats");
    return response.data;
  },

  getSystemStatus: async () => {
    const response = await ticketClient.get<SystemStatus>("/system-status");
    return response.data;
  },
};

// ============================================================================
// AGENCY API EXPORTS
// ============================================================================

export const agencyApi = {
  createAgency: async (data: AgencyFormData) => {
    const formData = new FormData();
    formData.append("agency_name", data.agency_name);
    formData.append("agency_owner", data.agency_owner);
    if (data.agency_address)
      formData.append("agency_address", data.agency_address);
    if (data.email) formData.append("email", data.email);
    if (data.telephone) formData.append("telephone", data.telephone);
    if (data.logo) formData.append("logo", data.logo);

    const response = await agencyClient.post("/create", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  listAgencies: async (page = 1, limit = 100) => {
    const response = await agencyClient.get<AgencyListResponse>("/list", {
      params: { page, limit },
    });
    return response.data;
  },

  getAgency: async (agencyId: string) => {
    const response = await agencyClient.get<Agency>(`/${agencyId}`);
    return response.data;
  },

  updateAgency: async (agencyId: string, data: Partial<AgencyFormData>) => {
    const formData = new FormData();
    if (data.agency_name) formData.append("agency_name", data.agency_name);
    if (data.agency_owner) formData.append("agency_owner", data.agency_owner);
    if (data.agency_address)
      formData.append("agency_address", data.agency_address);
    if (data.email) formData.append("email", data.email);
    if (data.telephone) formData.append("telephone", data.telephone);
    if (data.logo) formData.append("logo", data.logo);

    const response = await agencyClient.put(`/${agencyId}`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  deleteAgency: async (agencyId: string) => {
    const response = await agencyClient.delete(`/${agencyId}`);
    return response.data;
  },

  getStats: async () => {
    const response = await agencyClient.get<AgencyStats>("/stats/overview");
    return response.data;
  },

  getLogoUrl: (agencyId: string) => {
    return `${API_BASE_URL}/api/v1/agency/${agencyId}/logo`;
  },
};

// ============================================================================
// HELPER UTILS
// ============================================================================

export const getDownloadUrl = (batchId: string, filename?: string) => {
  const base = `${API_BASE_URL}/api/v1/ticket`;
  if (filename) {
    return `${base}/download/pdf/${batchId}/${filename}`;
  }
  return `${base}/download/batch/${batchId}`;
};
