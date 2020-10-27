# -*- coding: utf-8 -*-

"""
SaveCroppedObjects
==================

**SaveCroppedObjects** exports each object as a binary image. Pixels corresponding to an exported object are assigned
the value 255. All other pixels (i.e., background pixels and pixels corresponding to other objects) are assigned the
value 0. The dimensions of each image are the same as the original image.

The filename for an exported image is formatted as "{object name}_{label index}.{image_format}", where *object name*
is the name of the exported objects, *label index* is the integer label of the object exported in the image (starting
from 1).

|

============ ============ ===============
Supports 2D? Supports 3D? Respects masks?
============ ============ ===============
YES          NO           YES
============ ============ ===============

"""

import numpy
import os.path
import skimage.io
import skimage.measure
import time

import cellprofiler.module
import cellprofiler.setting

FN_FROM_IMAGE  = "From image filename"
FN_SEQUENTIAL  = "Sequential numbers"
FN_SINGLE_NAME = "Single name"

SINGLE_NAME_TEXT = "Enter single file name"
SEQUENTIAL_NUMBER_TEXT = "Enter file prefix"

FF_PNG  = "png"
FF_TIFF = "tiff"

PC_WITH_IMAGE = "Same folder as image"

WS_EVERY_CYCLE = "Every cycle"
WS_FIRST_CYCLE = "First cycle"
WS_LAST_CYCLE = "Last cycle"

SAVE_PER_OBJECT = "Images"
SAVE_MASK = "Masks"

