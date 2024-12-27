# Version minimale de CMake requise
cmake_minimum_required(VERSION 3.10)

# Nom du projet
project(MySDLProject C)

# Standard C utilisé
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -g")

# Déclaration des chemins
set(SRC_DIR ${CMAKE_SOURCE_DIR}/src)
set(LIB_DIR ${CMAKE_SOURCE_DIR}/libs)

# Ajouter les fichiers source depuis /src
file(GLOB_RECURSE SRCS ${SRC_DIR}/*.c)

# Création de l'exécutable
add_executable(my_sdl_program ${SRCS})

# Inclure les headers depuis /libs
include_directories(${LIB_DIR})

# Inclusion des bibliothèques SDL2
find_package(SDL2 REQUIRED)

# Ajouter les chemins d'inclusion et lier les bibliothèques
target_include_directories(my_sdl_program PRIVATE ${SDL2_INCLUDE_DIRS})
target_link_libraries(my_sdl_program ${SDL2_LIBRARIES} m)

# Ajout d'un clean run
add_custom_target(clean_run
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_BINARY_DIR}/CMakeFiles
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_BINARY_DIR}/src
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_BINARY_DIR}/libs
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_BINARY_DIR}/my_sdl_program
    COMMENT "Nettoyage complet du répertoire de build"
)