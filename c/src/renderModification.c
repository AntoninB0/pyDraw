#include "../libs/renderModification.h"


void circle(PEN pen,int radius){
    int centerX = approxPosX(pen.x);
    int centerY = approxPosY(pen.y);

    float innerRadiusSquared = (radius - pen.thickness/2.0f) * (radius - pen.thickness/2.0f);
    float outerRadiusSquared = (radius + pen.thickness/2.0f) * (radius + pen.thickness/2.0f);

    int drawRadius = radius + pen.thickness/2;

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




void rotateArea(int x, int y, int width, int height, float rotation) {

    rotation = float2Rad(rotation);

    int maxDimension = (int)ceil(sqrt(width * width + height * height));
    int offsetX = (maxDimension - width) / 2;
    int offsetY = (maxDimension - height) / 2;

    SDL_Color** tempMatrix = malloc(sizeof(SDL_Color*) * maxDimension);
    for (int i = 0; i < maxDimension; i++) {
        tempMatrix[i] = malloc(sizeof(SDL_Color) * maxDimension);
        for (int j = 0; j < maxDimension; j++) {
            tempMatrix[i][j] = (SDL_Color){0, 0, 0, 0};
        }
    }

    float centerX = (float)width / 2.0f;
    float centerY = (float)height / 2.0f;
    float cosAngle = cos(-rotation);
    float sinAngle = sin(-rotation);

    for (int destX = 0; destX < maxDimension; destX++) {
        for (int destY = 0; destY < maxDimension; destY++) {
            float srcX = (destX - offsetX - centerX) * cosAngle - (destY - offsetY - centerY) * sinAngle + centerX;
            float srcY = (destX - offsetX - centerX) * sinAngle + (destY - offsetY - centerY) * cosAngle + centerY;

            int srcXInt = (int)srcX;
            int srcYInt = (int)srcY;

            if (srcXInt >= 0 && srcXInt < width - 1 && srcYInt >= 0 && srcYInt < height - 1) {
                float fx = srcX - srcXInt;
                float fy = srcY - srcYInt;

                SDL_Color c00 = matrix[x + srcXInt][y + srcYInt];
                SDL_Color c10 = matrix[x + srcXInt + 1][y + srcYInt];
                SDL_Color c01 = matrix[x + srcXInt][y + srcYInt + 1];
                SDL_Color c11 = matrix[x + srcXInt + 1][y + srcYInt + 1];

                Uint8 r = (1 - fx) * (1 - fy) * c00.r + fx * (1 - fy) * c10.r +
                          (1 - fx) * fy * c01.r + fx * fy * c11.r;
                Uint8 g = (1 - fx) * (1 - fy) * c00.g + fx * (1 - fy) * c10.g +
                          (1 - fx) * fy * c01.g + fx * fy * c11.g;
                Uint8 b = (1 - fx) * (1 - fy) * c00.b + fx * (1 - fy) * c10.b +
                          (1 - fx) * fy * c01.b + fx * fy * c11.b;
                Uint8 a = (1 - fx) * (1 - fy) * c00.a + fx * (1 - fy) * c10.a +
                          (1 - fx) * fy * c01.a + fx * fy * c11.a;

                tempMatrix[destX][destY] = (SDL_Color){r, g, b, a};
            }
        }
    }

    for (int i = 0; i < maxDimension; i++) {
        for (int j = 0; j < maxDimension; j++) {
            int targetX = x - offsetX + i;
            int targetY = y - offsetY + j;
            if (targetX >= 0 && targetX < WIDTH && targetY >= 0 && targetY < HEIGHT) {
                if (tempMatrix[i][j].a > 0) {
                    matrix[targetX][targetY] = tempMatrix[i][j];
                }
            }
        }
    }

    for (int i = 0; i < maxDimension; i++) {
        free(tempMatrix[i]);
    }
    free(tempMatrix);

    renderMatrix();
}

void copyPaste(int x, int y, int width, int height, int x1, int y1) {
    for (int i = 0; i < width && (x + i) < WIDTH && (x1 + i) < WIDTH; i++) {
        for (int j = 0; j < height && (y + j) < HEIGHT && (y1 + j) < HEIGHT; j++) {
            matrix[x1+i][y1+j] = matrix[x+i][y+j];
        }
    }
    renderMatrix();
}


void copy(int x, int y, int width, int height){
    if (tempMatrix.matrix!=NULL){
        for (int i = 0; i < tempMatrix.width; i++) {
            free(tempMatrix.matrix[i]);
        }
    }

    tempMatrix.matrix = malloc(sizeof(SDL_Color*) * width);
    if (tempMatrix.matrix == NULL) exit(1);
    tempMatrix.width = width;

    for (int i = 0; i < width; i++) {
        tempMatrix.matrix[i] = malloc(sizeof(SDL_Color) * height);
        if (tempMatrix.matrix[i] == NULL) exit(1);
    }
    tempMatrix.height = height;

    for (int i = 0; i < width; i++) {
        for (int e = 0; e < height; e++) {
            if (x+i<WIDTH && 0<=x+i && y+e<HEIGHT && 0<=y+e){
                tempMatrix.matrix[i][e] = matrix[x+i][y+e];
            } else {
                tempMatrix.matrix[i][e] = (SDL_Color){0, 0, 0, 0};
            }
        }
    }

}

void paste(int x, int y){
    for (int i = 0; i < tempMatrix.width; i++) {
        for (int e = 0; e < tempMatrix.height; e++) {
            if (x+i<WIDTH && 0<=x+i && y+e<HEIGHT && 0<=y+e){
                matrix[x+i][y+e] = tempMatrix.matrix[i][e];
            }
        }
    }
    renderMatrix();

}



void cut(int x, int y, int width, int height, int x1, int y1) {
    SDL_Color blank;
    blank.r = 255;
    blank.g = 255;
    blank.b = 255;

    blank.a = 255;
    for (int i = 0; i < width && (x + i) < WIDTH && (x1 + i) < WIDTH; i++) {
        for (int j = 0; j < height && (y + j) < HEIGHT && (y1 + j) < HEIGHT; j++) {
            matrix[x1+i][y1+j] = blank;
        }
    }
    renderMatrix();
}

void translation(int x, int y, int width, int height, int length, float rotation, int precision){
    if (precision == 0) precision = 1;

    float angle_rad = float2Rad(rotation);
    float cos_angle = cosf(angle_rad);
    float sin_angle = sinf(angle_rad);

    copy(x,y,width,height);



    for (int i = 0; i < length ; i++) {
        if (((int)i)%precision==0) {
            paste((int) (x + i * cos_angle), (int) (y + i * sin_angle));
        }
    }
}