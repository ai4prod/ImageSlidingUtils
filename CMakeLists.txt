cmake_minimum_required(VERSION 3.20)
project(testapp)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED)
set (CMAKE_CXX_FLAGS "-lstdc++fs -std=c++17")
find_package(OpenCV 4.6 EXACT REQUIRED PATHS opencv/Release/)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/ImageUtils)

add_executable(testapp main.cpp)

target_link_libraries(testapp ${OpenCV_LIBS} imagesliding)
target_include_directories(testapp PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/ImageUtils)