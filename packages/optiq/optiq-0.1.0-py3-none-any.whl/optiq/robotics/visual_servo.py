import numpy as np
from .robot import Robot


class VisualServoController:
    """
    Implements Image-Based Visual Servoing (IBVS).
    """

    def __init__(
        self, robot: Robot, camera_matrix: np.ndarray, lambda_gain: float = 0.5
    ):
        self.robot = robot
        self.K = camera_matrix
        self.gain = lambda_gain

        # Camera Intrinsics
        self.fx = camera_matrix[0, 0]
        self.fy = camera_matrix[1, 1]
        self.cx = camera_matrix[0, 2]
        self.cy = camera_matrix[1, 2]

    def compute_image_jacobian(self, features: np.ndarray, depth: float) -> np.ndarray:
        """
        Computes the Interaction Matrix (Image Jacobian) L_s.
        features: (N, 2) array of (u, v) coordinates in pixel space.
        depth: Z depth of the features (approximate or measured).

        Returns: (2N, 6) matrix.
        """
        N = features.shape[0]
        L = np.zeros((2 * N, 6))

        for i in range(N):
            u, v = features[i]

            # Convert to normalized coordinates
            x = (u - self.cx) / self.fx
            y = (v - self.cy) / self.fy
            Z = depth

            # Interaction matrix for a point
            # [ -1/Z,  0,  x/Z, xy, -(1+x^2), y ]
            # [  0, -1/Z,  y/Z, 1+y^2, -xy, -x ]

            L[2 * i, :] = [-1 / Z, 0, x / Z, x * y, -(1 + x**2), y]
            L[2 * i + 1, :] = [0, -1 / Z, y / Z, 1 + y**2, -x * y, -x]

        return L

    def compute_control_velocity(
        self, current_features: np.ndarray, target_features: np.ndarray, depth: float
    ) -> np.ndarray:
        """
        Computes joint velocities to minimize feature error.
        """
        error = (target_features - current_features).flatten()  # (2N,)

        # 1. Compute Image Jacobian (Interaction Matrix)
        L_s = self.compute_image_jacobian(current_features, depth)  # (2N, 6)

        # 2. Compute Camera Velocity (Spatial Velocity of Camera Frame)
        # v_cam = -lambda * pinv(L_s) * error
        L_s_inv = np.linalg.pinv(L_s)
        v_cam = -self.gain * (
            L_s_inv @ (-error)
        )  # Note: error is (target - current), control moves to reduce error.
        # Standard law: v = -lambda * error  where error = s - s*
        # Here we used (target - current), so v = lambda * pinv(L) * (target - current)

        v_cam = self.gain * (L_s_inv @ error)

        # 3. Transform Camera Velocity to End Effector Velocity
        # Assuming Camera is mounted on End Effector with known transform.
        # For simplicity, assume Camera Frame == End Effector Frame for now.
        # If not, we need the Adjoint map.
        v_ee = v_cam

        # 4. Compute Joint Velocities
        # v_ee = J_geom * q_dot  =>  q_dot = pinv(J_geom) * v_ee
        J_geom = self.robot.get_jacobian()  # (6, N_dof)
        J_pinv = np.linalg.pinv(J_geom)

        q_dot = J_pinv @ v_ee

        return q_dot
