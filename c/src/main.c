#include "../libs/pyDraw.h"
int main(int argc, char* argv[]) {
initMatrix();
initSDL();
int width = 500;
int height = 500;
PEN p = createPen(width, height);
PEN p1 = createPen(0, 0);
p1 = walk(p1,100);
p1 = goTo(p1,200, 0);
p1.rotation = 270;
p1 = walk(p1,100);
p1 = goTo(p1,200, 200);
p1.rotation = 470;
p1 = walk(p1,100);
int y = height/2;
fillColor(300, 200, "0000ff");
circle(p,300);
p.rotation = 50;
p = walk(p,100);
p.rotation = 150;
p = walk(p,100);
int x = 0;
for (x; x < 20; x++) {
p.rotation = x*70;
p.thickness = x;
p.thickness = x;
if (x == 7) {
p = goTo(p,width / 2, 600);
}
else if (x == 12) {

}
else if (x == 16) {
p.penDown = 0;
}
else if (x == 18) {
p.penDown = 1;
}
p = walk(p,500);
}
fillColor(300, 200, "00FF00");
rotateArea(100, 100, 400, 300, 57);
copyPaste(100, 100, 400, 300, 150, 50);
translation(100, 100, 400, 200, 100, 20, 2);
translation(width / 2 + 200, height / 2 + 200, 400, 200, 100, 20, 10);
translation(100, 50, 400, 200, 100, 20, -5);
fillColor(500, 500, "FFFF00");
closeEventSDL();
return 0;
}