class SaveCroppedObjectsPlusPlus(cellprofiler.module.Module):
	module_name = "SaveCroppedObjects++"
	category = "File Processing"
	variable_revision_number = 3

	def create_settings(self):
		self.export_option = cellprofiler.setting.Choice(
			"Do you want to save cropped images or object masks?",
			[
				SAVE_PER_OBJECT,
				SAVE_MASK
			],
			doc="""\
Choose the way you want the per-object crops to be exported.

The choices are:

-  *{SAVE_PER_OBJECT}*: Save a per-object crop from the original image
   based on the object's bounding box.
-  *{SAVE_MASK}*: Export a per-object mask.""".format(
				SAVE_PER_OBJECT=SAVE_PER_OBJECT,
				SAVE_MASK=SAVE_MASK
			)
		)

		# TODO this is a quick hack please fix me
                '''
		self.root_dir = cellprofiler.setting.Text(
			'DO NOT CLICK',
			"DO NOT CLICK",
			doc="""\
DO NOT CLICK			
"""
		)
                '''

		self.objects_name = cellprofiler.setting.ObjectNameSubscriber(
			"Objects",
			doc="Select the objects you want to export as per-object crops."
		)

		self.image_name = cellprofiler.setting.ImageNameSubscriber(
			"Image",
			doc="Select the image to crop"
		)

		self.file_name_method = cellprofiler.setting.Choice(
			"Select method for constructing file names",
			[
				FN_FROM_IMAGE,
                FN_SEQUENTIAL,
                FN_SINGLE_NAME
			],
			FN_FROM_IMAGE,
			doc="""\
Several choices are available for constructing the image file name:

-  *{FN_FROM_IMAGE}:* The filename will be constructed based on the
   original filename of an input image specified in **NamesAndTypes**.
   You will have the opportunity to prefix or append additional text.

   If you have metadata associated with your images, you can append
   text to the image filename using a metadata tag. This is especially
   useful if you want your output given a unique label according to the
   metadata corresponding to an image group. The name of the metadata to
   substitute can be provided for each image for each cycle using the
   **Metadata** module.
-  *{FN_SEQUENTIAL}:* Same as above, but in addition, each filename
   will have a number appended to the end that corresponds to the image
   cycle number (starting at 1).
-  *{FN_SINGLE_NAME}:* A single name will be given to the file. Since
   the filename is fixed, this file will be overwritten with each cycle.
   In this case, you would probably want to save the image on the last
   cycle (see the *Select how often to save* setting). The exception to
   this is to use a metadata tag to provide a unique label, as mentioned
   in the *{FN_FROM_IMAGE}* option.
""".format(**{
				"FN_FROM_IMAGE": FN_FROM_IMAGE,
				"FN_SEQUENTIAL": FN_SEQUENTIAL,
				"FN_SINGLE_NAME": FN_SINGLE_NAME

			})
		)

		self.file_image_name = cellprofiler.setting.FileImageNameSubscriber(
			"Select image name for file prefix",
			cellprofiler.setting.NONE,
			doc="""\
*(Used only when “{FN_FROM_IMAGE}” is selected for constructing the filename)*

Select an image loaded using **NamesAndTypes**. The original filename
will be used as the prefix for the output filename.""".format(**{
				"FN_FROM_IMAGE": FN_FROM_IMAGE
			})
		)

		self.single_file_name = cellprofiler.setting.Text(
			SINGLE_NAME_TEXT,
			"OrigBlue",
			doc="""\
*(Used only when “{FN_SEQUENTIAL}” or “{FN_SINGLE_NAME}” are selected
for constructing the filename)*

Specify the filename text here. If you have metadata associated with
your images, enter the filename text with the metadata tags.

Do not enter the file extension in this setting; it will be appended
automatically.""".format(**{
				"FN_SEQUENTIAL": FN_SEQUENTIAL,
				"FN_SINGLE_NAME": FN_SINGLE_NAME
			})
		)

		self.number_of_digits = cellprofiler.setting.Integer(
			"Number of digits",
			4,
			doc="""\
*(Used only when “{FN_SEQUENTIAL}” is selected for constructing the filename)*

Specify the number of digits to be used for the sequential numbering.
Zeros will be used to left-pad the digits. If the number specified here
is less than that needed to contain the number of image sets, the latter
will override the value entered.""".format(**{
				"FN_SEQUENTIAL": FN_SEQUENTIAL
			})
		)

		self.wants_file_name_suffix = cellprofiler.setting.Binary(
			"Append a suffix to the image file name?",
			False,
			doc="""\
Select "*{YES}*" to add a suffix to the image’s file name. Select "*{NO}*"
to use the image name as-is.
			""".format(**{
				"NO": cellprofiler.setting.NO,
				"YES": cellprofiler.setting.YES
			})
		)

		self.file_name_suffix = cellprofiler.setting.Text(
			"Text to append to the image name",
			"",
			doc="""\
*(Used only when constructing the filename from the image filename)*

Enter the text that should be appended to the filename specified above.
If you have metadata associated with your images, you may use metadata tags.

Do not enter the file extension in this setting; it will be appended
automatically.
""".format(**{})
		)


		self.file_format = cellprofiler.setting.Choice(
			"Saved file format",
			[
				FF_PNG,
				FF_TIFF
			],
			value=FF_TIFF,
			doc="""\
*{FF_PNG}* files do not support 3D. *{FF_TIFF}* files use zlib compression level 6.""".format(**{
				"FF_PNG": FF_PNG,
				"FF_TIFF": FF_TIFF
			})
		)

		self.pathname = SaveImagesDirectoryPath(
			"Output file location",
			self.file_image_name,
			doc="""\
This setting lets you choose the folder for the output files.

An additional option is the following:

-  *Same folder as image*: Place the output file in the same folder that
   the source image is located.

If the subfolder does not exist when the pipeline is run, CellProfiler
will create it.

If you are creating nested subfolders using the sub-folder options, you
can specify the additional folders separated with slashes. For example,
“Outlines/Plate1” will create a “Plate1” folder in the “Outlines”
folder, which in turn is under the Default Input/Output Folder. The use
of a forward slash (“/”) as a folder separator will avoid ambiguity
between the various operating systems.
""".format(**{})
		)
                ##################################################
                ################
                ##################
                ##############
                self.root_dir = self.pathname
		self.create_subdirectories = cellprofiler.setting.Binary(
			"Create subfolders in the output folder?",
			False, doc="""Select "*{YES}*" to create subfolders to match the input image folder structure.""".format(**{
				"YES": cellprofiler.setting.YES
			})
		)

		self.overwrite = cellprofiler.setting.Binary(
			"Overwrite existing files without warning?",
			False,
			doc="""\
Select "*{YES}*" to automatically overwrite a file if it already exists.
Select "*{NO}*" to be prompted for confirmation first.

If you are running the pipeline on a computing cluster, select "*{YES}*"
since you will not be able to intervene and answer the confirmation
prompt.""".format(**{
				"NO": cellprofiler.setting.NO,
				"YES": cellprofiler.setting.YES
			})
		)

	def display(self, workspace, figure):
		figure.set_subplots((1, 1))
		figure.subplot_table(0, 0, [["\n".join(workspace.display_data.filenames)]])

	def get_filename_base(self, workspace, make_dirs=True, check_overwrite=True):
		""" Get a filename base (minus label and file type format) for the current image based on the user settings. """

		measurements = workspace.measurements
		if self.file_name_method == FN_SINGLE_NAME:
			filename = self.single_file_name.value
			filename = workspace.measurements.apply_metadata(filename)
		elif self.file_name_method == FN_SEQUENTIAL:
			filename = self.single_file_name.value
			filename = workspace.measurements.apply_metadata(filename)
			n_image_sets = workspace.measurements.image_set_count
			ndigits = int(numpy.ceil(numpy.log10(n_image_sets + 1)))
			ndigits = max((ndigits, self.number_of_digits.value))
			padded_num_string = str(measurements.image_set_number).zfill(ndigits)
			filename = '%s%s' % (filename, padded_num_string)
		else:
			file_name_feature = self.source_file_name_feature
			filename = measurements.get_current_measurement('Image',
															file_name_feature)
			filename = os.path.splitext(filename)[0]
			if self.wants_file_name_suffix:
				suffix = self.file_name_suffix.value
				suffix = workspace.measurements.apply_metadata(suffix)
				filename += suffix

		pathname = self.pathname.get_absolute_path(measurements)
                print('pathname_old', pathname)
		if self.create_subdirectories:
			image_path = self.source_path(workspace)
                        common_prefix = os.path.commonprefix([pathname, image_path]).rpartition('/')[0]
                        
			subdir = os.path.relpath(image_path, start=common_prefix)
			pathname = os.path.join(pathname, subdir)
                        
                        ########################################
                        ########################################
                        #######################################
                        print('pathname', pathname)
                        print('image_path', image_path)
                        print('common_prefix', common_prefix)
                        print('subdir', subdir)
                        print('join(pathname, subdir)', os.path.join(pathname, subdir))
                        print('filename', filename)
                        print('root_dir.get_abs_path', self.root_dir.get_absolute_path())
		if len(pathname) and not os.path.isdir(pathname) and make_dirs:
			try:
				os.makedirs(pathname)
			except:
				#
				# On cluster, this can fail if the path was created by
				# another process after this process found it did not exist.
				#
				if not os.path.isdir(pathname):
					raise
		result = os.path.join(pathname, filename)
                
		if check_overwrite and not self.check_overwrite(result, workspace):
			return

		if check_overwrite and os.path.isfile(result):
			try:
				os.remove(result)
			except:
				import bioformats
				bioformats.clear_image_reader_cache()
				os.remove(result)
		return result

	def run(self, workspace):
		objects       = workspace.object_set.get_objects(self.objects_name.value)
		labels        = objects.segmented
		unique_labels = numpy.unique(labels)

		if unique_labels[0] == 0:
			unique_labels = unique_labels[1:]

		filenames = []
		filename_base = self.get_filename_base(workspace)
		timestamp = str(int(time.time() * 1000))

		for label in unique_labels:
			if self.export_option == SAVE_MASK:
				mask = labels == label

			elif self.export_option == SAVE_PER_OBJECT:
				mask_in = labels == label
				images = workspace.image_set
				x = images.get_image(self.image_name.value)
				properties = skimage.measure.regionprops(mask_in.astype(int), intensity_image=x.pixel_data)
				mask = properties[0].intensity_image

				print("FILE FORMAT: ", self.file_format)

			if self.file_format.value == FF_PNG:
				filename = filename_base + "_" + str(label) + ".png"
				skimage.io.imsave(filename, skimage.img_as_ubyte(mask))
			elif self.file_format.value == FF_TIFF:
				filename = filename_base + "_" + str(label) + ".tiff"
				skimage.io.imsave(filename, skimage.img_as_ubyte(mask), compress=6)

			filenames.append(filename)

		if self.show_window:
			workspace.display_data.filenames = filenames

	def settings(self):
		settings = [
			self.objects_name,
			self.image_name,
			self.file_name_method,
			self.file_image_name,
			self.file_name_suffix,
			self.single_file_name,
			self.number_of_digits,
			self.wants_file_name_suffix,
			self.file_format,
			self.pathname,
			self.export_option,
			self.overwrite,
			self.create_subdirectories
		]

		return settings

	def visible_settings(self):
		result = [
			self.export_option,
			self.file_name_method,
			self.objects_name,
		]

		if self.export_option.value == SAVE_PER_OBJECT:
			result += [self.image_name]

		if self.file_name_method == FN_FROM_IMAGE:
			result += [self.file_image_name, self.wants_file_name_suffix]
			if self.wants_file_name_suffix:
				result.append(self.file_name_suffix)
		elif self.file_name_method == FN_SEQUENTIAL:
			self.single_file_name.text = SEQUENTIAL_NUMBER_TEXT
			# XXX - Change doc, as well!
			result.append(self.single_file_name)
			result.append(self.number_of_digits)
		elif self.file_name_method == FN_SINGLE_NAME:
			self.single_file_name.text = SINGLE_NAME_TEXT
			result.append(self.single_file_name)
		else:
			raise NotImplementedError("Unhandled file name method: %s" % self.file_name_method)
		result.append(self.file_format)
		result.append(self.pathname)
		result.append(self.overwrite)
		if self.file_name_method == FN_FROM_IMAGE:
			result.append(self.create_subdirectories)
			if self.create_subdirectories:
				result.append(self.root_dir)


		return result

	def volumetric(self):
		return True

	def check_overwrite(self, filename, workspace):
		'''Check to see if it's legal to overwrite a file

		Throws an exception if can't overwrite and no interaction available.
		Returns False if can't overwrite, otherwise True.
		'''
		if not self.overwrite.value and os.path.isfile(filename):
			try:
				return workspace.interaction_request(self, workspace.measurements.image_set_number, filename) == "Yes"
			except workspace.NoInteractionException:
				raise ValueError(
						'SaveImages: trying to overwrite %s in headless mode, but Overwrite files is set to "No"' % (
							filename))
		return True

	def source_path(self, workspace):
		'''The path for the image data, or its first parent with a path'''
		if self.file_name_method.value == FN_FROM_IMAGE:
			path_feature = '%s_%s' % (cellprofiler.measurement.C_PATH_NAME, self.file_image_name.value)
			assert workspace.measurements.has_feature(cellprofiler.measurement.IMAGE, path_feature), \
				"Image %s does not have a path!" % self.file_image_name.value
			return workspace.measurements.get_current_image_measurement(path_feature)

	@property
	def source_file_name_feature(self):
		'''The file name measurement for the exemplar disk image'''
		return '_'.join((cellprofiler.measurement.C_FILE_NAME, self.file_image_name.value))

