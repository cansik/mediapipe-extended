# Mediapipe-Extended
Mediapipe for python with extended solution support. The aim of this repository is to add solutions to mediapipe which are not contained in the original mediapipe python package.

### Installation

```
pip install -r requirements.txt
```

### Face Geometry
The Face Geometry solution allows to get back the head transformation matrix from the landmark detection. This allows for face effects or undistorted analysis of the landmarks.

![Face Geometry Example](media/face-geometry-recording.gif)

```bash
python examples/FaceGeometryExample.py
```

### Build
To build a wheel package setup your machine as described in [Mediapipe: Getting_Started](https://google.github.io/mediapipe/getting_started/python.html#mediapipe-python-framework) and run the following command (Powershell Core is required).

```bash
pwsh tools/build.ps1
```

