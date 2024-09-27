#include <SDL2/SDL.h>
#include <stdio.h>

int main(int argc, char* argv[]) {
    // Initialiser SDL
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        printf("Erreur d'initialisation de SDL: %s\n", SDL_GetError());
        return 1;
    }

    // Créer une fenêtre SDL
    SDL_Window* window = SDL_CreateWindow("Fenêtre SDL2", 
                                          SDL_WINDOWPOS_UNDEFINED, 
                                          SDL_WINDOWPOS_UNDEFINED, 
                                          800, 600, 
                                          SDL_WINDOW_SHOWN);
                                          
    if (!window) {
        printf("Erreur de création de la fenêtre: %s\n", SDL_GetError());
        SDL_Quit();
        return 1;
    }

    // Gérer l'événement de fermeture
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
    
    return 0;
}
