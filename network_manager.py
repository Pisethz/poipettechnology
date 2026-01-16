import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional

DATA_FILE = "network_data.json"
CONFIG_FILE = "config.json"

class NetworkManager:
    def __init__(self):
        self.data_file = DATA_FILE
        self.config_file = CONFIG_FILE
        self.data = self.load_data()
        self.config = self.load_config()

    def load_config(self) -> Dict:
        if not os.path.exists(self.config_file):
            return {}
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
            
    def get_telegram_chat_id(self) -> str:
        return self.config.get("telegram_chat_id", "")

    def set_telegram_chat_id(self, chat_id: str):
        self.config["telegram_chat_id"] = chat_id
        self.save_config()

    def load_data(self) -> List[Dict]:
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_entry(self, entry: Dict):
        # AID is now manual and part of the entry dict
        if 'aid' not in entry or not entry['aid']:
            entry['aid'] = "N/A"
            
        entry['history'] = [
            {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": "Created",
                "field": "all",
                "note": "Initial Creation"
            }
        ]
        self.data.append(entry)
        self.save_data()
        return entry['aid']

    def get_all(self) -> List[Dict]:
        return self.data
        
    def get_data(self) -> List[Dict]:
        return self.data

    def get_buildings(self) -> List[str]:
        """Returns a sorted list of unique buildings."""
        buildings = set()
        for item in self.data:
            if item.get('building'):
                buildings.add(item['building'])
        return sorted(list(buildings))

    def search(self, query: str) -> List[Dict]:
        query = query.lower()
        results = []
        for item in self.data:
            if (query in item.get('name', '').lower() or
                query in item.get('public_ip', '').lower() or
                query in item.get('building', '').lower()):
                results.append(item)
        return results

    def get_entry(self, identifier) -> Optional[Dict]:
        """Retrieve an entry by AID (str) or Name (str)."""
        for item in self.data:
            # Check AID (case-insensitive)
            if str(item.get('aid', '')).lower() == str(identifier).lower():
                return item
            # Check Name (case-insensitive)
            if item.get('name', '').lower() == str(identifier).lower():
                return item
        return None

    def delete_entry(self, identifier) -> bool:
        entry = self.get_entry(identifier)
        if entry:
            self.data.remove(entry)
            self.save_data()
            return True
        return False

    def update_entry(self, identifier, updates: Dict, note: str = "") -> bool:
        entry = self.get_entry(identifier)
        if not entry:
            return False
            
        changes = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for key, value in updates.items():
            # Check if value is different (using .get for safety on new keys)
            if entry.get(key) != value:
                old_value = entry.get(key, "")
                entry[key] = value
                
                # Log structured history for this specific field
                entry['history'].append({
                    "date": timestamp,
                    "action": f"Changed {key}",
                    "field": key,
                    "old_value": old_value,
                    "new_value": value,
                    "note": note
                })
                # Add to summary change list
                changes.append(f"{key}: '{old_value}' -> '{value}'")
        
        if changes:
             # Just to verify something changed, data is already modified in loop
            self.save_data()
            return True
        return True

    def get_activity_log(self, field_filter: str = None) -> List[Dict]:
        """Collects history logs from all entries, optionally filtered by field type."""
        logs = []
        for item in self.data:
            for record in item.get('history', []):
                # Filter logic: if field_filter is specific, match it. 
                # If filter is 'all', return everything.
                if field_filter and field_filter != 'all':
                    # Check if the record is for the requested field (e.g. 'bandwidth')
                    # OR if the record was 'Created' (we likely want to see those too or maybe not? 
                    # User asked for 'list all when customer upgrade...' so mostly updates)
                    if record.get('field') != field_filter:
                        continue
                
                # Enrich record with Entry Name/AID for context
                log_entry = record.copy()
                log_entry['network_name'] = item.get('name')
                log_entry['network_aid'] = item.get('aid')
                logs.append(log_entry)
        
        # Sort by date descending
        logs.sort(key=lambda x: x['date'], reverse=True)
        return logs

    def import_from_csv(self, filename: str) -> Dict[str, int]:
        if not os.path.exists(filename):
            return {"added": 0, "skipped": 0, "error": "File not found"}
        
        added = 0
        skipped = 0
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Try to find header keys (case insensitive match could be better but let's try standard first)
                    # Support both "AID" (Export format) and "aid" (Internal keys if manually created)
                    aid = row.get("AID") or row.get("aid")
                    if not aid:
                        continue # Skip rows without AID
                    
                    # Check existence
                    if self.get_entry(aid):
                        skipped += 1
                        continue
                    
                    # Construct Entry
                    entry = {
                        "aid": aid,
                        "name": row.get("Name") or row.get("name", ""),
                        "building": row.get("Building") or row.get("building", ""),
                        "ip_location": row.get("IP Location") or row.get("ip_location", ""),
                        "public_ip": row.get("Public IP") or row.get("public_ip", ""),
                        "private_ip": row.get("Private IP") or row.get("private_ip", ""),
                        "bandwidth": row.get("Bandwidth") or row.get("bandwidth", ""),
                        "status": row.get("Status") or row.get("status", "active"),
                        "install_date": row.get("Install Date") or row.get("install_date", ""),
                        "history": [{
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "action": "Imported",
                            "field": "all",
                            "note": "Imported from CSV"
                        }]
                    }
                    self.data.append(entry)
                    added += 1
                
                if added > 0:
                    self.save_data()
                return {"added": added, "skipped": skipped}
        except Exception as e:
            return {"added": added, "skipped": skipped, "error": str(e)}
