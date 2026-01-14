import unittest
import os
from src.core.audit_log import AuditLogger
from src.core.bids_parser import parse_bids_filename
from src.core.db import init_db

class TestAuditLog(unittest.TestCase):
    
    def setUp(self):
        self.test_db = "test_neuroops.db"
        init_db(self.test_db)
        self.logger = AuditLogger(self.test_db)
        
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
    def test_log_cycle(self):
        # 1. Create Context
        ctx = parse_bids_filename("sub-01_task-rest_bold.nii")
        
        # 2. Log Decision
        record = self.logger.log_decision(
            user_id="dr_who",
            bids_context=ctx,
            file_hash="sha256:123456",
            status="REJECTED",
            flags={"reason": "motion"}
        )
        
        # 3. Verify
        self.assertEqual(record.status, "REJECTED")
        self.assertEqual(record.bids_context.subject_id, "sub-01")

if __name__ == '__main__':
    unittest.main()
