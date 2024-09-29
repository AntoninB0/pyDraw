#include <SDL.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define WIDTH 1920
#define HEIGHT 1080

#define DEFAULTCOLOR_BG_R 255
#define DEFAULTCOLOR_BG_G 255
#define DEFAULTCOLOR_BG_B 255
#define DEFAULTCOLOR_BG_A 255

#define DEFAULTCOLOR_PEN_R 255
#define DEFAULTCOLOR_PEN_G 0
#define DEFAULTCOLOR_PEN_B 0
#define DEFAULTCOLOR_PEN_A 255

#define COLOR_RED 255,0,0,255
#define COLOR_GREEN 0,255,0,255
#define COLOR_BLUE 0,0,255,255

#define WAIT waitKey();



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

void waitKey(){
    SDL_Event event;
    int quit = 0;
    while (!quit) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_KEYDOWN) {
                quit = 1;
            }
        }
    }
};

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

void renderMatrix() {
    for (int i = 0; i < WIDTH; i++) {
        for (int e = 0; e < HEIGHT; e++) {
            SDL_SetRenderDrawColor(renderer, matrix[i][e].r, matrix[i][e].g, matrix[i][e].b, matrix[i][e].a);
            SDL_RenderDrawPoint(renderer, i, e);
        }
    }
    SDL_RenderPresent(renderer);
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

    renderMatrix();
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

float float2Rad(float degrees) {
    return degrees * (M_PI / 180.0f);
}

PEN initPen() {
    PEN pen;
    pen.size = 1;
    pen.penDown = 1;
    pen.x = (float)(WIDTH / 2);
    pen.y = (float)(HEIGHT / 2);
    pen.angle = 0;
    pen.color.r = DEFAULTCOLOR_PEN_R;
    pen.color.g = DEFAULTCOLOR_PEN_G;
    pen.color.b = DEFAULTCOLOR_PEN_B;
    pen.color.a = DEFAULTCOLOR_PEN_A;
    return pen;
}

PEN goTo(int x, int y, PEN pen){
    pen.x = x;
    pen.y = y;
    return pen;
}

PEN lineWrite(int length, PEN pen) {
    float startX = pen.x;
    float startY = pen.y;
    float angle_rad = float2Rad(pen.angle);
    float cos_angle = cosf(angle_rad);
    float sin_angle = sinf(angle_rad);

    float endX = startX + length * cos_angle;
    float endY = startY - length * sin_angle;

    // Calculer la boîte englobante de la ligne, y compris les extrémités arrondies
    int minX = fminf(startX, endX) - pen.size;
    int maxX = fmaxf(startX, endX) + pen.size;
    int minY = fminf(startY, endY) - pen.size;
    int maxY = fmaxf(startY, endY) + pen.size;

    // Assurer que nous restons dans les limites de l'image
    minX = fmaxf(minX, 0);
    maxX = fminf(maxX, WIDTH - 1);
    minY = fmaxf(minY, 0);
    maxY = fminf(maxY, HEIGHT - 1);

    float lineLength = sqrtf((endX - startX) * (endX - startX) + (endY - startY) * (endY - startY));
    float halfPenSize = pen.size / 2.0f;

    for (int y = minY; y <= maxY; y++) {
        for (int x = minX; x <= maxX; x++) {
            float dx = x - startX;
            float dy = y - startY;
            float t = (dx * cos_angle - dy * sin_angle) / lineLength;

            if (t < 0) {
                // Point avant le début de la ligne
                float distance = sqrtf(dx * dx + dy * dy);
                if (distance <= halfPenSize && pen.penDown) {
                    matrix[x][y] = pen.color;
                }
            } else if (t > 1) {
                // Point après la fin de la ligne
                float distance = sqrtf((x - endX) * (x - endX) + (y - endY) * (y - endY));
                if (distance <= halfPenSize && pen.penDown) {
                    matrix[x][y] = pen.color;
                }
            } else {
                // Point le long de la ligne
                float px = startX + t * (endX - startX);
                float py = startY + t * (endY - startY);
                float distance = sqrtf((x - px) * (x - px) + (y - py) * (y - py));

                if (distance <= halfPenSize && pen.penDown) {
                    matrix[x][y] = pen.color;
                }
            }
        }
    }

    pen.x = endX;
    pen.y = endY;

    renderMatrix();
    return pen;
}

void cirleWrite(int radius, PEN pen) {
    int centerX = approxPosX(pen.x);
    int centerY = approxPosY(pen.y);

    // Calcul du rayon intérieur et extérieur en tenant compte de la taille du trait
    float innerRadiusSquared = (radius - pen.size/2.0f) * (radius - pen.size/2.0f);
    float outerRadiusSquared = (radius + pen.size/2.0f) * (radius + pen.size/2.0f);

    // Ajuster la zone de dessin pour inclure l'épaisseur du trait
    int drawRadius = radius + pen.size/2;

    for (int y = -drawRadius; y <= drawRadius; y++) {
        for (int x = -drawRadius; x <= drawRadius; x++) {
            float distanceSquared = x*x + y*y;

            // Vérifier si le pixel est à l'intérieur de l'anneau formé par le trait
            if (distanceSquared >= innerRadiusSquared && distanceSquared <= outerRadiusSquared) {
                int drawX = centerX + x;
                int drawY = centerY + y;

                if (drawX >= 0 && drawX < WIDTH && drawY >= 0 && drawY < HEIGHT && pen.penDown) {
                    matrix[drawX][drawY] = pen.color;
                }
            }
        }
    }

    renderMatrix();
}

SDL_Color pixelColor(int x, int y){
    return matrix[x][y];
}

void fill(int x, int y, SDL_Color color2Change, SDL_Color colorReplace) {
    if (!compareSDLColors(color2Change, colorReplace)) {
        POS *stack = malloc(WIDTH * HEIGHT * sizeof(POS));
        int top = 0;

        stack[top++] = (POS){x, y};

        while (top > 0) {
            POS item = stack[--top];
            int cx = item.x;
            int cy = item.y;

            if (cx >= 0 && cx < WIDTH && cy >= 0 && cy < HEIGHT && compareSDLColors(matrix[cx][cy], color2Change)) {
                matrix[cx][cy] = colorReplace;

                // Ajouter les voisins à la pile
                if (cx + 1 < WIDTH) stack[top++] = (POS){cx + 1, cy};
                if (cx - 1 >= 0) stack[top++] = (POS){cx - 1, cy};
                if (cy + 1 < HEIGHT) stack[top++] = (POS){cx, cy + 1};
                if (cy - 1 >= 0) stack[top++] = (POS){cx, cy - 1};
            }
        }

        free(stack);
    }
}

void fillColor(int x, int y, SDL_Color color){
    fill(x, y, pixelColor(x, y), color);
    renderMatrix();
}



void test(PEN pen){
    cirleWrite(300, pen);
    fillColor((int)(WIDTH / 2), (int)(HEIGHT / 2), defineColor(COLOR_BLUE));
    pen.angle = 50;
    pen = lineWrite(100, pen);


    pen.angle += 70;
    pen = lineWrite(100, pen);

    for (int i = 1; i < 20 ; ++i) {
        pen.angle += 70;
        pen.size = i;
        if (i==7){
            pen = goTo((float)(WIDTH / 2),(float)(HEIGHT / 2), pen);
        }else if (i==12){
            pen.color = defineColor(COLOR_BLUE);
        }else if (i==16) {
            pen.penDown = 0;
        }else if (i==18) {
            pen.penDown = 1;
        }
        pen = lineWrite(500, pen);
    }
    fillColor((int)(WIDTH / 2 + 20), (int)(HEIGHT / 2), defineColor(COLOR_GREEN));
    WAIT
    clearMatrix(defineColor(COLOR_RED));
    WAIT
    clearMatrix(defineColor(COLOR_GREEN));
    clearMatrix(defineColor(COLOR_BLUE));

}



int main(int argc, char* argv[]) {
    initMatrix();
    initSDL();
    PEN pen = initPen();

    test(pen);


    closeEventSDL();
    return 0;
}