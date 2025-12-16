import zipfile
import io
from pathlib import Path
from typing import Optional, BinaryIO
from fastapi.responses import StreamingResponse, FileResponse
from fastapi import HTTPException


class FileHandler:
    
    def __init__(self, batches_dir: Path):
        self.batches_dir = batches_dir
    
    def get_pdf_path(self, batch_id: str, filename: str) -> Path:
        """Get full path to a PDF file"""
        pdf_path = self.batches_dir / batch_id / filename
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {filename}")
        
        if not pdf_path.is_file():
            raise ValueError(f"Not a file: {filename}")
        
        # Security: Ensure file is within batch directory
        try:
            pdf_path.resolve().relative_to(self.batches_dir.resolve())
        except ValueError:
            raise ValueError("Invalid file path - security violation")
        
        return pdf_path
    
    def serve_pdf(self, batch_id: str, filename: str) -> FileResponse:
       
        pdf_path = self.get_pdf_path(batch_id, filename)
        
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    def create_batch_zip(
        self, 
        batch_id: str, 
        batch_info: dict
    ) -> io.BytesIO:
        
        batch_dir = self.batches_dir / batch_id
        
        if not batch_dir.exists():
            raise FileNotFoundError(f"Batch directory not found: {batch_id}")
        
        # Create in-memory ZIP file
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Get all passengers from batch_info
            passengers = batch_info.get("passengers", [])
            
            # Add each generated PDF to ZIP
            added_count = 0
            for passenger in passengers:
                if passenger["status"] == "generated" and passenger["pdf_filename"]:
                    pdf_path = batch_dir / passenger["pdf_filename"]
                    
                    if pdf_path.exists():
                        # Add to ZIP with just the filename (no path)
                        zip_file.write(pdf_path, arcname=passenger["pdf_filename"])
                        added_count += 1
                        print(f"Added to ZIP: {passenger['pdf_filename']}")
            
            if added_count == 0:
                raise ValueError("No PDFs found to download")
            
            print(f"Created ZIP with {added_count} PDFs")
        
        # Reset buffer position to beginning
        zip_buffer.seek(0)
        return zip_buffer
    
    def serve_batch_zip(
        self, 
        batch_id: str, 
        batch_info: dict
    ) -> StreamingResponse:
        
        zip_buffer = self.create_batch_zip(batch_id, batch_info)
        
        # Create safe filename for ZIP
        excel_filename = batch_info.get("filename", "tickets")
        safe_name = excel_filename.replace(".xlsx", "").replace(".xls", "")
        safe_name = "".join(c for c in safe_name if c.isalnum() or c in (' ', '-', '_')).strip()
        zip_filename = f"{batch_id}_{safe_name}.zip"
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.getvalue()),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={zip_filename}"
            }
        )
    
    def get_batch_pdf_list(self, batch_id: str) -> list[dict]:
        
        batch_dir = self.batches_dir / batch_id
        
        if not batch_dir.exists():
            return []
        
        pdf_files = []
        for pdf_path in batch_dir.glob("*.pdf"):
            stat = pdf_path.stat()
            pdf_files.append({
                "filename": pdf_path.name,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified": stat.st_mtime
            })
        
        return pdf_files
    
    def delete_pdf(self, batch_id: str, filename: str) -> bool:
        
        try:
            pdf_path = self.get_pdf_path(batch_id, filename)
            pdf_path.unlink()
            print(f"Deleted PDF: {filename}")
            return True
        except Exception as e:
            print(f"Error deleting PDF {filename}: {e}")
            return False
    
    def validate_pdf_exists(self, batch_id: str, filename: str) -> bool:

        try:
            pdf_path = self.get_pdf_path(batch_id, filename)
            return True
        except (FileNotFoundError, ValueError):
            return False
    
    def get_batch_size(self, batch_id: str) -> dict:
        
        batch_dir = self.batches_dir / batch_id
        
        if not batch_dir.exists():
            return {"total_bytes": 0, "total_mb": 0, "file_count": 0}
        
        total_bytes = 0
        file_count = 0
        
        for pdf_path in batch_dir.glob("*.pdf"):
            total_bytes += pdf_path.stat().st_size
            file_count += 1
        
        return {
            "total_bytes": total_bytes,
            "total_mb": round(total_bytes / (1024 * 1024), 2),
            "file_count": file_count
        }
    
    def cleanup_temp_files(self, batch_id: str, pattern: str = "*.pptx"):
        
        batch_dir = self.batches_dir / batch_id
        
        if not batch_dir.exists():
            return
        
        deleted_count = 0
        for file_path in batch_dir.glob(pattern):
            try:
                file_path.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {file_path.name}: {e}")
        
        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} temporary files from {batch_id}")


# Singleton instance
_file_handler_instance = None

def get_file_handler(batches_dir: Optional[Path] = None) -> FileHandler:
    global _file_handler_instance
    
    if _file_handler_instance is None:
        if batches_dir is None:
            batches_dir = Path("output/batches")
        _file_handler_instance = FileHandler(batches_dir)
    
    return _file_handler_instance


# Convenience functions
def serve_pdf_download(batch_id: str, filename: str) -> FileResponse:

    handler = get_file_handler()
    return handler.serve_pdf(batch_id, filename)


def serve_batch_zip_download(batch_id: str, batch_info: dict) -> StreamingResponse:

    handler = get_file_handler()
    return handler.serve_batch_zip(batch_id, batch_info)