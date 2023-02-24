import cv2
import mediapipe as mp
import numpy as np
import open3d as o3d
from open3d.cpu.pybind.visualization import RenderOption

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh_with_geometry


class Preview:
    def __init__(self):
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(height=720, width=720)
        render_options: RenderOption = self.vis.get_render_option()
        render_options.point_size = 5
        render_options.background_color = [0, 0, 0]

        self.pcd = o3d.geometry.PointCloud()
        points = np.random.rand(10, 3)
        self.pcd.points = o3d.utility.Vector3dVector(points)
        self.vis.add_geometry(self.pcd)

        self.reset_view_proposed = True

    def display_mesh(self, geometry, projected: bool = False):
        # read raw information
        raw_mat = geometry.pose_transform_matrix
        pose_transform_mat = np.asarray(raw_mat.packed_data).reshape(raw_mat.cols, raw_mat.rows)
        vertices = np.asarray(geometry.mesh.vertex_buffer).reshape((-1, 5))
        vertices = vertices[:, :3]

        if projected:
            # calculate inverse matrix
            inv_pose_transform_mat = np.linalg.inv(pose_transform_mat)
            vertices = self._transform(vertices, inv_pose_transform_mat)

        points = vertices

        self.pcd.points.clear()
        self.pcd.points.extend(points)

    def display_landmarks(self, landmarks):
        landmarks = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])

        points = landmarks
        points[:, 1] *= -1
        points[:, 2] *= -1

        self.pcd.points.clear()
        self.pcd.points.extend(points)

    @staticmethod
    def _transform(vertices: np.ndarray, transform_mat: np.ndarray) -> np.ndarray:
        vertices = np.insert(vertices, 3, 1, axis=1)
        transformed_vertices = np.dot(transform_mat, vertices.T).T
        return transformed_vertices[:, :3]

    def update(self):
        self.vis.update_geometry(self.pcd)

        if self.reset_view_proposed:
            self.vis.reset_view_point(True)
            self.reset_view_proposed = False

        self.vis.poll_events()
        self.vis.update_renderer()

    def close(self):
        self.vis.destroy_window()


def main():
    # For webcam input:
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    cap = cv2.VideoCapture("media/video-480.mov")

    preview = Preview()

    with mp_face_mesh.FaceMeshWithGeometry(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as face_mesh:

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # Flip the image horizontally for a later selfie-view display, and convert
            # the BGR image to RGB.
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            results = face_mesh.process(image)

            # Draw the face mesh annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_tesselation_style())
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_contours_style())

            if results.multi_face_geometry:
                for i, geometry in enumerate(results.multi_face_geometry):
                    landmarks = results.multi_face_landmarks[i]
                    # preview.display_landmarks(landmarks.landmark)
                    preview.display_mesh(geometry, projected=False)

            cv2.imshow('MediaPipe FaceMesh', image)
            preview.update()
            if cv2.waitKey(1) & 0xFF == 27:
                break
        preview.close()
        cap.release()


if __name__ == "__main__":
    main()
