//
// Created by NZXT on 16/11/2024.
//

#ifndef PYDRAW_MISCS_H
#define PYDRAW_MISCS_H

#include "./pyDraw.h"

int compareSDLColors(SDL_Color color1, SDL_Color color2);
SDL_Color defineColor(int r, int g, int b, int a);
int approxPosX(float x);
int approxPosY(float y);
POS approxPos(float x, float y);
float float2Rad(float degrees);
SDL_Color pixelColor(int x, int y);

#endif //PYDRAW_MISCS_H
