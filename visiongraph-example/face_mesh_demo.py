import argparse

import visiongraph as vg
from MediaPipeFaceMeshWithGeometryEstimator import MediaPipeFaceMeshWithGeometryEstimator


def send_osc(faces: vg.ResultList[vg.BlazeFaceMesh]) -> vg.ResultList[vg.BlazeFaceMesh]:
    # todo: send out osc data

    return faces


def main():
    # parse command line arguments
    parser = argparse.ArgumentParser("FaceMesh with Geometry Example", description="Detect face meshes on images.")
    vg.VisionGraph.add_params(parser)
    args = parser.parse_args()

    # define graph
    graph = (
        vg.create_graph(name="FaceMesh with Geometry Example", input_node=args.input(), handle_signals=True)

        # run detection and pass image through for annotation
        .apply(
            image=vg.passthrough(),
            face_mesh=vg.sequence(MediaPipeFaceMeshWithGeometryEstimator(), vg.custom(send_osc)),
        )

        # annotate result
        .then(
            vg.ResultAnnotator(),
            vg.ImagePreview("Preview")
        )
        .build()
    )
    graph.configure(args)

    # start graph
    graph.open()


if __name__ == "__main__":
    main()
