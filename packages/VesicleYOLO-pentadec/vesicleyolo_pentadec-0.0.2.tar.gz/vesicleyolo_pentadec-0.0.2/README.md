# VesicleYOLO

This is a simple package meant to make the application of YOLO to vesicle quantification as easy as possible.

## Installation

This is really easy. An example of the code is shown below.

`
pip install VesicleYOLO-pentadec
`


### Example

```
from VesicleYOLO_pentadec.analyze import predict_folder

# A list of vesicles from the folder 'example_folder', with annotations passed into 'package_out'. 
vesicle_list = predict_folder("weights.pt",
                              r"example_folder",
                              "package_out")
```


Keep in mind
`predict_folder` is for batch image processing and will return a list of image names alongside vesicle counts. 
`predict_image` is for singular images and will return a count only.

### Notes on Parameters - what you can do with VesicleYOLO

**`predict_folder` takes the following inputs:**

`weights_path`: Currently required, the path to the model weights. In the future (tomorrow), I'm going to implement default weights.

`images_directory`: Required, the path to the images to be analyzed.

`out_directory`: Not required. Where annotations will be written; if annotations are chosen but no out_directory is set, a new directory is written. This is pretty easy but I haven't checked if it works yet haha. 

`num_slices`: Not required, default is 256. Number of slices to cut the images into. Probably don't mess with this.

`annotate_rect`: Whether to draw rectangular 'bounding box' annotations in the out directory. Default is True.

`annotate_ellipse`: Whether to draw elliptical annotations in the out directory. Default is False.


**`predict_image` takes the same inputs except for these things which you should leave blank:**

`length_divider`: Amount to divide each length (height and width) by. I can't think of a conceivable reason why you would change this.

`model_weights`: Also not really something you should change takes the model weights from `predict_folder`. 