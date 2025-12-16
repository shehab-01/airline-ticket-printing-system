from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form
from fastapi.responses import FileResponse
from api.model.models import (
    AgencyCreate,
    AgencyUpdate,
    AgencyResponse,
    AgencyListResponse,
    AgencyStats,
    ResData,
    create_success_response,
    validate_email
)
from api.utils.agency_manager import get_agency_manager
import traceback


router = APIRouter(prefix="/api/v1/agency")


@router.post("/create", response_model=ResData)
async def create_agency(
    agency_name: str = Form(...),
    agency_owner: str = Form(...),
    agency_address: str = Form(None),
    email: str = Form(None),
    telephone: str = Form(None),
    logo: UploadFile = File(None)  # Optional logo upload
):
   
    try:
        # Validate email if provided
        if email and not validate_email(email):
            raise HTTPException(
                status_code=400,
                detail="Invalid email format"
            )
        
        manager = get_agency_manager()
        
        # Create agency data dict
        agency_data = {
            "agency_name": agency_name,
            "agency_owner": agency_owner,
            "agency_address": agency_address or "",
            "email": email or "",
            "telephone": telephone or ""
        }
        
        # Create agency
        created_agency = manager.create_agency(agency_data)
        
        # Upload logo if provided
        if logo and logo.filename:
            try:
                created_agency = manager.save_logo(
                    agency_id=created_agency["id"],
                    logo_file=logo.file,
                    filename=logo.filename
                )
                print(f"Logo uploaded for {created_agency['id']}: {logo.filename}")
            except Exception as logo_error:
                print(f"Warning: Agency created but logo upload failed: {logo_error}")

        
        return create_success_response(
            data=created_agency,
            message=f"Agency '{created_agency['agency_name']}' created successfully" + 
                    (" with logo" if created_agency.get("logo_filename") else "")
        )
        
    except ValueError as e:
        # Duplicate name or validation error
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating agency: {str(e)}")


@router.get("/list", response_model=AgencyListResponse)
async def list_agencies(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):

    try:
        manager = get_agency_manager()
        result = manager.list_agencies(page=page, limit=limit)
        
        return AgencyListResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agency_id}", response_model=AgencyResponse)
async def get_agency(agency_id: str):
 
    try:
        manager = get_agency_manager()
        agency = manager.get_agency(agency_id)
        
        if not agency:
            raise HTTPException(
                status_code=404,
                detail=f"Agency with ID '{agency_id}' not found"
            )
        
        return AgencyResponse(**agency)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{agency_id}", response_model=ResData)
async def update_agency(
    agency_id: str,
    agency_name: str = Form(None),
    agency_owner: str = Form(None),
    agency_address: str = Form(None),
    email: str = Form(None),
    telephone: str = Form(None),
    logo: UploadFile = File(None)  # Optional logo upload
):
   
    try:
        # Validate email if provided
        if email and not validate_email(email):
            raise HTTPException(
                status_code=400,
                detail="Invalid email format"
            )
        
        manager = get_agency_manager()
        
        # Build update dictionary (only include provided fields)
        update_dict = {}
        if agency_name is not None:
            update_dict["agency_name"] = agency_name
        if agency_owner is not None:
            update_dict["agency_owner"] = agency_owner
        if agency_address is not None:
            update_dict["agency_address"] = agency_address
        if email is not None:
            update_dict["email"] = email
        if telephone is not None:
            update_dict["telephone"] = telephone
        
        # Update agency data if any fields provided
        if update_dict:
            updated_agency = manager.update_agency(agency_id, update_dict)
            
            if not updated_agency:
                raise HTTPException(
                    status_code=404,
                    detail=f"Agency with ID '{agency_id}' not found"
                )
        else:
            # No data fields to update, just get current agency
            updated_agency = manager.get_agency(agency_id)
            if not updated_agency:
                raise HTTPException(
                    status_code=404,
                    detail=f"Agency with ID '{agency_id}' not found"
                )
        
        # Update logo if provided
        logo_updated = False
        if logo and logo.filename:
            try:
                updated_agency = manager.save_logo(
                    agency_id=agency_id,
                    logo_file=logo.file,
                    filename=logo.filename
                )
                logo_updated = True
                print(f"Logo updated for {agency_id}: {logo.filename}")
            except Exception as logo_error:
                print(f"Warning: Logo update failed: {logo_error}")

        
        # Check if anything was actually updated
        if not update_dict and not logo_updated:
            raise HTTPException(
                status_code=400,
                detail="No fields provided to update"
            )
        
        message = f"Agency '{updated_agency['agency_name']}' updated successfully"
        if logo_updated:
            message += " (including logo)"
        
        return create_success_response(
            data=updated_agency,
            message=message
        )
        
    except ValueError as e:
        # Duplicate name error
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating agency: {str(e)}")


@router.delete("/{agency_id}")
async def delete_agency(agency_id: str):
    
    try:
        manager = get_agency_manager()
        
        # Get agency info before deleting (for response message)
        agency = manager.get_agency(agency_id)
        if not agency:
            raise HTTPException(
                status_code=404,
                detail=f"Agency with ID '{agency_id}' not found"
            )
        
        # Delete agency
        success = manager.delete_agency(agency_id)
        
        if success:
            return create_success_response(
                data={"agency_id": agency_id},
                message=f"Agency '{agency['agency_name']}' deleted successfully"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete agency"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview", response_model=AgencyStats)
async def get_agency_statistics():
    
    try:
        manager = get_agency_manager()
        stats = manager.get_statistics()
        
        return AgencyStats(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# LOGO MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/{agency_id}/upload-logo", response_model=ResData)
async def upload_agency_logo(
    agency_id: str,
    logo: UploadFile = File(...)
):
    
    try:
        manager = get_agency_manager()
        
        # Save logo
        updated_agency = manager.save_logo(
            agency_id=agency_id,
            logo_file=logo.file,
            filename=logo.filename
        )
        
        return create_success_response(
            data={
                "agency_id": agency_id,
                "logo_filename": updated_agency["logo_filename"],
                "logo_path": updated_agency["logo_path"]
            },
            message=f"Logo uploaded successfully for '{updated_agency['agency_name']}'"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error uploading logo: {str(e)}")


@router.get("/{agency_id}/logo")
async def get_agency_logo(agency_id: str):
    
    try:
        manager = get_agency_manager()
        logo_path = manager.get_logo_path(agency_id)
        
        if not logo_path:
            raise HTTPException(
                status_code=404,
                detail=f"No logo found for agency '{agency_id}'"
            )
        
        return FileResponse(
            path=str(logo_path),
            media_type=f"image/{logo_path.suffix[1:]}",
            filename=logo_path.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{agency_id}/logo")
async def delete_agency_logo(agency_id: str):
    
    try:
        manager = get_agency_manager()
        
        # Get agency info before deleting logo
        agency = manager.get_agency(agency_id)
        if not agency:
            raise HTTPException(
                status_code=404,
                detail=f"Agency with ID '{agency_id}' not found"
            )
        
        # Delete logo
        success = manager.delete_logo(agency_id)
        
        if success:
            return create_success_response(
                data={"agency_id": agency_id},
                message=f"Logo deleted successfully for '{agency['agency_name']}'"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail="No logo found to delete"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))