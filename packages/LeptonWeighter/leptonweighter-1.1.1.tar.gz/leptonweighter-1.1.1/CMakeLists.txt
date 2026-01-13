cmake_minimum_required(VERSION 3.15)
project(LeptonWeighter LANGUAGES CXX)

# -------------- Dependency discovery ----------------------------------------
include(ExternalProject)
find_package(PkgConfig REQUIRED)
find_package(GSL REQUIRED)
find_package(HDF5 REQUIRED COMPONENTS CXX HL)
find_package(Python REQUIRED COMPONENTS Interpreter)

# Get pybind11 CMake path from Python
execute_process(
    COMMAND ${Python_EXECUTABLE} -m pybind11 --cmakedir
    OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
list(APPEND CMAKE_PREFIX_PATH "${PYBIND11_CMAKE_DIR}")
find_package(pybind11 CONFIG REQUIRED)

# Find photospline via photospline-config (not pkg-config)
find_program(PHOTOSPLINE_CONFIG photospline-config
    HINTS /usr/local/bin /opt/local/bin /opt/homebrew/bin
)
if(NOT PHOTOSPLINE_CONFIG)
    message(FATAL_ERROR "photospline-config not found. Please install photospline.")
endif()
message(STATUS "Found photospline-config: ${PHOTOSPLINE_CONFIG}")

# Get photospline include directory from photospline-config
execute_process(
    COMMAND ${PHOTOSPLINE_CONFIG} --cflags
    OUTPUT_VARIABLE PHOTOSPLINE_CFLAGS
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
# Extract include path (look for -I/path pattern)
string(REGEX MATCH "-I([^ ]+)" _match "${PHOTOSPLINE_CFLAGS}")
if(_match)
    set(PHOTOSPLINE_INCLUDE_DIR "${CMAKE_MATCH_1}")
else()
    set(PHOTOSPLINE_INCLUDE_DIR "/usr/local/include")
endif()

# Optional: nuSQuIDS and SQuIDS (for advanced features)
pkg_check_modules(NUSQUIDS QUIET nusquids)
pkg_check_modules(SQUIDS QUIET squids)

# Optional: nuflux
pkg_check_modules(NUFLUX QUIET nuflux)

# -------------- Extract prefixes from found packages ------------------------

# GSL prefix
list(GET GSL_INCLUDE_DIRS 0 GSL_INCLUDE_DIR)
get_filename_component(GSL_PREFIX "${GSL_INCLUDE_DIR}" DIRECTORY)

# HDF5 prefix
list(GET HDF5_INCLUDE_DIRS 0 HDF5_INCLUDE_DIR)
get_filename_component(HDF5_PREFIX "${HDF5_INCLUDE_DIR}" DIRECTORY)

# Photospline prefix - derive from the config script location
get_filename_component(PHOTOSPLINE_BIN_DIR "${PHOTOSPLINE_CONFIG}" DIRECTORY)
get_filename_component(PHOTOSPLINE_PREFIX "${PHOTOSPLINE_BIN_DIR}" DIRECTORY)

# Directory where configure "make install" will land
set(LW_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/_deps/leptonweighter-install)

# -------------- Get python-config path --------------------------------------

get_filename_component(PYTHON_BIN_DIR ${Python_EXECUTABLE} DIRECTORY)
find_program(PYTHON_CONFIG
    NAMES python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}-config python${Python_VERSION_MAJOR}-config python-config
    HINTS ${PYTHON_BIN_DIR}
    NO_DEFAULT_PATH
)
if(NOT PYTHON_CONFIG)
    find_program(PYTHON_CONFIG
        NAMES python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}-config python${Python_VERSION_MAJOR}-config python-config
    )
endif()
message(STATUS "Using python-config: ${PYTHON_CONFIG}")

# -------------- Build configure command -------------------------------------
# Note: GSL is found by configure via pkg-config, so we don't pass --with-gsl

set(CONFIGURE_ARGS
    --prefix=${LW_INSTALL_PREFIX}
    --with-hdf5=${HDF5_PREFIX}
    --with-photospline-config=${PHOTOSPLINE_CONFIG}
    --with-python-bindings
    --python-bin=${Python_EXECUTABLE}
    --python-module-dir=${LW_INSTALL_PREFIX}/lib
)

# Add optional nuSQuIDS support
# Note: We don't pass --with-squids or --with-nusquids because the configure
# script's manual path doesn't include GSL. By omitting these, configure will
# use pkg-config which properly includes GSL dependencies.
if(NUSQUIDS_FOUND AND SQUIDS_FOUND)
    message(STATUS "nuSQuIDS found via pkg-config - nuSQuIDS features will be enabled")
else()
    message(STATUS "nuSQuIDS not found - building without nuSQuIDS features")
endif()

# Add optional nuflux support
# Note: Like SQuIDS, we let configure find nuflux via pkg-config
if(NUFLUX_FOUND)
    message(STATUS "nuflux found via pkg-config - nuflux features will be enabled")
