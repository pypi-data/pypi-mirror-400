"""
Isaac Sim Platform Adapter

Integrates Oculus tracing with NVIDIA Isaac Sim.
"""

import numpy as np
from typing import Optional, Any
from ...core.tracer import BaseTracer
from ...core.state import UniversalState
from ...core.config import OculusConfig


class IsaacSimTracer(BaseTracer):
    """Tracer for NVIDIA Isaac Sim"""
    
    def __init__(self, api_key: str, project_name: str, server_url: str = "ws://localhost:8080", **kwargs):
        config = OculusConfig(
            api_key=api_key,
            project_name=project_name,
            websocket_url=server_url,
            framework="isaac_sim",
            robot_type=kwargs.get('robot_type', 'custom')
        )
        super().__init__(config)
        self.robot = kwargs.get('robot', None)
        self.world = kwargs.get('world', None)
        
    def capture_state(self, step: int) -> UniversalState:
        """Capture state from Isaac Sim"""
        import time
        
        if not self.robot:
            raise ValueError("Robot not set. Pass robot object when initializing tracer.")
        
        try:
            # Get robot articulation
            articulation = self.robot
            
            # Get joint states
            joint_positions = articulation.get_joint_positions().tolist()
            joint_velocities = articulation.get_joint_velocities().tolist()
            
            # Get joint efforts/torques
            try:
                joint_torques = articulation.get_applied_joint_efforts().tolist()
            except:
                joint_torques = [0.0] * len(joint_positions)
            
            # Get base state
            position, orientation = articulation.get_world_pose()
            linear_vel = articulation.get_linear_velocity()
            angular_vel = articulation.get_angular_velocity()
            
            # Get contact information if available
            contact_forces = None
            contact_points = None
            try:
                contacts = articulation.get_contact_force()
                if contacts is not None:
                    contact_forces = contacts.tolist() if hasattr(contacts, 'tolist') else []
            except:
                pass
            
            state = UniversalState(
                step=step,
                timestamp=time.time(),
                joint_positions=joint_positions,
                joint_velocities=joint_velocities,
                joint_torques=joint_torques,
                base_position=tuple(position.tolist() if hasattr(position, 'tolist') else position),
                base_orientation=tuple(orientation.tolist() if hasattr(orientation, 'tolist') else orientation),
                base_linear_vel=tuple(linear_vel.tolist() if hasattr(linear_vel, 'tolist') else linear_vel),
                base_angular_vel=tuple(angular_vel.tolist() if hasattr(angular_vel, 'tolist') else angular_vel),
                contact_forces=contact_forces,
                contact_points=contact_points
            )
            
            # Trace the step
            self.trace_step(state)
            
            return state
            
        except Exception as e:
            print(f"⚠️ Failed to capture state: {e}")
            # Return minimal state
            return UniversalState(
                step=step,
                timestamp=time.time(),
                joint_positions=[],
                joint_velocities=[],
                joint_torques=[],
                base_position=(0.0, 0.0, 0.0),
                base_orientation=(0.0, 0.0, 0.0, 1.0),
                base_linear_vel=(0.0, 0.0, 0.0),
                base_angular_vel=(0.0, 0.0, 0.0)
            )


