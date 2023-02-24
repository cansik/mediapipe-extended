# Mediapipe-Extended
Mediapipe for Python with extended solution support. The aim of this repository is to add solutions to mediapipe that are not included in the original mediapipe Python package.

### Installation

```
pip install -r requirements.txt
```

### Face Geometry
The Face Geometry solution allows the head transformation matrix to be recovered from the landmark detection. This enables face effects or undistorted landmark analysis.

![Face Geometry Example](media/face-geometry-recording.gif)

```bash
python examples/FaceGeometryExample.py
```

### Build
To create a wheel package, set up your computer as described in [Mediapipe: Getting_Started](https://google.github.io/mediapipe/getting_started/python.html#mediapipe-python-framework) and run the following command (Powershell Core is required).

```bash
pwsh tools/build.ps1
```