else()
    message(STATUS "nuflux not found - building without nuflux features")
endif()

# -------------- Build core library via configure + make ---------------------

ExternalProject_Add(leptonweighter_core
    SOURCE_DIR ${CMAKE_SOURCE_DIR}
    CONFIGURE_COMMAND ${CMAKE_SOURCE_DIR}/configure ${CONFIGURE_ARGS}
    BUILD_COMMAND make -j${CMAKE_BUILD_PARALLEL_LEVEL} && make python -j${CMAKE_BUILD_PARALLEL_LEVEL}
    INSTALL_COMMAND make install PREFIX=${LW_INSTALL_PREFIX} && make python-install PREFIX=${LW_INSTALL_PREFIX}
    BUILD_IN_SOURCE 1
)

# -------------- Installation of C++ Library ---------------------------------

# Install C++ headers into the wheel/system prefix
install(DIRECTORY ${LW_INSTALL_PREFIX}/include/
        DESTINATION include)

# Install the compiled C++ library (.a/.so/.dylib) - exclude Python extension
install(DIRECTORY ${LW_INSTALL_PREFIX}/lib/
        DESTINATION lib
        PATTERN "LeptonWeighter.so" EXCLUDE
        PATTERN "*.pyc" EXCLUDE
        PATTERN "__pycache__" EXCLUDE)

# -------------- Installation of Python Library ------------------------------

# 1. Pure-Python __init__.py → LeptonWeighter/
install(
    DIRECTORY ${CMAKE_SOURCE_DIR}/resources/python/LeptonWeighter/
    DESTINATION LeptonWeighter
    FILES_MATCHING PATTERN "*.py"
)

# 2. Compiled extension built by `make python` → LeptonWeighter/
install(FILES ${LW_INSTALL_PREFIX}/lib/LeptonWeighter.so
        DESTINATION LeptonWeighter
        OPTIONAL)

# 3. Copy shared library needed by extension → LeptonWeighter/
file(GLOB LW_DYLIBS "${LW_INSTALL_PREFIX}/lib/libLeptonWeighter*.dylib")
file(GLOB LW_SO_LIBS "${LW_INSTALL_PREFIX}/lib/libLeptonWeighter*.so*")
install(FILES ${LW_DYLIBS} ${LW_SO_LIBS}
        DESTINATION LeptonWeighter
        OPTIONAL)

# -------------- macOS Library Path Fixups -----------------------------------
# For wheel distribution, fix library paths to use @loader_path

if(APPLE)
    install(CODE "
        # Fix the Python extension's references to libLeptonWeighter
        set(LW_SO \"\${CMAKE_INSTALL_PREFIX}/LeptonWeighter/LeptonWeighter.so\")
        if(EXISTS \${LW_SO})
            message(STATUS \"Fixing library paths in LeptonWeighter.so\")

            # Get current install names
            execute_process(
                COMMAND otool -L \${LW_SO}
                OUTPUT_VARIABLE OTOOL_OUTPUT
            )

            # Fix the libLeptonWeighter reference to use @loader_path
            execute_process(
                COMMAND install_name_tool -change
                    libLeptonWeighter.dylib
                    @loader_path/libLeptonWeighter.dylib
                    \${LW_SO}
                ERROR_QUIET
            )

            # Also try versioned library name
            execute_process(
                COMMAND install_name_tool -change
                    libLeptonWeighter.1.dylib
                    @loader_path/libLeptonWeighter.1.dylib
                    \${LW_SO}
                ERROR_QUIET
            )

            # Fix any absolute paths to the build directory
            string(REGEX MATCHALL \"[^\\n]*libLeptonWeighter[^\\n]*\" LW_REFS \"\${OTOOL_OUTPUT}\")
            foreach(REF \${LW_REFS})
                if(REF MATCHES \"(/[^ ]+libLeptonWeighter[^ ]*\\\\.dylib)\")
                    set(OLD_PATH \${CMAKE_MATCH_1})
                    get_filename_component(LIB_NAME \${OLD_PATH} NAME)
                    execute_process(
                        COMMAND install_name_tool -change
                            \${OLD_PATH}
                            @loader_path/\${LIB_NAME}
                            \${LW_SO}
                        ERROR_QUIET
                    )
                endif()
            endforeach()

            # Set the install name id properly
            execute_process(
                COMMAND install_name_tool -id
                    @loader_path/LeptonWeighter.so
                    \${LW_SO}
                ERROR_QUIET
            )
        endif()

        # Fix the libLeptonWeighter.dylib to have a proper id
        file(GLOB LW_DYLIBS \"\${CMAKE_INSTALL_PREFIX}/LeptonWeighter/libLeptonWeighter*.dylib\")
        foreach(DYLIB \${LW_DYLIBS})
            get_filename_component(DYLIB_NAME \${DYLIB} NAME)
            execute_process(
                COMMAND install_name_tool -id
                    @loader_path/\${DYLIB_NAME}
                    \${DYLIB}
                ERROR_QUIET
            )
        endforeach()
    ")
endif()
