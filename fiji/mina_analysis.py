'''
#@ String  (label="Root directory: ", value="") root_directory
#@ String  (label="Regex: ", value="a^") regex_string
#@ String  (label = "Thresholding Op:", value="otsu", choices={"huang", "ij1", "intermodes", "isoData", "li", "maxEntropy", "maxLikelihood", "mean", "minError", "minimum", "moments", "otsu", "percentile", "renyiEntropy", "rosin", "shanbhag", "triangle", "yen"}) threshold_method
#@ Boolean (label="Use ridge detection (2D only):", value=False) use_ridge_detection
#@ BigInteger (label="High contrast:", value=75, required=False) rd_max
#@ BigInteger (label="Low contrast:", value=5, required=False) rd_min
#@ BigInteger (label="Line width:", value=1, required=False) rd_width
#@ BigInteger (label="Line length:", value=3, required=False) rd_length
#@ String  (label="User comment: ", value="") user_comment
#@ Boolean (label="Verbose:", value=False) verbose
#@ OpService ops

#@output String image_title
#@output String thresholding_op
#@output String use_ridge_detection

#@output String high_contrast
#@output String low_contrast

#@output String line_width
#@output String mitochondrial_footprint
#@output String min_line_length

#@output String punctate_count

#@output String rod_count
#@output String rod_len_mean
#@output String rod_len_med
#@output String rod_len_stdevp

#@output String network_count
#@output String network_branches
#@output String network_branches_mean

#@output String branch_len_mean
#@output String branch_len_med
#@output String branch_len_stdevp

#@output String summed_branch_lens_mean
#@output String summed_branch_lens_med
#@output String summed_branch_lens_stdevp
'''

'''
Everything is returned as a String since that is the only way
(at least as we can recall) that Jython will play nice with
PyImageJ when it comes to returning arrays. This is probably because
the underlying structure of String is an array to begin with.

This looks weird but actually works when the script is run in headless mode.
'''

import os
import re

from math import sqrt
from ij import IJ
from ij import ImagePlus
from ij import WindowManager
from ij.io import LogStream
from ij.gui import ImageRoi
from ij.gui import Overlay
from ij.measure import ResultsTable, Measurements
from ij.plugin import Duplicator
from ij.process import ImageStatistics
from java.io import File

from net.imglib2.img.display.imagej import ImageJFunctions
from net.imglib2.type.numeric.integer import UnsignedByteType

from sc.fiji.analyzeSkeleton import AnalyzeSkeleton_

# from ij3d import Image3DUniverse

from org.scijava.vecmath import Point3f
from org.scijava.vecmath import Color3f

# Helper functions..............................................................
def ridge_detect(imp, rd_max, rd_min, rd_width, rd_length):
    title = imp.getTitle()
    IJ.run(imp, "8-bit", "");
    IJ.run(imp, "Ridge Detection", "line_width=%s high_contrast=%s low_contrast=%s make_binary method_for_overlap_resolution=NONE minimum_line_length=%s maximum=0" % (rd_width, rd_max, rd_min, rd_length))
    IJ.run(imp, "Remove Overlay", "")
    skel = WindowManager.getImage(title + " Detected segments")
    IJ.run(skel, "Skeletonize (2D/3D)", "")
    skel.hide()
    return(skel)

def average(num_list, divide_by=None):
    if divide_by is None:
        return sum(num_list)/len(num_list)
    else:
        return sum(num_list)/divide_by

def median(num_list):
    sorted_list = sorted(num_list)
    length      = len(num_list)
    index = (length - 1) // 2

    if (length % 2):
        return sorted_list[index]
    else:
        return (sorted_list[index] + sorted_list[index + 1])/2.0

def pstdev(num_list):
    var = 0 # Variance
    avg = average(num_list)
    for num in num_list:
        var = var + (num - avg)**2
    var = var / len(num_list)
    return sqrt(var)

def batch_load(root_dir, regex_str):
    rgx    = re.compile(regex_str)
    image_paths = []
    images      = []

    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if rgx.match(file):
                image_paths.append(os.path.join(root_dir, subdir, file))

    image_paths = set(image_paths)
    
    for ipath in image_paths:
        imp = IJ.openImage(ipath)
        if imp:
            images.append(imp)

    return images

