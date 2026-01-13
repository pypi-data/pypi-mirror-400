"""
MuJoCo Platform
"""

from .tracer import MujocoTracer

__all__ = ["MujocoTracer"]
    """
    Tracer for Mujoco simulations.
    
    Usage:
        from oculus.platforms.mujoco import MujocoTracer
        import mujoco
        
        with MujocoTracer(project="mujoco_sim") as tracer:
            model = mujoco.MjModel.from_xml_path("robot.xml")
            data = mujoco.MjData(model)
            
            for step in range(1000):
                mujoco.mj_step(model, data)
                
                tracer.auto_capture({
                    "qpos": data.qpos.tolist(),
                    "qvel": data.qvel.tolist(),
                    "qacc": data.qacc.tolist()
                })
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.platform = "mujoco"
        
    def capture_mujoco_state(self, data):
        """Helper to capture Mujoco state"""
        return {
            "qpos": data.qpos.tolist(),
            "qvel": data.qvel.tolist(),
            "qacc": data.qacc.tolist(),
            "time": data.time
        }
