#ifndef PYDRAW_FILL_H
#define PYDRAW_FILL_H

#include "./structs.h"
#include "./miscs.h"

void push(Stack *stack, POS pos);
POS pop(Stack *stack);
bool isEmpty(Stack *stack);
void freeStack(Stack *stack);
void fill(int x, int y, SDL_Color color2Change, SDL_Color colorReplace);
void fillColor(int x, int y, char * hex);

#endif //PYDRAW_FILL_H
