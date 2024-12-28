#ifndef PYDRAW_PEN_H
#define PYDRAW_PEN_H

#include "./pyDraw.h"

PEN initPen();
PEN goTo(int x, int y, PEN pen);
PEN lineWrite(int length, PEN pen);
PEN createPen(int x,int y);
#endif //PYDRAW_PEN_H