class SaveImagesDirectoryPath(cellprofiler.setting.DirectoryPath):
	'''A specialized version of DirectoryPath to handle saving in the image dir'''

	def __init__(self, text, file_image_name, doc):
		'''Constructor
		text - explanatory text to display
		file_image_name - the file_image_name setting so we can save in same dir
		doc - documentation for user
		'''
		super(SaveImagesDirectoryPath, self).__init__(
				text, dir_choices=[
					cellprofiler.setting.DEFAULT_OUTPUT_FOLDER_NAME, cellprofiler.setting.DEFAULT_INPUT_FOLDER_NAME,
					PC_WITH_IMAGE, cellprofiler.setting.ABSOLUTE_FOLDER_NAME,
					cellprofiler.setting.DEFAULT_OUTPUT_SUBFOLDER_NAME,
					cellprofiler.setting.DEFAULT_INPUT_SUBFOLDER_NAME], doc=doc)
		self.file_image_name = file_image_name

	def get_absolute_path(self, measurements=None, image_set_index=None):
		if self.dir_choice == PC_WITH_IMAGE:
			path_name_feature = "PathName_%s" % self.file_image_name.value
			return measurements.get_current_image_measurement(path_name_feature)
		return super(SaveImagesDirectoryPath, self).get_absolute_path(
				measurements, image_set_index)

	def test_valid(self, pipeline):
		if self.dir_choice not in self.dir_choices:
			raise cellprofiler.setting.ValidationError("%s is not a valid directory option" %
													   self.dir_choice, self)
