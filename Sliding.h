#pragma once
#include "imagesliding_export.h"
#include <iostream>
#include <algorithm>
#include <vector>
#include <filesystem>
#include <opencv2/opencv.hpp>



namespace ImageUtils
{
    class Sliding
    {

    public:
        float bb_intersection_over_union(const std::vector<int>& boxA, const std::vector<int>& boxB);

        void create_folder(const std::string& folder_path);


        void get_slice_bboxes(
        std::vector<std::vector<int>> &slice_bboxes,
        int image_width,
        int image_height,
        int slice_width,
        int slice_height,
        float overlap_width_ratio=0.2,
        float overlap_height_ratio=0.2,
        bool auto_slice_resolution=false);

        void create_images(cv::Mat origMat, std::vector<std::vector<cv::Mat>> &batch_vectors,int sliding_W,int sliding_H,float overlap_W, float overlap_H,int batch_size);

        Sliding();
        virtual ~Sliding();
    };

}