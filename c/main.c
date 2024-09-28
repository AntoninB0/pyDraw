#include <SDL.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define WIDTH 1920
#define HEIGHT 1080

#define DEFAULTCOLOR_BG_R 0
#define DEFAULTCOLOR_BG_G 255
#define DEFAULTCOLOR_BG_B 0
#define DEFAULTCOLOR_BG_A 255

#define DEFAULTCOLOR_PEN_R 255
#define DEFAULTCOLOR_PEN_G 0
#define DEFAULTCOLOR_PEN_B 0
#define DEFAULTCOLOR_PEN_A 255

typedef struct PEN {
    int size, penDown;
    float x, y, angle;
    SDL_Color color;
} PEN;

typedef struct POS {
    int x, y;
} POS;

SDL_Window* window = NULL;
SDL_Renderer* renderer = NULL;
SDL_Color **matrix;

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

void RenderMatrix() {
    for (int i = 0; i < WIDTH; i++) {
        for (int e = 0; e < HEIGHT; e++) {
            SDL_SetRenderDrawColor(renderer, matrix[i][e].r, matrix[i][e].g, matrix[i][e].b, matrix[i][e].a);
            SDL_RenderDrawPoint(renderer, i, e);
        }
    }
    SDL_RenderPresent(renderer);
}

SDL_Window * initSDL() {
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        printf("Erreur d'initialisation de SDL: %s\n", SDL_GetError());
        exit(1);
    }

    window = SDL_CreateWindow("Fenêtre SDL2",
                              SDL_WINDOWPOS_UNDEFINED,
                              SDL_WINDOWPOS_UNDEFINED,
                              WIDTH, HEIGHT,
                              SDL_WINDOW_SHOWN);

    if (!window) {
        printf("Erreur de création de la fenêtre: %s\n", SDL_GetError());
        SDL_Quit();
        exit(1);
    }

    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (!renderer) {
        printf("Erreur de création du renderer: %s\n", SDL_GetError());
        SDL_DestroyWindow(window);
        SDL_Quit();
        exit(1);
    }

    RenderMatrix();
    return window;
}

void closeEventSDL() {
    SDL_Event e;
    int quit = 0;
    while (!quit) {
        while (SDL_PollEvent(&e) != 0) {
            if (e.type == SDL_QUIT) {
                quit = 1;
            }
        }
    }

    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();

    for (int i = 0; i < WIDTH; i++) {
        free(matrix[i]);
    }
    free(matrix);
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

PEN initPen() {
    PEN pen;
    pen.size = 1;
    pen.penDown = 0;
    pen.x = (float)(WIDTH / 2);
    pen.y = (float)(HEIGHT / 2);
    pen.angle = 0;
    pen.color.r = DEFAULTCOLOR_PEN_R;
    pen.color.g = DEFAULTCOLOR_PEN_G;
    pen.color.b = DEFAULTCOLOR_PEN_B;
    pen.color.a = DEFAULTCOLOR_PEN_A;
    return pen;
}

float float2Rad(float degrees) {
    return degrees * (M_PI / 180.0f);
}

PEN lineWrite(int length, PEN pen) {
    for (int i = 0; i < length; i++) {
        float newX = pen.x + cosf(float2Rad(pen.angle));
        float newY = pen.y - sinf(float2Rad(pen.angle));

        int x = approxPosX(newX);
        int y = approxPosY(newY);

        if (x >= 0 && x < WIDTH && y >= 0 && y < HEIGHT) {
            matrix[x][y] = pen.color;
        }

        pen.x = newX;
        pen.y = newY;
    }

    RenderMatrix();
    return pen;
}

int main(int argc, char* argv[]) {
    initMatrix();
    initSDL();

    PEN pen = initPen();

    pen.angle = 50;
    pen = lineWrite(100, pen);
    printf("Position after first line: %f, %f\n", pen.x, pen.y);

    pen.angle += 70;
    pen = lineWrite(100, pen);

    for (int i = 0; i < 10 ; ++i) {
        pen.angle += 70;
        pen = lineWrite(500, pen);
    }

    printf("Position after second line: %f, %f\n", pen.x, pen.y);

    closeEventSDL();
    return 0;
}