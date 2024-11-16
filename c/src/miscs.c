//
// Created by NZXT on 16/11/2024.
//

#include "../libs/miscs.h"


int compareSDLColors(SDL_Color color1, SDL_Color color2) {
    return (color1.r == color2.r &&
            color1.g == color2.g &&
            color1.b == color2.b &&
            color1.a == color2.a);
}

SDL_Color defineColor(int r, int g, int b, int a){
    SDL_Color color;

    if ( r>=0&&r<=255 && g>=0&&g<=255 && b>=0&&b<=255 && a>=0&&a<=255 ){
        color.r = r;
        color.g = g;
        color.b = b;
        color.a = a;
    }else{
        color.r = 0;
        color.g = 0;
        color.b = 0;
        color.a = 0;
    }

    return color;
}


int approxPosX(float x) {
    return (x - (int)x > 0.5) ? (int)x + 1 : (int)x;
}

int approxPosY(float y) {
    return (y - (int)y > 0.5) ? (int)y + 1 : (int)y;
}

POS approxPos(float x, float y) {
    POS coord;
    coord.x = approxPosX(x);
    coord.y = approxPosY(y);
    return coord;
}

float float2Rad(float degrees) {
    return degrees * (M_PI / 180.0f);
}
SDL_Color pixelColor(int x, int y){
    return matrix[x][y];
}