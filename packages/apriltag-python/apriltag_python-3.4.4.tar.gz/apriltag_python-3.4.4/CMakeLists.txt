foreach(X IN ITEMS apriltag_detect.docstring apriltag_estimate_tag_pose.docstring apriltag_pywrap.c CMakeLists.txt)
    configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/src/${X}
    ${CMAKE_CURRENT_SOURCE_DIR}/src/apriltag/apriltag/${X}
    COPYONLY
)
endforeach()

# Top-level CMakeLists.txt for scikit-build-core
cmake_minimum_required(VERSION 3.16)
project(${SKBUILD_PROJECT_NAME}
        VERSION ${SKBUILD_PROJECT_VERSION}
        DESCRIPTION "Python wrapper for the AprilTag visual fiducial detector"
        LANGUAGES C)

# Set rpath for shared libraries to be found at runtime
if(APPLE)
    set(CMAKE_INSTALL_RPATH "@loader_path")
elseif(UNIX)
    set(CMAKE_INSTALL_RPATH "$ORIGIN")
endif()
set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)


# Find Python and NumPy
find_package(Python3 REQUIRED COMPONENTS Development.Module NumPy)
message(STATUS "Found Python ${Python3_VERSION}")

add_subdirectory(src/apriltag/apriltag)

# Install the Python module
# scikit-build-core will automatically handle installation to the correct location
install(TARGETS apriltag.${Python3_SOABI}
        LIBRARY DESTINATION apriltag
        RUNTIME DESTINATION apriltag)

install(TARGETS apriltag
        LIBRARY DESTINATION apriltag
        RUNTIME DESTINATION apriltag)
