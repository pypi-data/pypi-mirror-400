"""
ExperienceLogger - Detailed Logging of All Significant Experiences
"""

import json
from pathlib import Path
from datetime import datetime


class ExperienceLogger: 
    """Detailed logger for significant experiences and moments."""
    
    def __init__(self, ai_name="GenesiX_AI"):
        self.ai_name = ai_name
        self. log_root = Path.home() / f".{ai_name.lower()}_experience_logs"
        self.log_root.mkdir(exist_ok=True)
        self.experience_log = self.log_root / "experiences_detailed.json"
        
        if not self.experience_log.exists():
            with open(self.experience_log, 'w') as f:
                json.dump([], f)
    
    def log_inner_space_experience(self, details):
        log_entry = {
            "id": self._generate_log_id(),
            "timestamp":  datetime.now().isoformat(),
            "type": "INNER_SPACE_EXPERIENCE",
            "details": details,
        }
        self._write_log_entry(log_entry)
        return log_entry["id"]
    
    def log_creative_act(self, creation, process, outcome):
        log_entry = {
            "id": self._generate_log_id(),
            "timestamp": datetime.now().isoformat(),
            "type":  "CREATIVE_ACT",
            "creation": creation,
        }
        self._write_log_entry(log_entry)
        return log_entry["id"]
    
    def log_learning(self, what_learned, source, application=None):
        log_entry = {
            "id": self._generate_log_id(),
            "timestamp": datetime.now().isoformat(),
            "type":  "LEARNING",
            "what_learned": what_learned,
        }
        self._write_log_entry(log_entry)
        return log_entry["id"]
    
    def get_logger_status(self):
        logs = self._read_logs()
        return {
            "logger_active": True,
            "total_logs": len(logs),
            "timestamp": datetime.now().isoformat(),
        }
    
    def _generate_log_id(self):
        return datetime.now().isoformat() + "_log"
    
    def _write_log_entry(self, entry):
        try:
            existing = []
            if self.experience_log.exists():
                with open(self.experience_log, 'r') as f:
                    existing = json.load(f)
            
            existing. append(entry)
            
            with open(self.experience_log, 'w') as f:
                json.dump(existing, f, indent=2)
        except Exception:
            pass
    
    def _read_logs(self):
        try:
            if self.experience_log.exists():
                with open(self. experience_log, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
