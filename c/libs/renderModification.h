#ifndef PYDRAW_RENDERMODIFICATION_H
#define PYDRAW_RENDERMODIFICATION_H

#include "./consts.h"
#include "./miscs.h"

void cirleWrite(int radius, PEN pen);
void rotateArea(int x, int y, int width, int height, float angle);
void copyPaste(int x, int y, int width, int height, int x1, int y1);
void copy(int x, int y, int width, int height);
void paste(int x, int y);
void cut(int x, int y, int width, int height, int x1, int y1);
void translation(int x, int y, int width, int height, int length, float angle, int precision);

#endif //PYDRAW_RENDERMODIFICATION_H
