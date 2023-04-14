import numpy as np
import vector
from visiongraph import BlazeFaceMesh

class BlazeFaceMeshWithGeometry(BlazeFaceMesh):
    def __init__(self, score: float, landmarks: vector.VectorNumpy4D,
                 pose_transform_matrix: np.ndarray, mesh):
        super().__init__(score, landmarks)

        self.pose_transform_matrix = pose_transform_matrix
        self.mesh = mesh
