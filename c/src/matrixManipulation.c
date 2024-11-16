//
// Created by NZXT on 16/11/2024.
//

#include "../libs/matrixManipulation.h"


void initMatrix() {
    matrix = malloc(sizeof(SDL_Color*) * WIDTH);
    if (matrix == NULL) exit(1);

    for (int i = 0; i < WIDTH; i++) {
        matrix[i] = malloc(sizeof(SDL_Color) * HEIGHT);
        if (matrix[i] == NULL) exit(1);

        for (int e = 0; e < HEIGHT; e++) {
            matrix[i][e].r = DEFAULTCOLOR_BG_R;
            matrix[i][e].g = DEFAULTCOLOR_BG_G;
            matrix[i][e].b = DEFAULTCOLOR_BG_B;
            matrix[i][e].a = DEFAULTCOLOR_BG_A;
        }
    }
}


void clearMatrix(SDL_Color color) {
    for (int i = 0; i < WIDTH; i++) {
        for (int e = 0; e < HEIGHT; e++) {
            matrix[i][e].r = color.r;
            matrix[i][e].g = color.g;
            matrix[i][e].b = color.b;
            matrix[i][e].a = color.a;
        }
    }
    renderMatrix();
}