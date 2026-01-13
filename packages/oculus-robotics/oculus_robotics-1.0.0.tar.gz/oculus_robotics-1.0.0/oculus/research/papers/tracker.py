"""
Research Papers Tracking
Document implemented papers and experiments
"""

IMPLEMENTED_PAPERS = {
    "radium": {
        "title": "Radium: Learning Robust Controllers for Quadruped Locomotion",
        "status": "in_progress",
        "implementations": [
            "safe_fall.py - SafeFallQuadruped class",
        ],
        "notes": "Implementing safe fall strategies from Section 4.2"
    },
    
    "capture_point": {
        "title": "Capture Point: A Step toward Humanoid Push Recovery",
        "status": "planned",
        "implementations": [],
        "notes": "Will implement capture point calculations for bipeds"
    },
    
    "zmp_control": {
        "title": "Zero-Moment Point for Legged Robot Stability",
        "status": "in_progress",
        "implementations": [
            "comprehensive_tracer.py - ZMP computation",
        ],
        "notes": "ZMP tracking implemented in tracers"
    },
}

EXPERIMENT_LOG = {
    "exp_001_unitree_fall_detection": {
        "date": "2025-01-01",
        "robot": "Unitree Go1",
        "objective": "Test fall detection accuracy",
        "results": "Pending",
        "dataset": "data/unitree_falls_v1.pkl"
    },
    
    # Add more experiments as team runs them
}
