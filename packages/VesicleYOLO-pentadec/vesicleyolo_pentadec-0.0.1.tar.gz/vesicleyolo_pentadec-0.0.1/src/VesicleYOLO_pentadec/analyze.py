import os
import math
import cv2
from ultralytics import YOLO
from tqdm import tqdm


def predict_folder(weights_path: str, images_directory: str, out_directory: str = None, num_slices: int = 256,
                   annotate_rect=True, annotate_ellipse=False, ):
    # Using the path to the weights, load the model using YOLO
    assert weights_path[-3:] == ".pt", f"weights_path must be a .pt file. Currently: {weights_path}"
    model_weights = YOLO(weights_path)

    # If annotating ellipse or rectangle and no out_directory was set, note and set out_directory to something
    if (annotate_ellipse or annotate_rect) and not out_directory:
        print("It seems that, though you're annotating, no out_directory was set. That's fine! Just note that "
              "a new folder, with the name 'VesicleYOLO_annotations' will be created to store the images.")

    # Check if num_slices can be math.sqrt'ed by comparing to length_divider
    length_divider = math.isqrt(num_slices)
    if num_slices != length_divider ** 2:
        print(f"Note that the present input for num_slices ({num_slices}) is not a perfect square;"
              f"thus, there will instead be {length_divider ** 2} slices. This is fine, but I'd recommend not messing "
              f"with this unless you have a good idea of what you're doing.")

    # Initialize vesicle list
    vesicle_array = []

    # Iterate through all image paths
    for file_index in range(0,len(os.listdir(images_directory))):
        # Get filepath based on sorted directory
        path = sorted(os.listdir(images_directory))[file_index]

        # Get path to individual image and pass it into predict_image alongside length divider and model weights
        image_path = os.path.join(images_directory,path)

        # Get image name
        image_name = os.path.basename(image_path)

        # TODO: Make sure all the images are the same shape by getting an initial value for wdt,hgt and saving those
        # TODO this should probably do the annotations alongside returning the freakin count.

        # Get and add vesicle count and image name to array
        vesicle_count = predict_image("", image_path, length_divider=length_divider,
                                      model_weights=model_weights, annotate_rect=annotate_rect,
                                      annotate_ellipse=annotate_ellipse, out_directory=out_directory)
        vesicle_array.append([image_name,vesicle_count])
    # Finally, return full array
    return vesicle_array


def predict_image(weights_path: str, image_path: str, out_directory: str = None, num_slices: int = 256,
                  annotate_rect=True, annotate_ellipse=False, length_divider=None, model_weights=None):
    # Count of GUVs in the image
    vesicle_count = 0

    # Essentially checking if we're passing in the length divider.
    if not length_divider:
        # Check if num_slices can be math.sqrt'ed by comparing to length_divider
        length_divider = math.isqrt(num_slices)
        if num_slices != length_divider ** 2:
            print(f"Note that the present input for num_slices ({num_slices}) is not a perfect square;"
                  f"thus, there will instead be {length_divider ** 2} slices. I'd recommend not messing with this"
                  f"unless you have a good idea of what you're doing.")

    # If annotating ellipse or rectangle and no out_directory was set, note and set out_directory to something
    if (annotate_ellipse or annotate_rect) and not out_directory:
        print("It seems that, though you're annotating, no out_directory was set. That's fine! Just note that "
              "a new folder, with the name 'VesicleYOLO_annotations' will be created to store the images.")
        out_directory = "VesicleYOLO_annotations"

    # Do the same thing for model weights. If we're not passing in model_weights, recalculate them.
    if not model_weights:
        assert weights_path[-3:] == ".pt", f"weights_path must be a .pt file. Currently: {weights_path}"
        model_weights = YOLO(weights_path)

    # Read image in grayscale, get three_channel and shape
    grayscale_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    three_channel_grayscale_image = cv2.cvtColor(grayscale_image, cv2.COLOR_GRAY2BGR)
    image_height, image_width = grayscale_image.shape[:2]

    # Get canvases if we need to (note this just converts bgr -> gray -> bgr, so we can draw with color on gray.)
    if annotate_rect:
        canvas_rect = three_channel_grayscale_image.copy()
    if annotate_ellipse:
        canvas_ellipse = three_channel_grayscale_image.copy()

    # Cut width and height by divider
    cut_width, cut_height = image_width // length_divider, image_height // length_divider

    # Iterate through all slices
    for x_coordinate in tqdm(range(length_divider)):
        for y_coordinate in range(length_divider):

            # Get image, YOLO results
            sliced_image = three_channel_grayscale_image[
                           cut_height * y_coordinate:cut_height * (y_coordinate + 1),
                           cut_width * x_coordinate:cut_width * (x_coordinate + 1)]
            slice_results = model_weights(sliced_image, verbose=False)

            # Iterate through result boxes and use this to count (and draw) the GUVs in any particular image.
            for result in slice_results:
                result_boxes = result.boxes
                for box in result_boxes:

                    # Get coordinates based on what we need (annotating rectangle, etc.)
                    if annotate_rect:
                        top_left_x, top_left_y, bottom_left_x, bottom_left_y = box.xyxy[0]
                        cv2.rectangle(canvas_rect, ((int(top_left_x) + (cut_width * x_coordinate)),
                                                    int(top_left_y) + (cut_height * y_coordinate)),
                                      (int(bottom_left_x) + (cut_width * x_coordinate),
                                       int(bottom_left_y) + (cut_height * y_coordinate)), (0, 0, 255), 1)
                    if annotate_ellipse:
                        center_x, center_y, box_width, box_height = box.xywh[0]
                        cv2.ellipse(canvas_ellipse, (int(center_x + (cut_width * x_coordinate)),
                                                     int(center_y + (cut_height * y_coordinate))),
                                    (int(max(box_width, box_height) / 2),
                                     int(min(box_width, box_height) // 2)), angle=0, startAngle=0, endAngle=360,
                                    color=(0, 0, 255))

                    # extremely high tech vesicle counting technology
                    vesicle_count += 1

    # Make the file structure if it doesn't already exist
    if annotate_ellipse:
        ellipse_directory = os.path.join(out_directory,"ellipse annotations")
        if not os.path.isdir(ellipse_directory):
            os.mkdir(ellipse_directory)
    if annotate_rect:
        rect_directory = os.path.join(out_directory,"rectangle annotations")
        if not os.path.isdir(rect_directory):
            os.mkdir(rect_directory)

    # Get image name so I can save it with this name, then write to folder
    if annotate_rect:
        rect_canvas_base = "rect" + os.path.basename(image_path)
        rect_canvas_path = os.path.join(rect_directory, rect_canvas_base)
        cv2.imwrite(rect_canvas_path, canvas_rect)
    if annotate_ellipse:
        ellipse_canvas_base = "ellipse" + os.path.basename(image_path)
        ellipse_canvas_path = os.path.join(ellipse_directory, ellipse_canvas_base)
        cv2.imwrite(ellipse_canvas_path, canvas_ellipse)

    # Finally, return the vesicle count
    return vesicle_count

