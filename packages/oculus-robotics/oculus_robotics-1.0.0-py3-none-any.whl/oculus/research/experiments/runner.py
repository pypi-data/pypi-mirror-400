"""
Experiment Runner
Research team uses this to run controlled experiments
"""

import json
import time
from pathlib import Path
from typing import Dict, Any


class ExperimentRunner:
    """
    Framework for running reproducible experiments
    """
    
    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        self.start_time = None
        self.results = {}
        
        # Create experiment directory
        self.exp_dir = Path(f"experiments/{experiment_name}_{int(time.time())}")
        self.exp_dir.mkdir(parents=True, exist_ok=True)
        
    def setup(self, config: Dict[str, Any]):
        """Setup experiment with config"""
        self.config = config
        
        # Save config
        with open(self.exp_dir / "config.json", "w") as f:
            json.dump(config, f, indent=2)
            
        self.start_time = time.time()
        
    def log_result(self, key: str, value: Any):
        """Log experiment result"""
        self.results[key] = value
        
    def save_results(self):
        """Save experiment results"""
        self.results["duration_seconds"] = time.time() - self.start_time
        
        with open(self.exp_dir / "results.json", "w") as f:
            json.dump(self.results, f, indent=2)
            
        print(f"✅ Experiment saved to {self.exp_dir}")
