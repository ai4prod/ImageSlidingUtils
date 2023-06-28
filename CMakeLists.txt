cmake_minimum_required(VERSION 3.20)
project(imagesliding)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED)
set (CMAKE_CXX_FLAGS "-lstdc++fs -std=c++17")
include(GenerateExportHeader)

find_package(OpenCV 4.4 EXACT REQUIRED PATHS opencv/Release/)


add_executable(imagesliding main.cpp Sliding.h Sliding.cpp imagesliding_export.h )

target_link_libraries(imagesliding ${OpenCV_LIBS})
generate_export_header(imagesliding BASE_NAME imagesliding EXPORT_FILE_NAME ${CMAKE_CURRENT_SOURCE_DIR}/imagesliding_export.h)
