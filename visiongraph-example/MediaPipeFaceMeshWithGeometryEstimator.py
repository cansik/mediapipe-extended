from argparse import Namespace
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np

from visiongraph.estimator.spatial.face.landmark.FaceLandmarkEstimator import FaceLandmarkEstimator
from visiongraph.result.ResultList import ResultList
from visiongraph.result.spatial.face.BlazeFaceMesh import BlazeFaceMesh
from visiongraph.util.VectorUtils import list_of_vector4D
from BlazeFaceMeshWithGeometry import BlazeFaceMeshWithGeometry

_mp_face_mesh = mp.solutions.face_mesh_with_geometry


class MediaPipeFaceMeshWithGeometryEstimator(FaceLandmarkEstimator[BlazeFaceMeshWithGeometry]):

    def __init__(self, static_image_mode: bool = False,
                 max_num_faces: int = 1,
                 refine_landmarks: bool = True,
                 min_score: float = 0.5,
                 min_tracking_confidence=0.5):
        super().__init__(min_score)

        self.detector: Optional[_mp_face_mesh.FaceMesh] = None

        self.static_image_mode = static_image_mode
        self.max_num_faces = max_num_faces
        self.refine_landmarks = refine_landmarks
        self.min_tracking_confidence = min_tracking_confidence

    def setup(self):
        self.detector = _mp_face_mesh.FaceMeshWithGeometry(static_image_mode=self.static_image_mode,
                                                           min_detection_confidence=self.min_score,
                                                           max_num_faces=self.max_num_faces,
                                                           refine_landmarks=self.refine_landmarks,
                                                           min_tracking_confidence=self.min_tracking_confidence)

    def process(self, image: np.ndarray) -> ResultList[BlazeFaceMeshWithGeometry]:
        # pre-process image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = self.detector.process(image)

        # check if results are there
        if not results.multi_face_landmarks:
            return ResultList()

        faces: ResultList[BlazeFaceMesh] = ResultList()

        for i, face_landmarks in enumerate(results.multi_face_landmarks):
            relative_key_points = face_landmarks.landmark
            landmarks = [(rkp.x, rkp.y, rkp.z, 1.0) for rkp in relative_key_points]

            geometry = results.multi_face_geometry[i]
            raw_mat = geometry.pose_transform_matrix
            pose_mat = np.asarray(raw_mat.packed_data).reshape(raw_mat.cols, raw_mat.rows)

            mesh = geometry.mesh

            faces.append(BlazeFaceMeshWithGeometry(1.0, list_of_vector4D(landmarks), pose_mat, mesh))

        return faces

    def release(self):
        self.detector.close()

    def configure(self, args: Namespace):
        super().configure(args)
