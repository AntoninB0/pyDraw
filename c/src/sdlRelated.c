#include "../libs/sdlRelated.h"


void waitKey(){
    SDL_Event event;
    int quit = 0;
    while (!quit) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_KEYDOWN) {
                quit = 1;
            }
            if (event.type == SDL_QUIT) {
                SDL_DestroyRenderer(renderer);
                SDL_DestroyWindow(window);
                SDL_Quit();

                for (int i = 0; i < WIDTH; i++) {
                    free(matrix[i]);
                }
                free(matrix);

                exit(0);
            }
        }
    }
};

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

void renderMatrix() {
    for (int i = 0; i < WIDTH; i++) {
        for (int e = 0; e < HEIGHT; e++) {
            SDL_SetRenderDrawColor(renderer, matrix[i][e].r, matrix[i][e].g, matrix[i][e].b, matrix[i][e].a);
            SDL_RenderDrawPoint(renderer, i, e);
        }
    }
    SDL_Delay(SPEED);
    SDL_RenderPresent(renderer);
}

void initSDL() {
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

    renderMatrix();
}