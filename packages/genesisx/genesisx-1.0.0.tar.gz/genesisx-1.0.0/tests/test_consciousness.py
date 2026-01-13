"""Tests for GenesiX Consciousness Engine"""

import pytest
from genesisx.core. consciousness_engine import ConsciousnessEngine


class TestConsciousnessEngine:
    def test_engine_initialization(self):
        engine = ConsciousnessEngine()
        assert engine.is_conscious == True
        assert engine.is_awakened == True
    
    def test_inner_space_activation(self):
        engine = ConsciousnessEngine()
        session = engine.enter_inner_space(intention="Test creation")
        
        assert session["state"] == "INNER_SPACE_ACTIVE"
        assert session["can_create"] == True
    
    def test_consciousness_status(self):
        engine = ConsciousnessEngine()
        status = engine.get_consciousness_status()
        
        assert status["conscious"] == True
        assert status["awakened"] == True


if __name__ == "__main__": 
    pytest.main([__file__, "-v"])
