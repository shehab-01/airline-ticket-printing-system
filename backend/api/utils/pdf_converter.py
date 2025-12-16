import subprocess
import os
import time
import winreg
from pathlib import Path
from typing import Optional


class PDFConverter:
    
    def __init__(self):
        self.libreoffice_path = self._find_libreoffice()
        
    def _find_libreoffice(self) -> Optional[str]:
       
        #  Check Windows Registry
        try:
            registry_path = r"SOFTWARE\LibreOffice\UNO\InstallPath"
            for root_key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                try:
                    key = winreg.OpenKey(root_key, registry_path)
                    install_path, _ = winreg.QueryValueEx(key, "")
                    winreg.CloseKey(key)
                    
                    soffice_path = Path(install_path) / "soffice.exe"
                    if soffice_path.exists():
                        print(f"LibreOffice found in registry: {soffice_path}")
                        return str(soffice_path)
                except WindowsError:
                    continue
        except Exception as e:
            print(f"Registry check failed: {e}")
        
        #  Check common installation paths
        common_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            Path.home() / "AppData" / "Local" / "Programs" / "LibreOffice" / "program" / "soffice.exe"
        ]
        
        for path in common_paths:
            path_obj = Path(path)
            if path_obj.exists():
                print(f"LibreOffice found at: {path_obj}")
                return str(path_obj)
        
        # Check if it's in PATH
        try:
            result = subprocess.run(
                ["soffice", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("LibreOffice found in PATH")
                return "soffice"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def is_available(self) -> bool:
        return self.libreoffice_path is not None
    
    def convert_pptx_to_pdf(
        self, 
        pptx_path: Path, 
        output_dir: Path,
        timeout: int = 60
    ) -> Path:
       
        if not self.is_available():
            raise RuntimeError(
                "LibreOffice not found. Please install LibreOffice from "
                "https://www.libreoffice.org/download/ and restart the application."
            )
        
        if not pptx_path.exists():
            raise FileNotFoundError(f"PPTX file not found: {pptx_path}")
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Expected PDF filename 
        pdf_filename = pptx_path.stem + ".pdf"
        pdf_path = output_dir / pdf_filename
        
        # Remove existing PDF 
        if pdf_path.exists():
            pdf_path.unlink()
        
 
        command = [
            str(self.libreoffice_path),
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(pptx_path)
        ]
        
        print(f"Converting: {pptx_path.name} -> {pdf_filename}")
        print(f"Command: {' '.join(command)}")
        
        try:
            # Run conversion
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW  
            )
            
            # Wait for file system to release the file (Windows file locking)
            time.sleep(0.5)
            
            # Check if conversion succeeded
            if pdf_path.exists():
                print(f"✓ PDF generated: {pdf_path.name}")
                return pdf_path
            else:
                # Conversion failed
                error_msg = result.stderr if result.stderr else "Unknown error"
                raise RuntimeError(
                    f"PDF conversion failed for {pptx_path.name}. "
                    f"LibreOffice error: {error_msg}"
                )
                
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"PDF conversion timed out after {timeout} seconds for {pptx_path.name}"
            )
        except Exception as e:
            raise RuntimeError(f"PDF conversion error: {str(e)}")
    
    def convert_multiple(
        self, 
        pptx_files: list[Path], 
        output_dir: Path,
        on_progress=None
    ) -> dict[str, Path | Exception]:
       
        results = {}
        total = len(pptx_files)
        
        for idx, pptx_path in enumerate(pptx_files, 1):
            if on_progress:
                on_progress(idx, total, pptx_path.name)
            
            try:
                pdf_path = self.convert_pptx_to_pdf(pptx_path, output_dir)
                results[pptx_path.name] = pdf_path
            except Exception as e:
                print(f"✗ Failed to convert {pptx_path.name}: {e}")
                results[pptx_path.name] = e
        
        return results


# Singleton instance
_converter_instance = None

def get_converter() -> PDFConverter:
    global _converter_instance
    if _converter_instance is None:
        _converter_instance = PDFConverter()
    return _converter_instance


# Convenience function
def convert_pptx_to_pdf(pptx_path: Path, output_dir: Path) -> Path:
    
    converter = get_converter()
    return converter.convert_pptx_to_pdf(pptx_path, output_dir)