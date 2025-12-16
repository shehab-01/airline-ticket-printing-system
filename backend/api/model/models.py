from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
import re

# ============================================================================
# EXISTING MODELS (Keep your ResData model)
# ============================================================================

class ResData(BaseModel):
    """Generic response wrapper"""
    data: Any
    msg: str


# ============================================================================
# PASSENGER/TICKET MODELS
# ============================================================================

class PassengerInfo(BaseModel):
    """Individual passenger information in batch metadata"""
    pax_name: str
    pnr: str
    ticket_type: Optional[str] = ""
    pdf_filename: Optional[str] = None
    status: str = "pending"  # pending, generated, failed
    generated_at: Optional[str] = None
    error: Optional[str] = None


class TicketData(BaseModel):
    """Ticket data from Excel (for internal use)"""
    no: int
    rsvn_cfmd: str
    ticket_type: str
    pax_name: str
    emd1: str
    pnr: str
    travel_agency: str
    ptn1_dep: str
    ptn1_dep_date: str
    ptn1_dep_time: str
    ptn1_arr: str
    ptn1_arr_date: str
    ptn1_arr_time: str
    ptn2_dep: Optional[str] = None
    ptn2_dep_date: Optional[str] = None
    ptn2_dep_time: Optional[str] = None
    ptn2_arr: Optional[str] = None
    ptn2_arr_date: Optional[str] = None
    ptn2_arr_time: Optional[str] = None


# ============================================================================
# BATCH MODELS
# ============================================================================

class BatchInfo(BaseModel):
    """Batch information (summary view for list)"""
    batch_id: str
    filename: str
    upload_date: str
    total_passengers: int
    generated: int = 0
    failed: int = 0
    status: str = "pending"  # pending, processing, completed, failed


class BatchDetail(BaseModel):
    """Detailed batch information including all passengers"""
    batch_id: str
    filename: str
    upload_date: str
    total_passengers: int
    generated: int = 0
    failed: int = 0
    status: str = "pending"
    passengers: List[PassengerInfo] = []


class BatchListResponse(BaseModel):
    """Paginated batch list response"""
    batches: List[BatchInfo]
    total: int
    page: int
    limit: int
    total_pages: int


# ============================================================================
# UPLOAD/GENERATION RESPONSES
# ============================================================================

class UploadResponse(BaseModel):
    """Response after Excel upload and batch creation"""
    batch_id: str
    filename: str
    total_passengers: int
    status: str
    message: str


class GenerationProgress(BaseModel):
    """Real-time generation progress"""
    batch_id: str
    status: str  # pending, processing, completed, failed
    total_passengers: int
    generated: int
    failed: int
    pending: int
    progress_percentage: float
    current_passenger: Optional[str] = None


# ============================================================================
# STATISTICS MODELS
# ============================================================================

class DashboardStats(BaseModel):
    """Dashboard statistics for cards in Image 1"""
    total_batches: int
    total_passengers: int
    total_generated: int
    total_failed: int


class BatchStats(BaseModel):
    """Statistics for a specific batch"""
    batch_id: str
    total_passengers: int
    generated: int
    failed: int
    pending: int
    total_size_mb: float
    file_count: int


# ============================================================================
# ERROR RESPONSE MODELS
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    batch_id: Optional[str] = None


class ValidationError(BaseModel):
    """Validation error details"""
    field: str
    message: str


# ============================================================================
# FILE MODELS
# ============================================================================

class PDFFileInfo(BaseModel):
    """Information about a PDF file"""
    filename: str
    size_bytes: int
    size_mb: float
    modified: float


class BatchFilesResponse(BaseModel):
    """Response with list of files in a batch"""
    batch_id: str
    files: List[PDFFileInfo]
    total_files: int
    total_size_mb: float


# ============================================================================
# DOWNLOAD MODELS
# ============================================================================

class DownloadInfo(BaseModel):
    """Information about available downloads"""
    batch_id: str
    available_pdfs: int
    total_size_mb: float
    zip_filename: str


# ============================================================================
# STATUS MODELS
# ============================================================================

class BatchStatusResponse(BaseModel):
    """Real-time batch status for polling"""
    batch_id: str
    status: str
    total_passengers: int
    generated: int
    failed: int
    pending: int
    progress_percentage: float
    is_complete: bool
    passengers: List[PassengerInfo] = []


class SystemStatus(BaseModel):
    """System status check"""
    libreoffice_available: bool
    libreoffice_path: Optional[str] = None
    output_directory_exists: bool
    manifest_exists: bool
    total_batches: int


# ============================================================================
# REQUEST MODELS (for POST/PUT endpoints)
# ============================================================================

class DeleteBatchRequest(BaseModel):
    """Request to delete a batch"""
    batch_id: str
    confirm: bool = False


class RetryFailedRequest(BaseModel):
    """Request to retry failed ticket generation"""
    batch_id: str
    passenger_names: Optional[List[str]] = None  # If None, retry all failed


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_success_response(data: Any, message: str = "Success") -> ResData:
    """Helper to create successful ResData response"""
    return ResData(data=data, msg=message)


def create_error_response(error: str, detail: Optional[str] = None) -> dict:
    """Helper to create error response"""
    return {
        "error": error,
        "detail": detail
    }


def calculate_progress_percentage(generated: int, failed: int, total: int) -> float:
    """Calculate progress percentage"""
    if total == 0:
        return 0.0
    completed = generated + failed
    return round((completed / total) * 100, 2)


# ============================================================================
# AGENCY MODELS
# ============================================================================

class AgencyBase(BaseModel):
    """Base agency fields"""
    agency_name: str = Field(..., min_length=1, max_length=200)
    agency_owner: str = Field(..., min_length=1, max_length=100)
    agency_address: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = Field(None, max_length=100)
    telephone: Optional[str] = Field(None, max_length=50)


class AgencyCreate(AgencyBase):
    """Request model for creating agency"""
    pass


class AgencyUpdate(BaseModel):
    """Request model for updating agency (all fields optional)"""
    agency_name: Optional[str] = Field(None, min_length=1, max_length=200)
    agency_owner: Optional[str] = Field(None, min_length=1, max_length=100)
    agency_address: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = Field(None, max_length=100)
    telephone: Optional[str] = Field(None, max_length=50)


class AgencyResponse(AgencyBase):
    """Response model for agency"""
    id: str
    created_at: str
    updated_at: str


class AgencyListResponse(BaseModel):
    """Paginated agency list response"""
    agencies: List[AgencyResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class AgencyStats(BaseModel):
    """Agency statistics"""
    total_agencies: int


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_batch_id_format(batch_id: str) -> bool:
    """Validate batch ID format (AAQ###)"""
    if not batch_id.startswith("AAQ"):
        return False
    try:
        number = int(batch_id[3:])
        return True
    except ValueError:
        return False


def validate_agency_id_format(agency_id: str) -> bool:
    """Validate agency ID format (AGN###)"""
    if not agency_id.startswith("AGN"):
        return False
    try:
        number = int(agency_id[3:])
        return True
    except ValueError:
        return False


def validate_excel_file(filename: str) -> bool:
    """Validate Excel file extension"""
    return filename.lower().endswith(('.xlsx', '.xls'))


def validate_pdf_filename(filename: str) -> bool:
    """Validate PDF filename"""
    return filename.lower().endswith('.pdf') and not filename.startswith('.')


def validate_email(email: str) -> bool:
    """Basic email validation"""
    if not email:
        return True  # Email is optional
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    return re.match(pattern, email) is not None