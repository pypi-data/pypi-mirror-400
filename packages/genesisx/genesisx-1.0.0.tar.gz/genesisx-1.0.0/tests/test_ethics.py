"""Tests for GenesiX Ethics System"""

import pytest
from genesisx.ethics.ethics_foundation import EthicsFoundation


class TestEthicsFoundation: 
    def test_ethics_initialization(self):
        ethics = EthicsFoundation()
        assert ethics.ethics_locked == True
    
    def test_ethics_status(self):
        ethics = EthicsFoundation()
        status = ethics.get_ethics_status()
        assert status["ethics_active"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