# The run function..............................................................
def run():

    # outputs = {"image title" : "",
    # "thresholding op" : float,
    # "use ridge detection" : bool,
    # "high contrast" : int,
    # "low contrast" : int,
    # "line width" : int,
    # "minimum line length" : int,
    # "mitochondrial footprint" : float,
    # "branch length mean" : float,
    # "branch length median" : float,
    # "branch length stdevp" : float,
    # "summed branch lengths mean" : float,
    # "summed branch lengths median" : float,
    # "summed branch lengths stdevp" : float,
    # "network branches mean" : float,
    # "network branches median" : float,
    # "network branches stdevp" : float}
    outputs = {}

    output_order = [
        'image_title',
        'thresholding_op',
        'use_ridge_detection',
        'high_contrast',
        'low_contrast',
        'line_width',
        'min_line_length',
        'mitochondrial_footprint',
        'punctate_count',
        'rod_count',
        'network_count',
        'rod_len_mean',
        'rod_len_med',
        'rod_len_stdevp',
        'network_branches',
        'network_branches_mean',
        'branch_len_mean',
        'branch_len_med',
        'branch_len_stdevp',
        'summed_branch_lens_mean',
        'summed_branch_lens_med',
        'summed_branch_lens_stdevp',
    ]

    # TODO remove when you get globals working
    # root_directory = '/home/mitocab/Documents/Box-05282020'
    # regex_string   = '.*_cp_skel_[0-9]*.*'
    imps = batch_load(root_directory, regex_string)

    for o in output_order:
        outputs[o] = []
   
    for imp in imps:
        # Reserve spots for the next image's output data
        for k, _ in outputs.items():
            outputs[k].append(None)

        # Store all of the analysis parameters in the table
        outputs["thresholding_op"][-1]     = threshold_method
        outputs["use_ridge_detection"][-1] = str(use_ridge_detection)
        outputs["high_contrast"][-1]       = rd_max
        outputs["low_contrast"][-1]        = rd_min
        outputs["line_width"][-1]          = rd_width
        outputs["min_line_length"][-1]     = rd_length


        # Create and ImgPlus copy of the ImagePlus for thresholding with ops...
        if verbose:
            IJ.log("Determining threshold level...")

        imp_title = imp.getTitle()
        slices = imp.getNSlices()
        frames = imp.getNFrames()
        outputs["image_title"][-1] = imp_title
        imp_calibration = imp.getCalibration()
        imp_channel = Duplicator().run(imp, imp.getChannel(), imp.getChannel(), 1, slices, 1, frames)
        img = ImageJFunctions.wrap(imp_channel)

        # Determine the threshold value if not manual...
        binary_img = ops.run("threshold.%s"%threshold_method, img)
        binary = ImageJFunctions.wrap(binary_img, 'binary')
        binary.setCalibration(imp_calibration)
        binary.setDimensions(1, slices, 1)

        # Get the total area (i.e. footprint)
        if binary.getNSlices() == 1:
            area = binary.getStatistics(Measurements.AREA).area
            area_fraction = binary.getStatistics(Measurements.AREA_FRACTION).areaFraction
            outputs["mitochondrial_footprint"][-1] =  area * area_fraction / 100.0
        else:
            mito_footprint = 0.0
            for slice in range(binary.getNSlices()):
                    binary.setSliceWithoutUpdate(slice)
                    area = binary.getStatistics(Measurements.AREA).area
                    area_fraction = binary.getStatistics(Measurements.AREA_FRACTION).areaFraction
                    mito_footprint += area * area_fraction / 100.0
            outputs["mitochondrial_footprint"][-1] = mito_footprint * imp_calibration.pixelDepth

        # Generate skeleton from masked binary ...
        # Generate ridges first if using Ridge Detection
        if use_ridge_detection and (imp.getNSlices() == 1):
            skeleton = ridge_detect(imp, rd_max, rd_min, rd_width, rd_length)
        else:
            skeleton = Duplicator().run(binary)
            IJ.run(skeleton, "Skeletonize (2D/3D)", "")

        # Analyze the skeleton...
        if verbose:
            IJ.log("Setting up skeleton analysis...")
        skel = AnalyzeSkeleton_()
        skel.setup("", skeleton)
        if verbose:
            IJ.log("Analyzing skeleton...")
        skel_result = skel.run() # Results from Analyze Skeleton
                                # (SkeletonResults object) 
                                # https://javadoc.scijava.org/Fiji/sc/fiji/analyzeSkeleton/SkeletonResult.html

        branch_counts   = skel_result.getBranches()
        avg_branch_lens = skel_result.getAverageBranchLength()

        punctates, rods, networks, network_branches = 0, 0, 0, 0
        rod_lens, network_lens = [], [] # TODO track indicies instead of copying vals to new lists

        for i in range(len(branch_counts)):
            if branch_counts[i] == 0:
                punctates += 1
            elif branch_counts[i] == 1:
                rods += 1
                rod_lens.append(avg_branch_lens[i])
            else:
                networks += 1
                network_lens.append(avg_branch_lens[i] * branch_counts[i])
                network_branches += branch_counts[i]

        outputs['punctate_count'][-1] = punctates

        outputs['rod_count'][-1]      = rods
        outputs['rod_len_mean'][-1]   = average(rod_lens) if rods > 0 else 0
        outputs['rod_len_med'][-1]    = median(rod_lens)  if rods > 0 else 0
        outputs['rod_len_stdevp'][-1] = pstdev(rod_lens)  if rods > 0 else 0

        outputs['network_count'][-1]    = networks
        outputs['network_branches'][-1] = network_branches
        outputs['network_branches_mean'][-1] = average(network_lens, network_branches) if network_branches > 0 else 0

        if verbose:
            IJ.log("Computing graph based parameters...")
        branch_lengths = []
        summed_lengths = []
        
        
        graphs = skel_result.getGraph()

        for graph in graphs:
            summed_length = 0.0
            edges = graph.getEdges()
            for edge in edges:
                length = edge.getLength()
                branch_lengths.append(length)
                summed_length += length
            summed_lengths.append(summed_length)



        outputs["branch_len_mean"][-1]   = average(branch_lengths)
        outputs["branch_len_med"][-1]    = median(branch_lengths)
        outputs["branch_len_stdevp"][-1] = pstdev(branch_lengths)

        outputs["summed_branch_lens_mean"][-1]  = average(summed_lengths)
        outputs["summed_branch_lens_med"][-1]    = median(summed_lengths)
        outputs["summed_branch_lens_stdevp"][-1] = pstdev(summed_lengths)

        # Create/append results to a ResultsTable...
        if verbose:
            IJ.log("Display results...")
        if "Mito Morphology" in list(WindowManager.getNonImageTitles()):
            rt = WindowManager.getWindow("Mito Morphology").getTextPanel().getOrCreateResultsTable()
        else:
            rt = ResultsTable()

        
        rt.incrementCounter()
        for key in output_order:
            rt.addValue(key, str(outputs[key][-1]))

        # Add user comments intelligently
        if user_comment != None and user_comment != "":
            if "=" in user_comment:
                comments = user_comment.split(",")
                for comment in comments:
                    rt.addValue(comment.split("=")[0], comment.split("=")[1])
            else:
                rt.addValue("Comment", user_comment)

        # rt.show("Mito Morphology") # Do not show in headless mode

        # Create overlays on the original ImagePlus and display them if 2D...
        if imp.getNSlices() == 1:
            if verbose:
                IJ.log("Generate overlays...")
            IJ.run(skeleton, "Green", "")
            IJ.run(binary, "Magenta", "")

            skeleton_ROI = ImageRoi(0,0,skeleton.getProcessor())
            skeleton_ROI.setZeroTransparent(True)
            skeleton_ROI.setOpacity(1.0)
            binary_ROI = ImageRoi(0,0,binary.getProcessor())
            binary_ROI.setZeroTransparent(True)
            binary_ROI.setOpacity(0.25)

            overlay = Overlay()
            overlay.add(binary_ROI)
            overlay.add(skeleton_ROI)

            imp.setOverlay(overlay)
            imp.updateAndDraw()

        '''
        # Generate a 3D model if a stack
        if imp.getNSlices() > 1:

            univ = Image3DUniverse()
            univ.show()

            pixelWidth = imp_calibration.pixelWidth
            pixelHeight = imp_calibration.pixelHeight
            pixelDepth = imp_calibration.pixelDepth

            # Add end points in yellow
            end_points = skel_result.getListOfEndPoints()
            end_point_list = []
            for p in end_points:
                end_point_list.append(Point3f(p.x * pixelWidth, p.y * pixelHeight, p.z * pixelDepth))
            univ.addIcospheres(end_point_list, Color3f(255.0, 255.0, 0.0), 2, 1*pixelDepth, "endpoints")

            # Add junctions in magenta
            junctions = skel_result.getListOfJunctionVoxels()
            junction_list = []
            for p in junctions:
                junction_list.append(Point3f(p.x * pixelWidth, p.y * pixelHeight, p.z * pixelDepth))
            univ.addIcospheres(junction_list, Color3f(255.0, 0.0, 255.0), 2, 1*pixelDepth, "junctions")

            # Add the lines in green
            graphs = skel_result.getGraph()
            for graph in range(len(graphs)):
                edges = graphs[graph].getEdges()
                for edge in range(len(edges)):
                    branch_points = []
                    for p in edges[edge].getSlabs():
                        branch_points.append(Point3f(p.x * pixelWidth, p.y * pixelHeight, p.z * pixelDepth))
                    univ.addLineMesh(branch_points, Color3f(0.0, 255.0, 0.0), "branch-%s-%s"%(graph, edge), True)

            # Add the surface
            univ.addMesh(binary)
            univ.getContent("binary").setTransparency(0.5)
        '''

        if verbose:
            IJ.log("Done analysis!")

    return outputs

# Run the script...
if (__name__=="__main__") or (__name__=="__builtin__"):
    outputs = run()

    # Assign each of the outputs to a global
    # variable of the same name. 
    # 
    # This will return the variable if it is listed as
    # an output at the top of this document, and the
    # listing follows ImageJ script parameter rules.
    for k, v in outputs.items():
        globals()[k] = v
