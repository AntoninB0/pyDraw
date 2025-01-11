#ifndef PYDRAW_PEN_H
#define PYDRAW_PEN_H

#include "./pyDraw.h"

PEN initPen();
PEN goTo(PEN pen,int x, int y);
PEN walk(PEN pen,int length) ;
PEN createPen(int x,int y);
#endif //PYDRAW_PEN_H
