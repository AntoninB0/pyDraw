#include "../libs/pen.h"


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
PEN createPen(int x,int y){
    PEN pen = initPen();
    pen.x = x;
    pen.y = y;
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