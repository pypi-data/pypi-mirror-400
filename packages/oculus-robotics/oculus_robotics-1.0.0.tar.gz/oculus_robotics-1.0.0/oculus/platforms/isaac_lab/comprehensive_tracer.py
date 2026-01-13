"""
Comprehensive Isaac Lab Tracer
Captures RL training, episodes, rewards, and physics
"""

import numpy as np
import time
from typing import Dict, Optional, Any
from oculus.core.tracer import BaseTracer


class ComprehensiveIsaacLabTracer(BaseTracer):
    """
    Full RL observability for Isaac Lab
    Captures: Episodes, Rewards, Physics, Policy, Value Functions
    """
    
    def __init__(self, project: str = "isaac_lab_project", auto_capture: bool = True):
        super().__init__(project=project, auto_capture=auto_capture)
        
        # RL tracking
        self.current_episode = 0
        self.episode_rewards = []
        self.episode_lengths = []
        
        # Environment tracking
        self.env = None
        self.num_envs = 0
        
        # Policy tracking
        self.policy_version = None
        self.actions_history = []
        
    def initialize(self, env, policy_version: str = "v1.0"):
        """Initialize with Isaac Lab environment"""
        self.env = env
        self.num_envs = env.num_envs if hasattr(env, 'num_envs') else 1
        self.policy_version = policy_version
        
        # Capture environment config
        env_config = {
            "task_name": env.cfg.name if hasattr(env, 'cfg') else "unknown",
            "num_envs": self.num_envs,
            "num_observations": env.num_obs if hasattr(env, 'num_obs') else 0,
            "num_actions": env.num_actions if hasattr(env, 'num_actions') else 0,
            "episode_length": env.max_episode_length if hasattr(env, 'max_episode_length') else 0,
            "dt": env.dt if hasattr(env, 'dt') else 0.01,
        }
        
        self.log_event("environment_initialized", env_config)
        
    def capture_step(self, obs, actions, rewards, dones, info, step: int):
        """
        Capture comprehensive RL step data
        """
        timestamp = time.time()
        
        # 1. OBSERVATIONS
        obs_data = self._process_observations(obs)
        
        # 2. ACTIONS & POLICY
        action_data = self._process_actions(actions)
        
        # 3. REWARDS
        reward_data = self._process_rewards(rewards)
        
        # 4. PHYSICS STATE (from environment)
        physics_data = self._capture_physics_state()
        
        # 5. EPISODE TRACKING
        episode_data = self._track_episodes(dones, rewards)
        
        # 6. VALUE FUNCTIONS (if available in info)
        value_data = self._extract_value_functions(info)
        
        # 7. SAFETY METRICS
        safety_data = self._compute_rl_safety_metrics(obs, actions, physics_data)
        
        # Comprehensive trace
        trace = {
            "step": step,
            "timestamp": timestamp,
            "observations": obs_data,
            "actions": action_data,
            "rewards": reward_data,
            "physics": physics_data,
            "episodes": episode_data,
            "values": value_data,
            "safety": safety_data,
            "dones": dones.tolist() if hasattr(dones, 'tolist') else dones,
        }
        
        self.trace(trace)
        return trace
        
    def _process_observations(self, obs) -> Dict:
        """Process observation data"""
        if isinstance(obs, dict):
            return {k: v.tolist() if hasattr(v, 'tolist') else v for k, v in obs.items()}
        elif hasattr(obs, 'shape'):
            return {
                "shape": list(obs.shape),
                "mean": float(obs.mean()),
                "std": float(obs.std()),
                "min": float(obs.min()),
                "max": float(obs.max()),
                "sample": obs[0].tolist() if len(obs.shape) > 1 else obs.tolist()
            }
        return {"raw": obs}
        
    def _process_actions(self, actions) -> Dict:
        """Process action data"""
        if hasattr(actions, 'shape'):
            return {
                "shape": list(actions.shape),
                "mean": float(actions.mean()),
                "std": float(actions.std()),
                "min": float(actions.min()),
                "max": float(actions.max()),
                "sample": actions[0].tolist() if len(actions.shape) > 1 else actions.tolist()
            }
        return {"raw": actions}
        
    def _process_rewards(self, rewards) -> Dict:
        """Process reward data"""
        if hasattr(rewards, 'shape'):
            return {
                "total": float(rewards.sum()),
                "mean": float(rewards.mean()),
                "std": float(rewards.std()),
                "min": float(rewards.min()),
                "max": float(rewards.max()),
                "distribution": rewards.tolist() if len(rewards) < 32 else rewards[:32].tolist()
            }
        return {"value": float(rewards)}
        
    def _capture_physics_state(self) -> Dict:
        """Capture physics from Isaac Lab environment"""
        if not self.env:
            return {}
            
        try:
            # Robot state
            robot_states = {}
            if hasattr(self.env, 'robot'):
                robot = self.env.robot
                robot_states = {
                    "root_pos": robot.data.root_pos_w[0].tolist() if hasattr(robot.data, 'root_pos_w') else None,
                    "root_quat": robot.data.root_quat_w[0].tolist() if hasattr(robot.data, 'root_quat_w') else None,
                    "root_vel": robot.data.root_vel_w[0].tolist() if hasattr(robot.data, 'root_vel_w') else None,
                    "joint_pos": robot.data.joint_pos[0].tolist() if hasattr(robot.data, 'joint_pos') else None,
                    "joint_vel": robot.data.joint_vel[0].tolist() if hasattr(robot.data, 'joint_vel') else None,
                }
                
            # Contact forces
            contact_forces = {}
            if hasattr(self.env, 'contact_sensor'):
                sensor = self.env.contact_sensor
                contact_forces = {
                    "net_forces": sensor.data.net_forces_w[0].tolist() if hasattr(sensor.data, 'net_forces_w') else None,
                    "force_matrix": sensor.data.force_matrix_w[0].tolist() if hasattr(sensor.data, 'force_matrix_w') else None,
                }
                
            return {
                "robot": robot_states,
                "contacts": contact_forces,
            }
        except Exception as e:
            return {"error": str(e)}
            
    def _track_episodes(self, dones, rewards) -> Dict:
        """Track episode statistics"""
        if hasattr(dones, '__iter__'):
            num_done = sum(dones)
            if num_done > 0:
                self.current_episode += num_done
                self.episode_rewards.extend([float(r) for r, d in zip(rewards, dones) if d])
                
        return {
            "current_episode": self.current_episode,
            "episodes_completed": len(self.episode_rewards),
            "avg_reward": float(np.mean(self.episode_rewards[-100:])) if self.episode_rewards else 0.0,
            "best_reward": float(max(self.episode_rewards)) if self.episode_rewards else 0.0,
        }
        
    def _extract_value_functions(self, info) -> Dict:
        """Extract value function estimates"""
        if isinstance(info, dict):
            return {
                "values": info.get("values", None),
                "advantages": info.get("advantages", None),
                "returns": info.get("returns", None),
            }
        return {}
        
    def _compute_rl_safety_metrics(self, obs, actions, physics) -> Dict:
        """Compute RL-specific safety metrics"""
        return {
            "action_magnitude": float(np.linalg.norm(actions)) if hasattr(actions, 'shape') else 0.0,
            "action_variance": float(np.var(actions)) if hasattr(actions, 'shape') else 0.0,
            "observation_anomaly": self._detect_obs_anomaly(obs),
            "physics_stability": self._assess_physics_stability(physics),
        }
        
    def _detect_obs_anomaly(self, obs) -> float:
        """Detect anomalies in observations"""
        if hasattr(obs, 'shape'):
            # Simple anomaly detection: check for NaN or extreme values
            has_nan = np.isnan(obs).any()
            has_inf = np.isinf(obs).any()
            return 1.0 if (has_nan or has_inf) else 0.0
        return 0.0
        
    def _assess_physics_stability(self, physics) -> float:
        """Assess physics stability (0-1, higher is better)"""
        if not physics or 'robot' not in physics:
            return 1.0
            
        robot = physics['robot']
        if robot.get('root_vel'):
            vel = np.array(robot['root_vel'])
            velocity_magnitude = np.linalg.norm(vel)
            # Normalize to 0-1 (assume max safe velocity is 10 m/s)
            return max(0.0, 1.0 - velocity_magnitude / 10.0)
        return 1.0
