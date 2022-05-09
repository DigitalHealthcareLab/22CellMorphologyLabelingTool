from pathlib import Path

import numpy as np
import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "st_custom_image_labeller",
        url="http://localhost:3001",
    )
else:
    parent_dir = Path(__file__).parent
    build_dir = Path(parent_dir, "frontend/build")
    _component_func = components.declare_component(
        "st_custom_image_labeller", path=str(build_dir)
    )


def st_custom_image_labeller(
    resized_img, point_color="blue", point=None, key=None
):
    """Create a new instance of "st_img_label".
    Parameters
    ----------
    img_file: PIL.Image
        The image to be croppepd
    point_color: string
        The color of the pointer's point. Defaults to blue.
    rects: list
        list of points that already exists.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    Returns
    -------
    points: list
        list of points.
    """
    # Get arguments to send to frontend
    canvasWidth = resized_img.width
    canvasHeight = resized_img.height

    # Translates image to a list for passing to Javascript
    imageData = np.array(resized_img.convert("RGBA")).flatten().tolist()
    if point is None:
        point_x = canvasWidth // 2
        point_y = canvasHeight // 2
    else:
        point_x, point_y = point

    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # Defaults to a box whose vertices are at 20% and 80% of height and width.
    # The _recommended_box function could be replaced with some kind of image
    # detection algorith if it suits your needs.
    component_value = _component_func(
        canvasWidth=canvasWidth,
        canvasHeight=canvasHeight,
        point={"x": point_x, "y": point_y},
        pointColor=point_color,
        imageData=imageData,
        key=key,
    )
    # Return a cropped image using the box from the frontend
    if component_value:
        return component_value
    else:
        return {"x": point_x, "y": point_y}
