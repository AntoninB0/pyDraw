//
// Created by Antonin BÔ on 16/11/2024.
//

#ifndef PYDRAW_STRUCTS_H
#define PYDRAW_STRUCTS_H

#include "./consts.h"

typedef struct PEN {
    int size, penDown;
    float x, y, angle;
    SDL_Color color;
} PEN;

typedef struct POS {
    int x, y;
} POS;

typedef struct {
    POS *data;
    int size;
    int capacity;
} Stack;

typedef struct TEMPSDLMATRIX{
    int height,width;
    SDL_Color **matrix;
}TEMPSDLMATRIX;

#endif //PYDRAW_STRUCTS_H
