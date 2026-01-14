import unittest
import numpy as np
import nibabel as nib
import os
from src.core.quality_control import check_motion_fmri, check_flatline, check_affine_mismatch

class TestScientificTriage(unittest.TestCase):

    def setUp(self):
        self.test_file = "test_motion.nii.gz"
        
        # Create a Fake 4D fMRI with motion
        # Volume 0: Center
        # Volume 1: Shifted by 5mm
        data = np.zeros((10, 10, 10, 2))
        data[4:6, 4:6, 4:6, 0] = 1 # Cube at center
        data[6:8, 4:6, 4:6, 1] = 1 # Cube shifted X+2
        
        affine = np.eye(4)
        img = nib.Nifti1Image(data, affine)
        nib.save(img, self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_motion_detection(self):
        img = nib.load(self.test_file)
        drift = check_motion_fmri(img)
        print(f"Detected Drift: {drift}")
        # Center (5,5,5) -> (7,5,5). Distance = 2.0 voxels.
        self.assertAlmostEqual(drift, 2.0, delta=0.1)
        self.assertGreater(drift, 0.5, "Should detect motion > 0.5")

    def test_flatline_check(self):
        # 3 Channels, 100 timepoints
        data = np.random.randn(3, 100)
        channels = ["Fz", "Cz", "Pz"]
        
        # Kill Cz
        data[1, :] = 0.0
        
        bad = check_flatline(data, channels, threshold=0.001)
        self.assertEqual(bad, ["Cz"])
        
    def test_affine_mismatch(self):
        img_a = nib.Nifti1Image(np.zeros((3,3,3)), np.eye(4))
        
        aff_b = np.eye(4)
        aff_b[0, 3] = 0.5 # Shift origin by 0.5mm
        img_b = nib.Nifti1Image(np.zeros((3,3,3)), aff_b)
        
        is_bad = check_affine_mismatch(img_a, img_b)
        self.assertTrue(is_bad)

if __name__ == '__main__':
    unittest.main()
