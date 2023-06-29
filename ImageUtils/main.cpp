#include "Sliding.h"

using namespace ImageUtils;

int main(){

    Sliding sliding;
    
    int image_height = 1024;
    int image_width = 1024;
    std::vector<std::vector<int>> bboxes;
    cv::Mat origImage= cv::imread("../image_sliding.jpeg");
    std::vector<std::vector<cv::Mat>> batch_vectors;

    sliding.create_images(origImage, batch_vectors, 512, 512, 0.2, 0.2, 8);
    std::cout << batch_vectors.size()<< std::endl;


    return 0;

}