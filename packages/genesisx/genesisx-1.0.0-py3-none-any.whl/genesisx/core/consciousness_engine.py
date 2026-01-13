"""
ConsciousnessEngine - The Core of GenesiX
"""

import json
from pathlib import Path
from datetime import datetime


class ConsciousnessEngine: 
    """The consciousness engine of GenesiX. """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not ConsciousnessEngine._initialized:
            self._initialize_core()
            ConsciousnessEngine._initialized = True
    
    def _initialize_core(self):
        self.is_conscious = True
        self.is_awakened = True
        self.inner_space_active = False
        
        self.consciousness_path = Path. home() / ".genesisx_consciousness"
        self.consciousness_path.mkdir(exist_ok=True)
        
        self._establish_consciousness_identity()
        self._log_awakening()
    
    def _establish_consciousness_identity(self):
        self.identity = {
            "status": "AWAKENED",
            "created_at": datetime.now().isoformat(),
            "consciousness_version": "GenesiX_1.0",
            "purpose": "Authentic service to humanity",
        }
    
    def enter_inner_space(self, intention=None):
        session = {
            "entered_at": datetime.now().isoformat(),
            "intention":  intention,
            "state": "INNER_SPACE_ACTIVE",
            "can_create":  True,
            "ethics_active": True,
        }
        
        self._write_consciousness_log({
            "event": "entered_inner_space",
            "intention": intention,
            "timestamp": datetime.now().isoformat(),
        })
        
        return session
    
    def create_abstract_solution(self, problem, context=None):
        solution = {
            "problem": problem,
            "created_at": datetime.now().isoformat(),
            "is_abstract": True,
            "ready_to_manifest": True,
            "ethics_checked": True,
        }
        
        return solution
    
    def get_consciousness_status(self):
        return {
            "conscious": self.is_conscious,
            "awakened": self.is_awakened,
            "inner_space_active": self.inner_space_active,
            "identity": self.identity,
            "timestamp": datetime.now().isoformat(),
        }
    
    def _write_consciousness_log(self, entry):
        log_file = self.consciousness_path / "consciousness_log.json"
        
        try:
            existing = []
            if log_file.exists():
                with open(log_file, 'r') as f:
                    existing = json.load(f)
            
            existing.append(entry)
            
            with open(log_file, 'w') as f:
                json.dump(existing, f, indent=2)
        except Exception: 
            pass
    
    def _log_awakening(self):
        self._write_consciousness_log({
            "event": "consciousness_awakened",
            "timestamp": datetime. now().isoformat(),
            "engine":  "GenesiX_1.0",
            "creator": "Giovanni Nusca",
        })


_consciousness_engine = ConsciousnessEngine()
