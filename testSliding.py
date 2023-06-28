"""

this file take a Dataset and create images where annotation is not Present
Supported Annotation
- Yolov5
"""
import os
import cv2
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union
import numpy as np


class SlidingImages:
    """
        Class to generate Defect Free Images from one Image with High Resolution.
        The idea is to use a sliding windows over all the High Resolution Image and computer IOU between 
        Defect BBox and Sliding bbox

        IF IOU ==0 means that the sliding window does not include any defect and we save the images

        How Images are saved:
        img_001.jpg HIGH RESOLUTION -> img_001/img_001_1.jpg
                                       img_001/img_001_2.jpg

        One folder with the image name and the all the free defect images with provided resolution. For each free defect
        we save it with the path save_path/image_name/image_name_{index}.jpg                                

        root: Root path of Dataset
        save_path: Where the images are saved
        sliding_dim: Dimension of the sliding Window
        iou_threshold: iou_threshold to save images. Value is between [0,1] 
        
    """

    def __init__(self,
                 root: str,
                 save_path: str,
                 sliding_dim: tuple,
                 iou_threshold=0.001
                 ):

        self.images_path = [os.path.join(
            root, "Images", path) for path in os.listdir(root + "Images/")]
        self.label_path = [os.path.join(root, "Labels", path)
                           for path in os.listdir(root + "Labels/")]

        self.create_folder(save_path)
        print(self.images_path[0])
        self.save_path = save_path
        self.sliding_dim = sliding_dim
        self.iou_threshold= iou_threshold
        
    def create_folder(self, folder_path):
        print(f"FOLDER CREATED IN {folder_path}")
        Path(folder_path).mkdir(
            parents=True, exist_ok=True)

    def get_full_path_without_ext(self,
                                  path: str) -> str:

        return os.path.splitext(path)[0]

    def calc_ratio_and_slice(self,
                             orientation,
                             slide=1,
                             ratio=0.1):
        """
        According to image resolution calculation overlap params
        Args:
            orientation: image capture angle
            slide: sliding window
            ratio: buffer value
        Returns:
            overlap params
        """
        if orientation == "vertical":
            slice_row, slice_col, overlap_height_ratio, overlap_width_ratio = slide, slide * 2, ratio, ratio
        elif orientation == "horizontal":
            slice_row, slice_col, overlap_height_ratio, overlap_width_ratio = slide * \
                2, slide, ratio, ratio
        elif orientation == "square":
            slice_row, slice_col, overlap_height_ratio, overlap_width_ratio = slide, slide, ratio, ratio

        return slice_row, slice_col, overlap_height_ratio, overlap_width_ratio  # noqa

    def calc_resolution_factor(self,
                               resolution: int) -> int:
        """
        According to image resolution calculate power(2,n) and return the closest smaller `n`.
        Args:
            resolution: the width and height of the image multiplied. such as 1024x720 = 737280
        Returns:
        """
        expo = 0
        while np.power(2, expo) < resolution:
            expo += 1

        return expo - 1

    def calc_aspect_ratio_orientation(self,
                                      width: int,
                                      height: int) -> str:
        """
        Args:
            width:
            height:
        Returns:
            image capture orientation
        """

        if width < height:
            return "vertical"
        elif width > height:
            return "horizontal"
        else:
            return "square"

    def calc_slice_and_overlap_params(self,
                                      resolution: str,
                                      height: int,
                                      width: int,
                                      orientation: str) -> List:
        """
        This function calculate according to image resolution slice and overlap params.
        Args:
            resolution: str
            height: int
            width: int
            orientation: str
        Returns:
            x_overlap, y_overlap, slice_width, slice_height
        """

        if resolution == "medium":
            split_row, split_col, overlap_height_ratio, overlap_width_ratio = self.calc_ratio_and_slice(
                orientation, slide=1, ratio=0.8
            )

        elif resolution == "high":
            split_row, split_col, overlap_height_ratio, overlap_width_ratio = self.calc_ratio_and_slice(
                orientation, slide=2, ratio=0.4
            )

        elif resolution == "ultra-high":
            split_row, split_col, overlap_height_ratio, overlap_width_ratio = self.calc_ratio_and_slice(
                orientation, slide=4, ratio=0.4
            )
        else:  # low condition
            split_col = 1
            split_row = 1
            overlap_width_ratio = 1
            overlap_height_ratio = 1

        slice_height = height // split_col
        slice_width = width // split_row

        x_overlap = int(slice_width * overlap_width_ratio)
        y_overlap = int(slice_height * overlap_height_ratio)

        return x_overlap, y_overlap, slice_width, slice_height  # noqa

    def get_resolution_selector(self,
                                res: str,
                                height: int,
                                width: int):
        """
        Args:
            res: resolution of image such as low, medium
            height:
            width:
        Returns:
            trigger slicing params function and return overlap params
        """
        orientation = self.calc_aspect_ratio_orientation(
            width=width, height=height)
        x_overlap, y_overlap, slice_width, slice_height = self.calc_slice_and_overlap_params(
            resolution=res, height=height, width=width, orientation=orientation
        )

        return x_overlap, y_overlap, slice_width, slice_height

    def get_auto_slice_params(self,
                              height: int,
                              width: int):
        """
        According to Image HxW calculate overlap sliding window and buffer params
        factor is the power value of 2 closest to the image resolution.
            factor <= 18: low resolution image such as 300x300, 640x640
            18 < factor <= 21: medium resolution image such as 1024x1024, 1336x960
            21 < factor <= 24: high resolution image such as 2048x2048, 2048x4096, 4096x4096
            factor > 24: ultra-high resolution image such as 6380x6380, 4096x8192
        Args:
            height:
            width:
        Returns:
            slicing overlap params x_overlap, y_overlap, slice_width, slice_height
        """
        resolution = height * width
        factor = self.calc_resolution_factor(resolution)
        if factor <= 18:
            return self.get_resolution_selector("low", height=height, width=width)
        elif 18 <= factor < 21:
            return self.get_resolution_selector("medium", height=height, width=width)
        elif 21 <= factor < 24:
            return self.get_resolution_selector("high", height=height, width=width)
        else:
            return self.get_resolution_selector("ultra-high", height=height, width=width)

    def get_slice_bboxes(
            self,
            image_height: int,
            image_width: int,
            slice_height: int = None,
            slice_width: int = None,
            auto_slice_resolution: bool = True,
            overlap_height_ratio: float = 0.2,
            overlap_width_ratio: float = 0.2,) -> List[List[int]]:
        """Slices `image_pil` in crops.
        Corner values of each slice will be generated using the `slice_height`,
        `slice_width`, `overlap_height_ratio` and `overlap_width_ratio` arguments.
        Args:
            image_height (int): Height of the original image.
            image_width (int): Width of the original image.
            slice_height (int): Height of each slice. Default 512.
            slice_width (int): Width of each slice. Default 512.
            overlap_height_ratio(float): Fractional overlap in height of each
                slice (e.g. an overlap of 0.2 for a slice of size 100 yields an
                overlap of 20 pixels). Default 0.2.
            overlap_width_ratio(float): Fractional overlap in width of each
                slice (e.g. an overlap of 0.2 for a slice of size 100 yields an
                overlap of 20 pixels). Default 0.2.
            auto_slice_resolution (bool): if not set slice parameters such as slice_height and slice_width,
                it enables automatically calculate these params from image resolution and orientation.
        Returns:
            List[List[int]]: List of 4 corner coordinates for each N slices.
                [
                    [slice_0_left, slice_0_top, slice_0_right, slice_0_bottom],
                    ...
                    [slice_N_left, slice_N_top, slice_N_right, slice_N_bottom]
                ]
        """

        slice_bboxes = []
        y_max = y_min = 0

        if slice_height and slice_width:
            y_overlap = int(overlap_height_ratio * slice_height)
            x_overlap = int(overlap_width_ratio * slice_width)
        elif auto_slice_resolution:
            # x_overlap, y_overlap, slice_width, slice_height = get_auto_slice_params(height=image_height, width=image_width)
            pass
        else:
            raise ValueError(
                "Compute type is not auto and slice width and height are not provided.")
        while y_max < image_height:
            x_min = x_max = 0
            y_max = y_min + slice_height
            while x_max < image_width:
                x_max = x_min + slice_width
                if y_max > image_height or x_max > image_width:
                    xmax = min(image_width, x_max)
                    ymax = min(image_height, y_max)
                    xmin = max(0, xmax - slice_width)
                    ymin = max(0, ymax - slice_height)
                    slice_bboxes.append([xmin, ymin, xmax, ymax])
                else:
                    slice_bboxes.append([x_min, y_min, x_max, y_max])
                x_min = x_max - x_overlap
            y_min = y_max - y_overlap
        return slice_bboxes

    def bb_intersection_over_union(self, boxA, boxB):
        # determine the (x, y)-coordinates of the intersection rectangle
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        # compute the area of intersection rectangle
        interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
        if interArea == 0:
            return 0
        # compute the area of both the prediction and ground-truth
        # rectangles
        boxAArea = abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
        boxBArea = abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the interesection area
        iou = interArea / float(boxAArea + boxBArea - interArea)

        # return the intersection over union value
        return iou

    def create_images(self):

        for image_path, label_path in zip(self.images_path, self.label_path):

            img = cv2.imread(image_path)
            extension = Path(image_path).suffix
            image_name_without_ext = Path(image_path).stem

            save_path_with_image_name = os.path.join(
                self.save_path, image_name_without_ext)

            # folder with image name
            self.create_folder(self.get_full_path_without_ext(
                self.save_path + image_name_without_ext))

            height, width, c = img.shape

            slices = self.get_slice_bboxes(
                height, width, slice_height=self.sliding_dim[1], slice_width=self.sliding_dim[0])

            with open(label_path) as f:
                lines = f.readlines()

                # index to keep track of each sliding windows crop for single image
                single_image_index = 0
                img_clone = img.copy()
                
                #Get all defect and IOU for a single Images

                # cycle over each sliding bbox
                for slice in slices:
                    iou_array=[]
                    
                    for line in lines:
                        array = line.replace("\n", "").split(" ")[1:]
                        array = [float(x)*width if i % 2 == 0 else float(x)
                                    * height for i, x in enumerate(array)]

                        array = [int(x) for x in array]

                        start_point = (array[0], array[1])
                        end_point = (array[0]+array[2], array[1]+array[3])
                        

                        bbox_x1x2y1y2 = [
                            start_point[0], start_point[1], end_point[0], end_point[1]]

                        iou = self.bb_intersection_over_union(
                            slice, bbox_x1x2y1y2)
                        iou_array.append(iou)
                        # cv2.rectangle(img_clone, start_point,
                        #                 end_point, (0, 255, 0), 2)
                        
                    #Save image only if Sliding windows do not intersect any defect
                    if (all(x < self.iou_threshold for x in iou_array)):
                        # cv2.rectangle(
                        # img_clone, (slice[0], slice[1]), (slice[2], slice[3]), (0, 0, 255), 2)
                        
                        cropped_image= img_clone[slice[1]:slice[3],slice[0]:slice[2]]
                        
                        saved_out_path = os.path.join(
                            save_path_with_image_name, image_name_without_ext + "_"+ str(single_image_index) + extension)
                        single_image_index= single_image_index + 1
                        
                        print(f"save path {saved_out_path}")
                        #cv2.imwrite(saved_out_path, img_clone)
                        cv2.imwrite(saved_out_path, cropped_image)

if __name__ == "__main__":

    slideImage = SlidingImages("/home/Develop/ai4prod_python/DatasetTmp/",
                               "/home/Develop/ai4prod_python/DatasetTmp/saved_images/", (256, 256),0.02)

    slideImage.create_images()