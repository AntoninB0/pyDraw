#include "../libs/pyDraw.h"

void test(){

    PEN pen = createPen(WIDTH/2, HEIGHT/2);
    PEN pen1 = createPen(0,0);


    lineWrite(100, pen1);
    goTo(200,0,pen1);
    pen1.angle = 270;
    lineWrite(100, pen1);

    pen1.x = 200;
    pen1.y = 200;
    pen1.angle = 470;
    lineWrite(100, pen1);

    fillColor((int)(WIDTH / 2 + 20), (int)(HEIGHT / 2), "00FF00");

    cirleWrite(300, pen);

    fillColor((int)(WIDTH / 2), (int)(HEIGHT / 2), "00FFff");
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
            pen.color = defineColor("00FFff");
        }else if (i==16) {
            pen.penDown = 0;
        }else if (i==18) {
            pen.penDown = 1;
        }
        pen = lineWrite(500, pen);
    }
    fillColor((int)(WIDTH / 2 + 20), (int)(HEIGHT / 2), "00FF00");

    rotateArea((int)(WIDTH / 2 - 400), (int)(HEIGHT / 2), 400, 300, float2Rad(57));

    copyPaste((int)(WIDTH / 2 - 400), (int)(HEIGHT / 2), 400, 300, (int)(WIDTH / 2 + 400), (int)(HEIGHT / 2));

    translation((int)(WIDTH / 2 - 200), (int)(HEIGHT / 2 - 200), 400,200,100,20,2);
    translation((int) (WIDTH / 2 + 200), (int) (HEIGHT / 2 + 200), 400, 200, 100, 20, 10);
    translation((int) (WIDTH / 2 + 100), (int) (HEIGHT / 2 + 100), 400, 200, 100, 20, -5);

    WAIT
    clearMatrix("FF0000");
    WAIT
    clearMatrix("00FF00");
    clearMatrix("0000FF");

}

int main(int argc, char* argv[]) {
    initMatrix();
    initSDL();
    test();


    closeEventSDL();
    return 0;
}