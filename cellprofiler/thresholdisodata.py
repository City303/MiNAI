# coding=utf-8

#################################
#
# Imports from useful Python libraries
#
#################################

import numpy as np
import scipy.ndimage
from skimage.filters import threshold_isodata

import cellprofiler.image
import cellprofiler.module
import cellprofiler.setting

__doc__ = """\
ThresholdISODATA
=============
**ThresholdISODATA** performs thresholding on the image
using the ISODATA method.
|
============ ============ ===============
Supports 2D? Supports 3D? Respects masks?
============ ============ ===============
YES          NO           YES
============ ============ ===============
See also
^^^^^^^^
Threshold
What do I need as input?
^^^^^^^^^^^^^^^^^^^^^^^^
Image.
What do I get as output?
^^^^^^^^^^^^^^^^^^^^^^^^
Outputs a thresholded image using the ISODATA method.
Technical notes
^^^^^^^^^^^^^^^
Implemented using SciKit-Image 
(`link <https://scikit-image.org/docs/dev/api/skimage.filters.html#skimage.filters.threshold_isodata>`__)
References
^^^^^^^^^^
- Ridler TW, Calvard S (1978) “Picture thresholding using an iterative selection method.” 
  *IEEE Transactions on Systems, Man and Cybernetics* 8, 630-632.
  (`link <https://doi.org/10.1109/TSMC.1978.4310039>`__)
- Sezgin M, Sankur B (2004)  “Survey over Image Thresholding Techniques and 
  Quantitative Performance Evaluation.” *Journal of Electronic Imaging* 13(1), 146-165.
  (`link <https://doi.org/10.1117/1.1631315>`__)
- ImageJ AutoThreshold code, 
  (`link <http://fiji.sc/wiki/index.php/Auto_Threshold>`__)
"""

#
# Constants
#
# It's good programming practice to replace things like strings with
# constants if they will appear more than once in your program. That way,
# if someone wants to change the text, that text will change everywhere.
# Also, you can't misspell it by accident.
NUM_BINS    = "Number of bins for the histogram"


#
# The module class.
#
# Your module should "inherit" from cellprofiler.module.Module, or a
# subclass of cellprofiler.module.Module. This module inherits from
# cellprofiler.module.ImageProcessing, which is the base class for
# image processing modules. Image processing modules take an image as
# input and output an image.
#
# This module will use the methods from cellprofiler.module.ImageProcessing
# unless you re-implement them. You can let cellprofiler.module.ImageProcessing
# do most of the work and implement only what you need.
#
# Other classes you can inherit from are:
#
# -  cellprofiler.module.ImageSegmentation: modules which take an image
#    as input and output a segmentation (objects) should inherit from this
#    class.
# -  cellprofiler.module.ObjectProcessing: modules which operate on objects
#    should inherit from this class. These are modules that take objects as
#    input and output new objects.
#
class ThresholdISODATA(cellprofiler.module.ImageProcessing):
    #
    # The module starts by declaring the name that's used for display,
    # the category under which it is stored and the variable revision
    # number which can be used to provide backwards compatibility if
    # you add user-interface functionality later.
    #
    # This module's category is "Image Processing" which is defined
    # by its superclass.
    #
    module_name = "ThresholdISODATA"
    variable_revision_number = 1

    #
    # "create_settings" is where you declare the user interface elements
    # (the "settings") which the user will use to customize your module.
    #
    # You can look at other modules and in cellprofiler.settings for
    # settings you can use.
    #
    def create_settings(self):
        #
        # The superclass (cellprofiler.module.ImageProcessing) defines two
        # settings for image input and output:
        #
        # -  x_name: an ImageNameSubscriber which "subscribes" to all
        #    ImageNameProviders in prior modules. Modules before yours will
        #    put images into CellProfiler. The ImageNameSubscriber gives
        #    your user a list of these images which can then be used as inputs
        #    in your module.
        # -  y_name: an ImageNameProvider makes the image available to subsequent
        #    modules.
        super(ThresholdISODATA, self).create_settings()

        #
        # reST help that gets displayed when the user presses the
        # help button to the right of the edit box.
        #
        # The superclass defines some generic help test. You can add
        # module-specific help text by modifying the setting's "doc"
        # string.
        #
        self.x_name.doc = """\
This is the image that the module operates on. You can choose any image
that is made available by a prior module.
**ThresholdISODATA** will perform ISODATA thresholding on this image.
"""

        self.nbins = cellprofiler.setting.Integer(
            text="Number of bins",
            value=256,
            minval=0,
            doc="""\
The number of gray bins for the histogram.
"""
        )


    #
    # The "settings" method tells CellProfiler about the settings you
    # have in your module. CellProfiler uses the list for saving
    # and restoring values for your module when it saves or loads a
    # pipeline file.
    #
    def settings(self):
        #
        # The superclass's "settings" method returns [self.x_name, self.y_name],
        # which are the input and output image settings.
        #
        settings = super(ThresholdISODATA, self).settings()

        # Append additional settings here.
        return settings + [
            self.nbins
        ]

    #
    # "visible_settings" tells CellProfiler which settings should be
    # displayed and in what order.
    #
    # You don't have to implement "visible_settings" - if you delete
    # visible_settings, CellProfiler will use "settings" to pick settings
    # for display.
    #
    def visible_settings(self):
        #
        # The superclass's "visible_settings" method returns [self.x_name,
        # self.y_name], which are the input and output image settings.
        #
        visible_settings = super(ThresholdISODATA, self).visible_settings()

        # Configure the visibility of additional settings below.
        visible_settings += [
            self.nbins
        ]

        return visible_settings


    #
    # CellProfiler calls "run" on each image set in your pipeline.
    #
    def run(self, workspace):
        #
        # The superclass's "run" method handles retreiving the input image
        # and saving the output image. Module-specific behavior is defined
        # by setting "self.function", defined in this module. "self.function"
        # is called after retrieving the input image and before saving
        # the output image.
        #
        # The first argument of "self.function" is always the input image
        # data (as a numpy array). The remaining arguments are the values of
        # the module settings as they are returned from "settings" (excluding
        # "self.y_data", or the output image).
        #
        self.function = run_isodata
        super(ThresholdISODATA, self).run(workspace)

    #
    # "volumetric" indicates whether or not this module supports 3D images.
    # The "gradient_image" function is inherently 2D, and we've noted this
    # in the documentation for the module. Explicitly return False here
    # to indicate that 3D images are not supported.
    #
    def volumetric(self):
        return False

#
# This is the function that gets called during "run" to create the output image.
# The first parameter must be the input image data. The remaining parameters are
# the additional settings defined in "settings", in the order they are returned.
#
# This function must return the output image data (as a numpy array).
#
def run_isodata(pixels, nbins):
    threshold = threshold_isodata(pixels, nbins=nbins)
    outimg    = np.where(pixels >= threshold, 1.0, 0.0)
    return outimg
