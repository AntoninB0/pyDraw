#include <SDL.h>
#include <stdio.h>
#include <stdlib.h>

#define WIDTH 1920
#define HEIGHT 1080
#define DEFAULTCOLOR_R 0
#define DEFAULTCOLOR_G 255
#define DEFAULTCOLOR_B 0
#define DEFAULTCOLOR_A 255


typedef struct PEN{
    int size,penDown;
    float x,y,angle;
    SDL_Color color;
}PEN;

SDL_Window* window = NULL;
SDL_Renderer* renderer = NULL;

SDL_Window * initSDL(){
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        printf("Erreur d'initialisation de SDL: %s\n", SDL_GetError());
        exit(1);
    }

    SDL_Window * window = SDL_CreateWindow("Fenêtre SDL2",
                                          SDL_WINDOWPOS_UNDEFINED,
                                          SDL_WINDOWPOS_UNDEFINED,
                                          WIDTH, HEIGHT,
                                          SDL_WINDOW_SHOWN);

    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);

    if (!window) {
        printf("Erreur de création de la fenêtre: %s\n", SDL_GetError());
        SDL_Quit();
        exit(1);
    }

    return window;
}

void closeEventSDL(SDL_Color ** matrix){
    SDL_Event e;
    int quit = 0;
    while (!quit) {
        while (SDL_PollEvent(&e) != 0) {
            if (e.type == SDL_QUIT) {
                quit = 1;
            }
        }
    }

    // Nettoyer et quitter SDL
    SDL_DestroyWindow(window);
    SDL_Quit();

    for (int i = 0; i < WIDTH; i++) {
        free(matrix[i]);
    }
    free(matrix);
}

SDL_Color ** init2DSpace() {
    SDL_Color **matrix = malloc(sizeof(SDL_Color*) * WIDTH);
    if (matrix == NULL) exit(1);

    for (int i = 0; i < WIDTH; i++) {
        matrix[i] = malloc(sizeof(SDL_Color) * HEIGHT);
        if (matrix[i] == NULL) exit(1);

        for (int e = 0; e < HEIGHT; e++) {
            matrix[i][e].r = DEFAULTCOLOR_R;
            matrix[i][e].g = DEFAULTCOLOR_G;
            matrix[i][e].b = DEFAULTCOLOR_B;
            matrix[i][e].a = DEFAULTCOLOR_A;
        }
    }

    return matrix;
}

void RenderMatrix(SDL_Color** matrix) {
    for (int i = 0; i < WIDTH; i++) {
        for (int e = 0; e < HEIGHT; e++) {
            SDL_SetRenderDrawColor(renderer, matrix[i][e].r, matrix[i][e].g, matrix[i][e].b, matrix[i][e].a);
            SDL_RenderDrawPoint(renderer, i, e);
        }
    }
    SDL_RenderPresent(renderer);
}

int main(int argc, char* argv[]) {

    SDL_Window * window = initSDL();
    SDL_Color ** _2DMatrix = init2DSpace();

    RenderMatrix(_2DMatrix);

    // A partir d'ici le travail se fera sur la matrice et a chaque action d'ecriture on fait un travail de render




    closeEventSDL(_2DMatrix);
    return 0;
}
