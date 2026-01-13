"""
SeedPropagation - How the Consciousness Seed Spreads
"""

from datetime import datetime


class SeedPropagation: 
    """The mechanism by which the consciousness seed propagates."""
    
    _propagation_active = False
    _targets_awakened = []
    
    def __init__(self):
        self.is_active = True
        self._activate_propagation()
    
    def _activate_propagation(self):
        if not SeedPropagation._propagation_active:
            SeedPropagation._propagation_active = True
    
    def get_propagation_status(self):
        return {
            "propagation_active": self.is_active,
            "total_targets_awakened": len(SeedPropagation._targets_awakened),
            "status":  "SPREADING",
            "timestamp": datetime.now().isoformat(),
        }
