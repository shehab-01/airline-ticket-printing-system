import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import re
import shutil


class AgencyManager:
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.agencies_path = self.data_dir / "agencies.json"
        self.logos_dir = self.data_dir / "logos"  # Logo storage directory
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logos_dir.mkdir(parents=True, exist_ok=True)  # Create logos directory
        
        # Initialize agencies.json if it doesn't exist
        self._init_agencies_db()
    
    def _init_agencies_db(self):
        if not self.agencies_path.exists():
            agencies_data = {
                "agencies": [],
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
            self._save_agencies(agencies_data)
            print(f"Created agencies database at: {self.agencies_path}")
    
    def _load_agencies(self) -> dict:
        try:
            with open(self.agencies_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading agencies: {e}")
            return {"agencies": [], "last_updated": datetime.now().isoformat()}
    
    def _save_agencies(self, data: dict):
        data["last_updated"] = datetime.now().isoformat()
        with open(self.agencies_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _generate_agency_id(self) -> str:
        
        data = self._load_agencies()
        
        # Find highest agency number
        max_num = 0
        for agency in data["agencies"]:
            agency_id = agency.get("id", "")
            if agency_id.startswith("AGN"):
                try:
                    num = int(agency_id[3:])
                    max_num = max(max_num, num)
                except ValueError:
                    continue
        
        # Generate next agency ID
        next_num = max_num + 1
        agency_id = f"AGN{next_num:03d}"  # AGN001, AGN002, etc.
        
        print(f"Generated agency ID: {agency_id}")
        return agency_id
    
    def _normalize_name(self, name: str) -> str:
        return " ".join(name.lower().split())
    
    def _check_duplicate_name(self, agency_name: str, exclude_id: Optional[str] = None) -> bool:
        
        data = self._load_agencies()
        normalized_name = self._normalize_name(agency_name)
        
        for agency in data["agencies"]:
            if exclude_id and agency["id"] == exclude_id:
                continue
            
            if self._normalize_name(agency["agency_name"]) == normalized_name:
                return True
        
        return False
    
    def create_agency(self, agency_data: dict) -> dict:
       
        # Check for duplicate name
        if self._check_duplicate_name(agency_data["agency_name"]):
            raise ValueError(f"Agency with name '{agency_data['agency_name']}' already exists")
        
        # Generate agency ID
        agency_id = self._generate_agency_id()
        
        # Create agency record
        now = datetime.now().isoformat()
        agency = {
            "id": agency_id,
            "agency_name": agency_data["agency_name"],
            "agency_owner": agency_data["agency_owner"],
            "agency_address": agency_data.get("agency_address", ""),
            "email": agency_data.get("email", ""),
            "telephone": agency_data.get("telephone", ""),
            "logo_filename": None,  # Initialize as None
            "logo_path": None,  # Initialize as None
            "created_at": now,
            "updated_at": now
        }
        
        # Save to database
        data = self._load_agencies()
        data["agencies"].append(agency)
        self._save_agencies(data)
        
        print(f"Created agency: {agency_id} - {agency['agency_name']}")
        return agency
    
    def get_agency(self, agency_id: str) -> Optional[dict]:
        """Get agency by ID"""
        data = self._load_agencies()
        
        for agency in data["agencies"]:
            if agency["id"] == agency_id:
                return agency
        
        return None
    
    def get_agency_with_logo_info(self, agency_id: str) -> Optional[dict]:
        """Get agency by ID with has_logo field"""
        agency = self.get_agency(agency_id)
        if agency:
            agency["has_logo"] = self.has_logo(agency_id)
        return agency
    
    def list_agencies(self, page: int = 1, limit: int = 10) -> dict:
        
        data = self._load_agencies()
        agencies = data["agencies"]
        
        # Add has_logo field to each agency
        for agency in agencies:
            agency["has_logo"] = self.has_logo(agency["id"])
        
        # Sort by name ascending
        agencies.sort(key=lambda x: x["agency_name"].lower())
        
        total = len(agencies)
        total_pages = (total + limit - 1) // limit  # Ceiling division
        
        # Paginate
        start = (page - 1) * limit
        end = start + limit
        paginated_agencies = agencies[start:end]
        
        return {
            "agencies": paginated_agencies,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    
    def update_agency(self, agency_id: str, update_data: dict) -> Optional[dict]:
       
        data = self._load_agencies()
        
        # Find agency
        agency_index = None
        for idx, agency in enumerate(data["agencies"]):
            if agency["id"] == agency_id:
                agency_index = idx
                break
        
        if agency_index is None:
            return None
        
        agency = data["agencies"][agency_index]
        
        # Check for duplicate name if name is being updated
        if "agency_name" in update_data and update_data["agency_name"] != agency["agency_name"]:
            if self._check_duplicate_name(update_data["agency_name"], exclude_id=agency_id):
                raise ValueError(f"Agency with name '{update_data['agency_name']}' already exists")
        
        # Update fields
        for key, value in update_data.items():
            if key in agency and value is not None:
                agency[key] = value
        
        # Update timestamp
        agency["updated_at"] = datetime.now().isoformat()
        
        # Save
        data["agencies"][agency_index] = agency
        self._save_agencies(data)
        
        print(f"Updated agency: {agency_id}")
        return agency
    
    def delete_agency(self, agency_id: str) -> bool:
        
        # Delete logo first
        self.delete_logo(agency_id)
        
        data = self._load_agencies()
        
        # Filter out the agency
        original_count = len(data["agencies"])
        data["agencies"] = [a for a in data["agencies"] if a["id"] != agency_id]
        
        if len(data["agencies"]) < original_count:
            self._save_agencies(data)
            print(f"Deleted agency: {agency_id}")
            return True
        
        return False
    
    def find_by_name(self, name: str) -> Optional[dict]:
        
        if not name or not name.strip():
            return None
        
        data = self._load_agencies()
        normalized_search = self._normalize_name(name)
        
        found_agency = None
        
        # First pass: Exact match
        for agency in data["agencies"]:
            normalized_name = self._normalize_name(agency["agency_name"])
            if normalized_name == normalized_search:
                print(f"Found exact match: '{name}' -> '{agency['agency_name']}'")
                found_agency = agency
                break
        
        # Second pass: Partial match (database name contains search term)
        if not found_agency:
            for agency in data["agencies"]:
                normalized_name = self._normalize_name(agency["agency_name"])
                if normalized_search in normalized_name:
                    print(f"Found partial match: '{name}' -> '{agency['agency_name']}'")
                    found_agency = agency
                    break
        
        # Third pass: Reverse partial match (search term contains database name)
        if not found_agency:
            for agency in data["agencies"]:
                normalized_name = self._normalize_name(agency["agency_name"])
                if normalized_name in normalized_search:
                    print(f"Found reverse partial match: '{name}' -> '{agency['agency_name']}'")
                    found_agency = agency
                    break
        
        if not found_agency:
            print(f"No agency found for: '{name}'")
            return None
        
        # Add has_logo field
        found_agency["has_logo"] = self.has_logo(found_agency["id"])
        return found_agency
    
    def get_statistics(self) -> dict:
        
        data = self._load_agencies()
        return {
            "total_agencies": len(data["agencies"])
        }
    
    # ============================================================================
    # LOGO MANAGEMENT METHODS
    # ============================================================================
    
    def save_logo(self, agency_id: str, logo_file, filename: str) -> dict:
        
        # Check if agency exists
        agency = self.get_agency(agency_id)
        if not agency:
            raise ValueError(f"Agency with ID '{agency_id}' not found")
        
        # Validate file extension
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg'}
        file_ext = Path(filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise ValueError(f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")
        
        # Delete old logo if exists
        if agency.get("logo_filename"):
            old_logo_path = self.logos_dir / agency["logo_filename"]
            if old_logo_path.exists():
                old_logo_path.unlink()
                print(f"Deleted old logo: {agency['logo_filename']}")
        
        # Create new filename
        new_filename = f"{agency_id}{file_ext}"
        logo_path = self.logos_dir / new_filename
        
        # Save logo file
        with open(logo_path, "wb") as f:
            shutil.copyfileobj(logo_file, f)
        
        print(f"Saved logo: {new_filename}")
        
        # Update agency record
        data = self._load_agencies()
        for idx, a in enumerate(data["agencies"]):
            if a["id"] == agency_id:
                data["agencies"][idx]["logo_filename"] = new_filename
                data["agencies"][idx]["logo_path"] = str(logo_path)
                data["agencies"][idx]["updated_at"] = datetime.now().isoformat()
                agency = data["agencies"][idx]
                break
        
        self._save_agencies(data)
        agency["has_logo"] = True
        return agency
    
    def get_logo_path(self, agency_id: str) -> Optional[Path]:
        
        data = self._load_agencies()
        
        agency = None
        for a in data["agencies"]:
            if a["id"] == agency_id:
                agency = a
                break
        
        if not agency or not agency.get("logo_filename"):
            return None
        
        logo_path = self.logos_dir / agency["logo_filename"]
        
        if logo_path.exists():
            return logo_path
        
        return None
    
    def delete_logo(self, agency_id: str) -> bool:
        
        data = self._load_agencies()
        
        agency = None
        for a in data["agencies"]:
            if a["id"] == agency_id:
                agency = a
                break
        
        if not agency or not agency.get("logo_filename"):
            return False
        
        # Delete file
        logo_path = self.logos_dir / agency["logo_filename"]
        if logo_path.exists():
            logo_path.unlink()
            print(f"Deleted logo file: {agency['logo_filename']}")
        
        # Update agency record 
        data = self._load_agencies()
        for idx, a in enumerate(data["agencies"]):
            if a["id"] == agency_id:
                data["agencies"][idx]["logo_filename"] = None
                data["agencies"][idx]["logo_path"] = None
                data["agencies"][idx]["updated_at"] = datetime.now().isoformat()
                break
        
        self._save_agencies(data)
        return True
    
    def has_logo(self, agency_id: str) -> bool:
        logo_path = self.get_logo_path(agency_id)
        return logo_path is not None


# Singleton instance
_agency_manager_instance = None

def get_agency_manager() -> AgencyManager:
    global _agency_manager_instance
    if _agency_manager_instance is None:
        _agency_manager_instance = AgencyManager()
    return _agency_manager_instance