from fastapi import FastAPI, APIRouter, File, Form, HTTPException, UploadFile, Depends
from api.model.models import ResData
import pandas as pd
import re
from dataclasses import dataclass
from typing import Optional


router = APIRouter(prefix="/api/v1/ticket")

@dataclass
class Ticket:
    no: int
    rsvn_cfmd: str
    ticket_type: str
    pax_name: str
    emd1: float
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

@router.post("/generate", response_model=ResData)
async def generate(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx or .xls)")
    
    try:
        print("Reading the file")
        df = pd.read_excel(file.file, sheet_name=0, header=0)
        df.columns = df.columns.str.replace(' ', '_')

        df = df.fillna("")
        # Create tickets
        tickets = []
        for index, row in df.iterrows():
            raw_emd = row.get('emd1_(Extra_RQ)', '')
            clean_emd = str(int(raw_emd)) if raw_emd != "" else ""

            ticket = Ticket(
                no=row['NO'],
                rsvn_cfmd=row['RSVN_cfmd'],
                ticket_type=row['ADT/LBR/CHD/INF'],
                pax_name=row['PAX_name'],
                emd1=clean_emd, 
                pnr=row['PNR_Reference'],
                travel_agency=row['Travel_Agency'],
                ptn1_dep=row['PTN1-Dep'],
                ptn1_dep_date=row['PTN1_Date'],
                ptn1_dep_time=row['PTN1_Time'],
                ptn1_arr=row['PTN1-Arr'],
                ptn1_arr_date=row['PTN1_Date.1'],  
                ptn1_arr_time=row['PTN1_Time.1'], 
                ptn2_dep=row.get('PTN2-Dep'),
                ptn2_dep_date=row.get('PTN2_Date'),
                ptn2_dep_time=row.get('PTN2_Time'),
                ptn2_arr=row.get('PTN2-Arr'),
                ptn2_arr_date=row.get('PTN2_Date.1'),
                ptn2_arr_time=row.get('PTN2_Time.1')
            )
            tickets.append(ticket)
        
        print(f"Created {len(tickets)} ticket objects")

        if tickets:
            print("\nFirst ticket:")
            print(tickets[0])

        return ResData(data='excel_data', msg=f"Successfully read")

    
    except:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    


