import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import secrets


class BatchManager:
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.batches_dir = self.output_dir / "batches"
        self.manifest_path = self.output_dir / "manifest.json"
        
        # Ensure directories exist
        self.batches_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize manifest if it doesn't exist
        self._init_manifest()
    
    def _init_manifest(self):
        if not self.manifest_path.exists():
            manifest = {
                "batches": [],
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
            self._save_manifest(manifest)
            print(f"Created manifest at: {self.manifest_path}")
    
    def _load_manifest(self) -> dict:
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading manifest: {e}")
            return {"batches": [], "last_updated": datetime.now().isoformat()}
    
    def _save_manifest(self, manifest: dict):
        manifest["last_updated"] = datetime.now().isoformat()
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    def generate_batch_id(self) -> str:
       
        manifest = self._load_manifest()
        
        # Find highest batch number
        max_num = 0
        for batch in manifest["batches"]:
            batch_id = batch.get("batch_id", "")
            if batch_id.startswith("AAQ"):
                try:
                    num = int(batch_id[3:])
                    max_num = max(max_num, num)
                except ValueError:
                    continue
        
        # Generate next batch ID
        next_num = max_num + 1
        batch_id = f"AAQ{next_num:03d}"  # AAQ001, AAQ002, etc.
        
        print(f"Generated batch ID: {batch_id}")
        return batch_id
    
    def create_batch(
        self, 
        excel_filename: str, 
        total_passengers: int
    ) -> dict:
       
        batch_id = self.generate_batch_id()
        batch_dir = self.batches_dir / batch_id
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        # Create batch metadata
        batch_info = {
            "batch_id": batch_id,
            "filename": excel_filename,
            "upload_date": datetime.now().isoformat(),
            "total_passengers": total_passengers,
            "generated": 0,
            "failed": 0,
            "status": "pending",  # pending, processing, completed, failed
            "batch_dir": str(batch_dir)
        }
        
        # Initialize batch metadata file
        metadata = {
            "batch_id": batch_id,
            "source_file": excel_filename,
            "upload_date": batch_info["upload_date"],
            "passengers": []
        }
        self._save_batch_metadata(batch_id, metadata)
        
        # Add to manifest
        manifest = self._load_manifest()
        manifest["batches"].append(batch_info)
        self._save_manifest(manifest)
        
        print(f"Created batch: {batch_id} in {batch_dir}")
        return batch_info
    
    def get_batch_dir(self, batch_id: str) -> Path:

        return self.batches_dir / batch_id
    
    def get_batch_metadata_path(self, batch_id: str) -> Path:
        return self.get_batch_dir(batch_id) / "metadata.json"
    
    def _load_batch_metadata(self, batch_id: str) -> dict:
        metadata_path = self.get_batch_metadata_path(batch_id)
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading batch metadata for {batch_id}: {e}")
            return None
    
    def _save_batch_metadata(self, batch_id: str, metadata: dict):
        metadata_path = self.get_batch_metadata_path(batch_id)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def add_passenger_to_batch(
        self, 
        batch_id: str, 
        passenger_info: dict
    ):
       
        metadata = self._load_batch_metadata(batch_id)
        if metadata is None:
            raise ValueError(f"Batch {batch_id} not found")
        
        passenger_entry = {
            "pax_name": passenger_info.get("pax_name"),
            "pnr": passenger_info.get("pnr"),
            "ticket_type": passenger_info.get("ticket_type", ""),
            "pdf_filename": None,
            "status": "pending",  # pending, generated, failed
            "generated_at": None,
            "error": None
        }
        
        metadata["passengers"].append(passenger_entry)
        self._save_batch_metadata(batch_id, metadata)
    
    def update_passenger_status(
        self, 
        batch_id: str, 
        pax_name: str,
        pnr: str,
        status: str,
        pdf_filename: Optional[str] = None,
        error: Optional[str] = None
    ):
        
        metadata = self._load_batch_metadata(batch_id)
        if metadata is None:
            raise ValueError(f"Batch {batch_id} not found")
        
        # Find and update passenger
        found = False
        for passenger in metadata["passengers"]:
            if passenger["pax_name"] == pax_name and passenger["pnr"] == pnr:
                passenger["status"] = status
                passenger["pdf_filename"] = pdf_filename
                passenger["generated_at"] = datetime.now().isoformat() if status == "generated" else None
                passenger["error"] = error
                found = True
                break
        
        if not found:
            print(f"Warning: Passenger {pax_name} ({pnr}) not found in batch {batch_id}")
            return
        
        # Save updated metadata
        self._save_batch_metadata(batch_id, metadata)
        
        # Update manifest counts
        self._update_batch_counts(batch_id)
    
    def _update_batch_counts(self, batch_id: str):
        metadata = self._load_batch_metadata(batch_id)
        if metadata is None:
            return
        
        # Count statuses
        generated = sum(1 for p in metadata["passengers"] if p["status"] == "generated")
        failed = sum(1 for p in metadata["passengers"] if p["status"] == "failed")
        pending = sum(1 for p in metadata["passengers"] if p["status"] == "pending")
        
        # Update manifest
        manifest = self._load_manifest()
        for batch in manifest["batches"]:
            if batch["batch_id"] == batch_id:
                batch["generated"] = generated
                batch["failed"] = failed
                
                # Update batch status
                if pending == 0:
                    batch["status"] = "completed"
                elif generated > 0 or failed > 0:
                    batch["status"] = "processing"
                
                break
        
        self._save_manifest(manifest)
    
    def update_batch_status(self, batch_id: str, status: str):
        manifest = self._load_manifest()
        for batch in manifest["batches"]:
            if batch["batch_id"] == batch_id:
                batch["status"] = status
                break
        self._save_manifest(manifest)
    
    def get_batch_info(self, batch_id: str) -> Optional[dict]:
        manifest = self._load_manifest()
        for batch in manifest["batches"]:
            if batch["batch_id"] == batch_id:
                return batch
        return None
    
    def get_batch_details(self, batch_id: str) -> Optional[dict]:
        batch_info = self.get_batch_info(batch_id)
        if batch_info is None:
            return None
        
        metadata = self._load_batch_metadata(batch_id)
        if metadata is None:
            return None
        
        return {
            **batch_info,
            "passengers": metadata["passengers"]
        }
    
    def list_batches(
        self, 
        page: int = 1, 
        limit: int = 10
    ) -> dict:
        
        manifest = self._load_manifest()
        batches = manifest["batches"]
        
        # Sort by upload_date descending (newest first)
        batches.sort(key=lambda x: x["upload_date"], reverse=True)
        
        total = len(batches)
        total_pages = (total + limit - 1) // limit  # Ceiling division
        
        # Paginate
        start = (page - 1) * limit
        end = start + limit
        paginated_batches = batches[start:end]
        
        return {
            "batches": paginated_batches,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    
    def delete_batch(self, batch_id: str) -> bool:
        
        try:
            # Remove from manifest
            manifest = self._load_manifest()
            manifest["batches"] = [b for b in manifest["batches"] if b["batch_id"] != batch_id]
            self._save_manifest(manifest)
            
            # Delete batch directory and all files
            batch_dir = self.get_batch_dir(batch_id)
            if batch_dir.exists():
                import shutil
                shutil.rmtree(batch_dir)
                print(f"Deleted batch: {batch_id}")
            
            return True
        except Exception as e:
            print(f"Error deleting batch {batch_id}: {e}")
            return False
    
    def get_statistics(self) -> dict:
        
        manifest = self._load_manifest()
        batches = manifest["batches"]
        
        return {
            "total_batches": len(batches),
            "total_passengers": sum(b.get("total_passengers", 0) for b in batches),
            "total_generated": sum(b.get("generated", 0) for b in batches),
            "total_failed": sum(b.get("failed", 0) for b in batches)
        }


# Singleton instance
_batch_manager_instance = None

def get_batch_manager() -> BatchManager:
    global _batch_manager_instance
    if _batch_manager_instance is None:
        _batch_manager_instance = BatchManager()
    return _batch_manager_instance