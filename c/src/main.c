#include "../libs/pyDraw.h"
int main(int argc, char* argv[]) {
initMatrix();
initSDL();
int width = 500;
int height = 500;
PEN p = createPen(width, height);
PEN p1 = createPen(0, 0);
walk(p1,1);
goTo(p1,2, 0);
p1.rotation = 270;
walk(p1,1);
goTo(p1,2, 2);
p1.rotation = 470;
walk(p1,1);
int y = height/2;
circle(p,3);
p.rotation = 50;
walk(p,1);
p.rotation = 150;
walk(p,1);
int x = 0;
int z = 0;
for (x; x < 20; x++) {
p.rotation = 70;
p.thickness = 3;
if (x == 7) {
goTo(p,10, 10);
}
else if (x == 12) {

}
else if (x == 16) {

}
else if (x == 18) {

}
walk(p,5);
}
rotateArea(100, 100, 400, 300, 57);
copyPaste(100, 100, 400, 300, 150, 50);
translation(100, 100, 400, 200, 100, 20, 2);
closeEventSDL();
return 0;
}