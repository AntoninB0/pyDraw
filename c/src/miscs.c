#include "../libs/miscs.h"

SDL_Color hex2rgb(char *hex) {

    SDL_Color a;

    if (hex[0] == '#') {
        hex++; // Ignore le caractère '#'
    }

    size_t len = strlen(hex);

    if (len == 6) { // Format RGB (RRGGBB)
        a.a = 255; // Valeur alpha par défaut (opaque)
        a.r = (int)strtol(hex, NULL, 16) >> 16;            // Les 2 premiers caractères
        a.g = (int)((strtol(hex, NULL, 16) >> 8) & 0xFF);  // Les 2 caractères du milieu
        a.b = (int)(strtol(hex, NULL, 16) & 0xFF);         // Les 2 derniers caractères
    } else if (len == 8) { // Format RGBA (RRGGBBAA)
        a.r = (int)strtol(hex, NULL, 16) >> 24;            // Les 2 premiers caractères
        a.g = (int)((strtol(hex, NULL, 16) >> 16) & 0xFF); // Les 2 caractères suivants
        a.b = (int)((strtol(hex, NULL, 16) >> 8) & 0xFF);  // Les 2 caractères du milieu
        a.a = (int)(strtol(hex, NULL, 16) & 0xFF);         // Les 2 derniers caractères
    } else {
        fprintf(stderr, "Erreur : format hexadécimal invalide\n");
    }

    return a;
}


int compareSDLColors(SDL_Color color1, SDL_Color color2){


    return (color1.r == color2.r &&
            color1.g == color2.g &&
            color1.b == color2.b &&
            color1.a == color2.a);
}

SDL_Color defineColor(char *hexColor){
    SDL_Color color = hex2rgb(hexColor);

    if ( color.r>=0&&color.r<=255 && color.g>=0&&color.g<=255 && color.b>=0&&color.b<=255 && color.a>=0&&color.a<=255 ){
        return color;
    }else{
        color.r = 0;
        color.g = 0;
        color.b = 0;
        color.a = 0;
    }

    
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

