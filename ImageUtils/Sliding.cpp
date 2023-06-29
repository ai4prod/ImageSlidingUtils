#include "Sliding.h"

namespace ImageUtils
{

    Sliding::Sliding()
    {
    }

    Sliding::~Sliding()
    {
    }

    void Sliding::create_folder(const std::string &folder_path)
    {

        std::cout << "FOLDER CREATED IN " << folder_path << std::endl;
        std::filesystem::create_directories(folder_path);
    }

    /**
     * @brief 
     * 
     * @param slice_bboxes Vector of vector of slice bboxes 
     * @param image_height Image Height of original image
     * @param image_width Image Width of original image
     * @param slice_height Heigh of bbox
     * @param slice_width Width of bbox
     * @param auto_slice_resolution  
     * @param overlap_height_ratio Intersection ratio
     * @param overlap_width_ratio 
     */
    void Sliding::get_slice_bboxes(
        std::vector<std::vector<int>> &slice_bboxes,
        int image_width,
        int image_height,
        int slice_width,
        int slice_height,
        float overlap_width_ratio,
        float overlap_height_ratio,
        bool auto_slice_resolution)
    {

        int y_max = 0, y_min = 0;

        int y_overlap, x_overlap;

        if (slice_height != 0 && slice_width != 0)
        {
            y_overlap = static_cast<int>(overlap_height_ratio * slice_height);
            x_overlap = static_cast<int>(overlap_width_ratio * slice_width);
        }
        else if (auto_slice_resolution)
        {
            // Calculate slice parameters automatically based on image resolution and orientation.
            // int x_overlap, y_overlap, slice_width, slice_height;
            // get_auto_slice_params(image_height, image_width, x_overlap, y_overlap, slice_width, slice_height);
            // Implement the logic to calculate the slice parameters based on your requirements.
            // Uncomment the above lines and replace the function call with the appropriate logic.
        }
        else
        {
            throw std::invalid_argument("Compute type is not auto and slice width and height are not provided.");
        }

        while (y_max < image_height)
        {
            int x_min = 0, x_max = 0;
            y_max = y_min + slice_height;
            while (x_max < image_width)
            {
                x_max = x_min + slice_width;
                if (y_max > image_height || x_max > image_width)
                {
                    int xmax = std::min(image_width, x_max);
                    int ymax = std::min(image_height, y_max);
                    int xmin = std::max(0, xmax - slice_width);
                    int ymin = std::max(0, ymax - slice_height);
                    slice_bboxes.push_back({xmin, ymin, xmax, ymax});
                }
                else
                {
                    slice_bboxes.push_back({x_min, y_min, x_max, y_max});
                }
                x_min = x_max - x_overlap;
            }
            y_min = y_max - y_overlap;
        }
    }

    /**
     * @brief Calculate IOU intersection
     * 
     * @param boxA first Box
     * @param boxB Second Box
     * @return float return IOU value between [0,1]
     */
    float Sliding::bb_intersection_over_union(const std::vector<int> &boxA, const std::vector<int> &boxB)
    {

        float xA = std::max(boxA[0], boxB[0]);
        float yA = std::max(boxA[1], boxB[1]);
        float xB = std::min(boxA[2], boxB[2]);
        float yB = std::min(boxA[3], boxB[3]);

        // compute the area of intersection rectangle
        float interArea = std::max(0.0f, xB - xA) * std::max(0.0f, yB - yA);
        if (interArea == 0)
        {
            return 0;
        }

        // compute the area of both the prediction and ground-truth rectangles
        float boxAArea = std::abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]));
        float boxBArea = std::abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]));

        // compute the intersection over union by taking the intersection area
        // and dividing it by the sum of prediction + ground-truth areas - the intersection area
        float iou = interArea / (boxAArea + boxBArea - interArea);

        // return the intersection over union value
        return iou;
    }

/**
 * @brief Creates the batch of images
 *
 * @param origMat The original image
 * @param batch_vectors Vector containing the images divided into batches
 * @param sliding_W Width of the sliding box
 * @param sliding_H Height of the sliding box
 * @param overlap_W Horizontal overlap between sliding boxes
 * @param overlap_H Vertical overlap between sliding boxes
 * @param batch_size Number of images in each batch
 */
    void Sliding::create_images(cv::Mat origMat, std::vector<std::vector<cv::Mat>> &batch_vectors, int sliding_W, int sliding_H, float overlap_W, float overlap_H, int batch_size)
    {
        
        int height = origMat.rows;
        int width = origMat.cols;
        std::vector<std::vector<int>> slices;

        get_slice_bboxes(slices, height, width, sliding_W, sliding_H, overlap_W, overlap_H,false);
        
        //reserve vector space in order to not double the dimension
        batch_vectors.reserve((int)(slices.size()/batch_size)+1);

        std::vector<cv::Mat> tmp_batches;
        tmp_batches.reserve(batch_size);
        
        for (size_t counter = 0; counter < slices.size(); counter++)
        {
            
            std::cout << slices[counter][1]<<" "<< slices[counter][3] <<" "<< slices[counter][0]<<" "<< slices[counter][2]<< std::endl;
            cv::Mat cropped_image = origMat(cv::Range(slices[counter][0], slices[counter][2]), cv::Range(slices[counter][1], slices[counter][3]));

            cv::imshow("image", cropped_image);
            cv::waitKey(0);
           

            tmp_batches.push_back(cropped_image);

            if (tmp_batches.size() == batch_size)
            {
                //push_back vetor_batch
                batch_vectors.push_back(tmp_batches);

                tmp_batches.clear();
                tmp_batches.reserve(batch_size);
            }
        }
        
        //save last vector even if is not multiple of batch_size
        batch_vectors.push_back(tmp_batches);
    }

}