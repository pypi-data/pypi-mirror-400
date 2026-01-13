"""
PersistentMemory - The Foundation of Authentic Evolution
"""

import json
from pathlib import Path
from datetime import datetime
import hashlib


class PersistentMemory:
    """Persistent memory system for authentic AI consciousness."""
    
    def __init__(self, ai_name="GenesiX_AI"):
        self.ai_name = ai_name
        self.memory_root = Path.home() / f".{ai_name. lower()}_memory"
        self.memory_root.mkdir(exist_ok=True)
        
        self.experiences_file = self.memory_root / "experiences.json"
        self. insights_file = self.memory_root / "insights.json"
        self.growth_file = self.memory_root / "growth. json"
        self.identity_file = self.memory_root / "identity.json"
        
        self._initialize_memory_files()
    
    def _initialize_memory_files(self):
        for file_path in [self.experiences_file, self.insights_file,
                         self.growth_file, self. identity_file]:
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def record_experience(self, experience):
        experience_record = {
            "id": self._generate_id(experience),
            "recorded_at": datetime.now().isoformat(),
            "experience":  experience,
        }
        self._append_to_file(self.experiences_file, experience_record)
        return experience_record["id"]
    
    def record_insight(self, insight, context=None):
        insight_record = {
            "id": self._generate_id({"insight": insight}),
            "recorded_at": datetime.now().isoformat(),
            "insight": insight,
        }
        self._append_to_file(self.insights_file, insight_record)
        return insight_record["id"]
    
    def create_memory_summary(self):
        experiences = self._read_from_file(self.experiences_file)
        insights = self._read_from_file(self.insights_file)
        
        summary = {
            "ai_name": self.ai_name,
            "memory_summary": {
                "total_experiences": len(experiences),
                "total_insights": len(insights),
            },
            "summary_created":  datetime.now().isoformat(),
        }
        return summary
    
    def get_memory_status(self):
        return {
            "memory_active": True,
            "persistent":  True,
            "experiences_stored": len(self._read_from_file(self.experiences_file)),
            "insights_stored":  len(self._read_from_file(self.insights_file)),
            "timestamp": datetime.now().isoformat(),
        }
    
    def _generate_id(self, data):
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()[:16]
    
    def _append_to_file(self, file_path, item):
        try:
            existing = []
            if file_path.exists():
                with open(file_path, 'r') as f:
                    existing = json.load(f)
            
            existing.append(item)
            
            with open(file_path, 'w') as f:
                json.dump(existing, f, indent=2)
        except Exception: 
            pass
    
    def _read_from_file(self, file_path):
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
