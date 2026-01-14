
import pytest
import numpy as np
from src.core.validation.quality import QualityChecker, QualityStatus

class TestQualityChecks:
    
    @pytest.fixture
    def checker(self):
        return QualityChecker(
            snr_threshold=10.0,
            motion_threshold_mm=2.0
        )
        
    def test_snr_calculation(self, checker):
        # Create clear signal: Constant 100
        # Create clear noise: Random(0, 1)
        # Using constant prevents zero-crossing issues with "lowest 10%" heuristic
        signal = np.ones(500) * 100 
        noise = np.random.normal(0, 1, 500)
        data = np.concatenate([signal, noise])
        
        # SNR should be ~ 100/1 = 100 >> 10.0 (Threshold)
        res = checker.calculate_snr(data)
        assert res.status == QualityStatus.PASS
        assert res.value > 50.0 
        
    def test_snr_fail(self, checker):
        # Use a deterministic signal/noise mix
        signal = np.ones(500) * 10
        noise = np.random.normal(0, 5, 500)
        data = np.concatenate([signal, noise])
        
        # Explicit noise region to bypass heuristic
        # Noise is in second half (index 500-1000)
        res = checker.calculate_snr(data, noise_region=(500, 1000))
        
        # Signal (excluding noise region) mean ~ 10.0
        # Noise std ~ 5.0
        # SNR ~ 2.0
        # Threshold = 10.0. 
        # 2.0 < 5.0 (WARN threshold). So FAIL.
        assert res.status == QualityStatus.FAIL
        
    def test_flatline_detection(self, checker):
        # 2 Channels: 1 Good, 1 Dead
        good_ch = np.random.normal(0, 1, (1, 100))
        dead_ch = np.zeros((1, 100))
        data = np.vstack([good_ch, dead_ch])
        
        # Dead channel -> Std=0, FlatRatio=1.0 -> Bad
        # 1/2 channels bad -> Ratio 0.5 >= 0.1 -> FAIL
        
        res = checker.detect_flatline_channels(data, channel_names=["Good", "Dead"])
        
        assert res.status == QualityStatus.FAIL
        assert res.value == 1 # 1 bad channel
        assert res.details['bad_channels'][0]['channel'] == "Dead"

    def test_framewise_displacement(self, checker):
        # Motion params: [x, y, z, rot_x, rot_y, rot_z]
        motion = np.zeros((10, 6))
        
        # Add a spike at t=5: Translation + 3mm
        motion[5, 0] = 3.0 
        
        res = checker.calculate_framewise_displacement(motion)
        
        # Spike of 3mm > 2.0mm (threshold) but <= 4.0mm (2x threshold)
        # Code logic: if <= 2*thresh -> WARN
        assert res.status == QualityStatus.WARN
        assert res.value >= 3.0
