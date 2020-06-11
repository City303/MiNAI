'''
MinaAnalysis
==========================

**MinaAnalysis** uses the pipeline introduced in Valente et. al. (2017) to analyze mitochondria.

============ ============ ===============
Supports 2D? Supports 3D? Respects masks?
============ ============ ===============
YES          NO           NO
============ ============ ===============

Designed for Cellprofiler 3.1.9.
'''

import os
import cellprofiler.image as cpi
import cellprofiler.module as cpm
import cellprofiler.preferences as cpp
import cellprofiler.setting as cps

import numpy as np

class MinaAnalysis(cpm.Module):
    category    = "Advanced"
    module_name = "MinaAnalysis"
    variable_revision_number = 1

    def create_settings(self):
        self.skel_image = cps.ImageNameSubscriber(
            text="Skeletonized image",
            doc = """\
A skeletonized image (generated with **MorphologicalSkeleton**) of a cell that
highlights the mitochondrial segments.
        """)

        self.use_threshold = cps.Binary(
            text="Calculate mitochondrial footprint?",
            value=False,
            doc = """\
If selected, requests a thresholded image from a **Threshold** module
to be used as a second image input, for the purposes of calcuating
the mitochondrial input of an image.
        """)

        self.threshold_image = cps.ImageNameSubscriber(
            text="Threshold image",
            doc = """\
The threshold image that **MinaAnalysis*** will use to
calculate the mitochondrial footprint. Usually, this image is 
generated from a **Threshold** module.
        """)

        self.use_custom_units = cps.Binary(
            text="Use custom units?",
            value = False,
            doc = """\
If set to \"Yes\", sets the output statistics to a certain length/area unit. A ratio
has to be established between the number of pixels and the length of one unit. 
        """)

        self.unit_name = cps.Text(
            text="Unit name",
            value="",
            doc = """\
The name of the unit (i.e. um or micrometers).
        """)

        self.unit_ratio = cps.Float(
            text="Number of pixels per unit",
            value=50.0,
            doc = """\
Enter the number of pixels that correspond to one unit of measurement for the image.
For example, if 1 micrometer is equivalent to 50 pixels in the image, the value entered
in this box would be 50.
        """)

    def settings(self):
        ''' Returns all the settings available so CellProifler can track them. '''
        return [
            self.skel_image,
            self.use_threshold,
            self.threshold_image,
            self.use_custom_units,
            self.unit_name,
            self.unit_ratio
        ]
    
    def visible_settings(self):
        ''' Returns what settings should be displayed and in what order. '''
        visible_settings = [self.skel_image, self.use_threshold]

        if self.use_threshold:
            visible_settings += [self.threshold_image]

        visible_settings += [self.use_custom_units]

        if self.use_custom_units:
            visible_settings += [self.unit_name, self.unit_ratio]

        return visible_settings

    def volumetric(self):
        return False

    def run(self, workspace):
        # Put the measurements made in the measurements object
        measurements = workspace.measurements
        
        # Record some statistics to be displayed later.
        # We format them so that Matplotlib can display them in a table.
        # The first row is a header that tells what the fields are.
        statistics = [[
            "high contrast",
            "low contrast",
            "line width",
            "minimum line length",
            "mitochondrial footprint",
            "branch length mean",
            "branch length median",
            "branch length stdevp",
            "summed branch lengths mean",
            "summed branch lengths median",
            "summed branch lengths stdevp",
            "network branches mean",
            "network branches median",
            "network branches stdevp"
        ]]

        workspace.display_data.statistics = statistics # Put the statistics in the workspace 
                                                       # display data so they can be plotted in MPL

        image_set = workspace.image_set

        skel_name   = self.skel_image.value
        skel_image  = image_set.get_image(skel_name, must_be_grayscale=True)
        skel_pixels = skel_image.pixel_data # 2d numpy array

        # Get the mitochondrial footprint, if a threshold image was provided
        if self.use_threshold:
            thresh_name   = self.threshold_image.value
            thresh_image  = image_set.get_image(thresh_name, must_be_grayscale=True)
            thresh_pixels = thresh_image.pixel_data # 2d numpy array

            # Calculate the mitochondrial footprint
            footprint = np.count_nonzero(thresh_pixels)         # Number of nonzero pixels
            
            if self.use_custom_units:
                footprint /= (self.unit_ratio.value ** 2)
                print('Footprint (units^2):', footprint)
            else:
                print('Footprint (px):', footprint)
            # TODO add footprint to values

        # Analyze the skeleton


        

        