__all__ = ["IsaacSimTracer"]
    """
    OpenTelemetry-based tracer for Isaac Sim
    Captures hierarchical traces of simulation runs
    """
    
    def __init__(
        self,
        service_name: str = "isaac-sim",
        project_name: str = "default",
        collector_endpoint: str = "http://localhost:8080/v1/traces",
        console_export: bool = False
    ):
        self.service_name = service_name
        self.project_name = project_name
        
        # Create resource
        resource = Resource.create({
            "service.name": service_name,
            "project.name": project_name,
            "deployment.environment": "local"
        })
        
        # Set up tracer provider
        provider = TracerProvider(resource=resource)
        
        # Add OTLP exporter
        otlp_exporter = OTLPSpanExporter(endpoint=collector_endpoint)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        
        # Set as global
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(__name__)
        
        self.current_run_id = None
        self.current_episode = None
        self.step_count = 0
        
    @contextmanager
    def trace_simulation_run(self, run_id: str, metadata: Optional[Dict[str, Any]] = None):
        """Trace entire simulation run"""
        self.current_run_id = run_id
        self.step_count = 0
        
        with self.tracer.start_as_current_span(
            "simulation_run",
            attributes={
                "run.id": run_id,
                "run.project": self.project_name,
                **(metadata or {})
            }
        ) as span:
            span.set_attribute("run.start_time", time.time())
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
            finally:
                span.set_attribute("run.end_time", time.time())
                span.set_attribute("run.total_steps", self.step_count)
    
    @contextmanager
    def trace_episode(self, episode_id: int, metadata: Optional[Dict[str, Any]] = None):
        """Trace single episode"""
        self.current_episode = episode_id
        
        with self.tracer.start_as_current_span(
            "episode",
            attributes={
                "episode.id": episode_id,
                "episode.run_id": self.current_run_id,
                **(metadata or {})
            }
        ) as span:
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    
    @contextmanager
    def trace_simulation_step(self, step_data: Optional[Dict[str, Any]] = None):
        """Trace single simulation step"""
        self.step_count += 1
        
        with self.tracer.start_as_current_span(
            "simulation_step",
            attributes={
                "step.number": self.step_count,
                "step.episode": self.current_episode,
                "step.run_id": self.current_run_id,
            }
        ) as span:
            step_start = time.time()
            try:
                yield span
                if step_data:
                    self._add_step_attributes(span, step_data)
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
            finally:
                span.set_attribute("step.duration_ms", (time.time() - step_start) * 1000)
    
    @contextmanager
    def trace_physics_step(self, physics_data: Optional[Dict[str, Any]] = None):
        """Trace physics simulation step"""
        with self.tracer.start_as_current_span(
            "physics_step",
            attributes={"step.number": self.step_count}
        ) as span:
            start = time.time()
            try:
                yield span
                if physics_data:
                    span.set_attribute("physics.timestep", physics_data.get("timestep", 0))
                span.set_status(Status(StatusCode.OK))
            finally:
                span.set_attribute("physics.duration_ms", (time.time() - start) * 1000)
    
    @contextmanager
    def trace_robot_control(self, robot_name: str, control_data: Optional[Dict[str, Any]] = None):
        """Trace robot control computation"""
        with self.tracer.start_as_current_span(
            "robot_control",
            attributes={
                "robot.name": robot_name,
                "step.number": self.step_count
            }
        ) as span:
            start = time.time()
            try:
                yield span
                if control_data:
                    span.set_attribute("control.mode", control_data.get("mode", "unknown"))
                span.set_status(Status(StatusCode.OK))
            finally:
                span.set_attribute("control.duration_ms", (time.time() - start) * 1000)
    
    def log_metric(self, name: str, value: float, attributes: Optional[Dict[str, Any]] = None):
        """Log a metric as span event"""
        current_span = trace.get_current_span()
        if current_span:
            event_attrs = {
                "metric.name": name,
                "metric.value": value,
                "metric.step": self.step_count,
                **(attributes or {})
            }
            current_span.add_event("metric", attributes=event_attrs)
    
    def log_event(self, event_name: str, attributes: Optional[Dict[str, Any]] = None):
        """Log a custom event"""
        current_span = trace.get_current_span()
        if current_span:
            current_span.add_event(
                event_name,
                attributes={
                    "event.step": self.step_count,
                    **(attributes or {})
                }
            )
    
    def _add_step_attributes(self, span, step_data: Dict[str, Any]):
        """Add step data as span attributes"""
        for key, value in step_data.items():
            if isinstance(value, (int, float, str, bool)):
                span.set_attribute(f"step.{key}", value)
    
    def shutdown(self):
        """Shutdown tracer and flush pending spans"""
        provider = trace.get_tracer_provider()
        if hasattr(provider, 'shutdown'):
            provider.shutdown()


__all__ = ['IsaacSimTracer']
