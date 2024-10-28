cmake_minimum_required(VERSION 3.26)
project(pyDraw C)

set(CMAKE_C_STANDARD 11)
##
# Définir les répertoires include et lib en fonction de l'architecture
set(SDL2_INCLUDE_DIR C:/libs/SDL2-2.30.7/include)
if (CMAKE_SIZEOF_VOID_P EQUAL 8)
    set(SDL2_LIB_DIR C:/libs/SDL2-2.30.7/lib/x64)
else ()
    set(SDL2_LIB_DIR C:/libs/SDL2-2.30.7/lib/x86)
endif ()

include_directories(${SDL2_INCLUDE_DIR})
link_directories(${SDL2_LIB_DIR})

add_executable(${PROJECT_NAME} main.c)

target_link_libraries(${PROJECT_NAME} SDL2main SDL2)

# Copier automatiquement SDL2.dll dans le répertoire de build
add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${SDL2_LIB_DIR}/SDL2.dll"
        $<TARGET_FILE_DIR:${PROJECT_NAME}>
)
