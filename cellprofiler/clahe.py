# coding=utf-8

#################################
#
# Imports from useful Python libraries
#
#################################

import numpy
import scipy.ndimage
from skimage.exposure import equalize_adapthist

import cellprofiler.image
import cellprofiler.module
import cellprofiler.setting

__doc__ = """\
CLAHE
=============
**CLAHE** runs Contrast Limited Adaptive Histogram Equalization
(CLAHE) on the image.
|
============ ============ ===============
Supports 2D? Supports 3D? Respects masks?
============ ============ ===============
YES          NO           YES
============ ============ ===============
See also
^^^^^^^^
ImageMath
What do I need as input?
^^^^^^^^^^^^^^^^^^^^^^^^
Image.
What do I get as output?
^^^^^^^^^^^^^^^^^^^^^^^^
Outputs an image with localized contrast adjustments from CLAHE.
Technical notes
^^^^^^^^^^^^^^^
Implemented using SciKit-Image 
(`link <https://scikit-image.org/docs/dev/api/skimage.exposure.html?highlight=clahe#skimage.exposure.equalize_adapthist>`__)
References
^^^^^^^^^^
Put CLAHE citation here
"""

#
# Constants
#
# It's good programming practice to replace things like strings with
# constants if they will appear more than once in your program. That way,
# if someone wants to change the text, that text will change everywhere.
# Also, you can't misspell it by accident.
#
KERNEL_SIZE = "Kernel size"
CLIP_LIMIT  = "Clip limit"
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
class CLAHE(cellprofiler.module.ImageProcessing):
    #
    # The module starts by declaring the name that's used for display,
    # the category under which it is stored and the variable revision
    # number which can be used to provide backwards compatibility if
    # you add user-interface functionality later.
    #
    # This module's category is "Image Processing" which is defined
    # by its superclass.
    #
    module_name = "CLAHE"
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
        super(CLAHE, self).create_settings()

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
**CLAHE** will perform Contrast Limited Adaptive Histogram Equalization (CLAHE) on this image.
"""

        self.kernel_size = cellprofiler.setting.Integer(
            text="Kernel size",
            value=50,  # The default value is 1 - a short-range scale
            minval=0,  # We don't let the user type in really small values
            doc="""\
Defines the size of the square kernel (in pixels) to perform the local contrasting. The kernel's
dimensions are square, with each side being the length defined here.
"""
        )

        self.clip_limit = cellprofiler.setting.Float(
            text="Clip limit",
            value=0.01,
            minval=0.0,
            maxval=1.0,
            doc="""\
Clipping limit, normalized between 0 and 1. Higher values give
more contrast.
"""
        )

        self.nbins = cellprofiler.setting.Integer(
            text="Number of bins",
            value=256,
            minval=0,
            doc="""\
The number of gray bins for the histogram (i.e. the data range)
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
        settings = super(CLAHE, self).settings()

        # Append additional settings here.
        return settings + [
            self.kernel_size,
            self.clip_limit,
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
        visible_settings = super(CLAHE, self).visible_settings()

        # Configure the visibility of additional settings below.
        visible_settings += [
            self.kernel_size,
            self.clip_limit,
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
        self.function = run_clahe
        super(CLAHE, self).run(workspace)

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
def run_clahe(pixels, kernel_size, clip_limit, nbins):
    outimg = equalize_adapthist(pixels, kernel_size=kernel_size, clip_limit=clip_limit, nbins=nbins)
    return outimg
