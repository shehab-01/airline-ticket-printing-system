import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import re


class TicketNumberManager:
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.counters_path = self.data_dir / "ticket_counters.json"
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize counters file if it doesn't exist
        self._init_counters()
    
    def _init_counters(self):
        if not self.counters_path.exists():
            counters_data = {
                "counters": {},
                "last_updated": datetime.now().isoformat()
            }
            self._save_counters(counters_data)
            print(f"Created ticket counters at: {self.counters_path}")
    
    def _load_counters(self) -> dict:
        try:
            with open(self.counters_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading counters: {e}")
            return {"counters": {}}
    
    def _save_counters(self, data: dict):
        data["last_updated"] = datetime.now().isoformat()
        with open(self.counters_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _extract_agency_initials(self, agency_name: str) -> str:
        
        if not agency_name:
            return "XX"
        
        # Remove special characters and extra spaces
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', agency_name)
        words = cleaned.split()
        
        if len(words) >= 2:
            # Take first letter of first two words
            initials = words[0][0].upper() + words[1][0].upper()
        elif len(words) == 1:
            # Take first two letters of single word
            if len(words[0]) >= 2:
                initials = words[0][:2].upper()
            else:
                initials = (words[0][0] + "X").upper()
        else:
            initials = "XX"
        
        return initials
    
    def _get_date_string(self, date: Optional[datetime] = None) -> str:
        
        if date is None:
            date = datetime.now()
        
        return date.strftime("%y%m%d")
    
    def _get_counter_key(self, agency_initials: str, date_string: str) -> str:
        
        return f"{agency_initials}_{date_string}"
    
    def generate_ticket_number(
        self, 
        agency_name: str, 
        date: Optional[datetime] = None
    ) -> str:
        
        initials = self._extract_agency_initials(agency_name)
        
        date_string = self._get_date_string(date)
        
        counter_key = self._get_counter_key(initials, date_string)
        
        data = self._load_counters()
        counters = data.get("counters", {})
        
        current_count = counters.get(counter_key, 0)
        
        new_count = current_count + 1
        counters[counter_key] = new_count
        
        data["counters"] = counters
        self._save_counters(data)
        
        serial = f"{new_count:02d}"
        
        ticket_number = f"A{initials}{date_string}{serial}"
        
        print(f"Generated ticket number: {ticket_number} (Agency: {agency_name}, Date: {date_string}, Serial: {serial})")
        
        return ticket_number
    
    def get_todays_count(self, agency_name: str) -> int:
       
        initials = self._extract_agency_initials(agency_name)
        date_string = self._get_date_string()
        counter_key = self._get_counter_key(initials, date_string)
        
        data = self._load_counters()
        counters = data.get("counters", {})
        
        return counters.get(counter_key, 0)
    
    def get_statistics(self) -> dict:
        
        data = self._load_counters()
        counters = data.get("counters", {})
        
        total_tickets = sum(counters.values())
        
        today = self._get_date_string()
        
        todays_tickets = sum(
            count for key, count in counters.items() 
            if key.endswith(today)
        )
        
        return {
            "total_tickets_generated": total_tickets,
            "todays_tickets": todays_tickets,
            "unique_agency_date_combinations": len(counters)
        }


# Singleton instance
_ticket_number_manager_instance = None

def get_ticket_number_manager() -> TicketNumberManager:
    """Get or create TicketNumberManager singleton"""
    global _ticket_number_manager_instance
    if _ticket_number_manager_instance is None:
        _ticket_number_manager_instance = TicketNumberManager()
    return _ticket_number_manager_instance