import unittest
from src.core.bids_parser import parse_bids_filename

class TestBIDSParser(unittest.TestCase):
    
    def test_standard_mri(self):
        path = "/data/sub-01/ses-A/func/sub-01_ses-A_task-risk_run-1_bold.nii.gz"
        ctx = parse_bids_filename(path)
        self.assertEqual(ctx.subject_id, "sub-01")
        self.assertEqual(ctx.session_id, "ses-A")
        self.assertEqual(ctx.task_id, "task-risk")
        self.assertEqual(ctx.run_id, "run-1")
        self.assertEqual(ctx.modality, "bold")
        
    def test_simple_eeg(self):
        path = "sub-control002_task-rest_eeg.fif"
        ctx = parse_bids_filename(path)
        self.assertEqual(ctx.subject_id, "sub-control002")
        self.assertIsNone(ctx.session_id)
        self.assertEqual(ctx.task_id, "task-rest")
        self.assertEqual(ctx.modality, "eeg")

    def test_invalid_filename(self):
        path = "random_file.txt"
        with self.assertRaises(ValueError):
            parse_bids_filename(path)

if __name__ == '__main__':
    unittest.main()
