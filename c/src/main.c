#include "../libs/pyDraw.h"
int main(int argc, char* argv[]) {
initMatrix();
initSDL();
int width = 800;
int height = 1080;
PEN p = createPen(width, height);
PEN p1 = createPen(0, 0);
p1 = walk(p1,100);
p1 = goTo(p1,200, 20);
p1.rotation = 270;
p1 = walk(p1,100);
p1 = goTo(p1,200, 200);
p1.rotation = 470;
p1 = walk(p1,100);
int y = height/2;
fillColor(300, 200, "0000ff");
int test(int a) {
circle(p,a);
}
circle(p,300);
fillColor(width / 2, height / 2, "f0f00f");
p.rotation = 50;
p = walk(p,100);
p.rotation = 150;
p.rotation = p.rotation+70;
p = walk(p,100);
int x = 0;
int z = 0;
for (x; x < 20; x++) {
p.rotation = x*70;
p.thickness = x;
z = test(x * 10);
p.thickness = x;
if (x == 7) {
p = goTo(p,width / 2, 600);
}
else if (x == 12) {
p.color = defineColor("00FFFF");
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
copy(100, 100, 400, 300);
paste(800, 600);
rotateArea(100, 100, 400, 300, 57);
copyPaste(100, 100, 400, 300, 150, 50);
translation(100, 100, 400, 200, 100, 20, 2);
translation(width / 2 + 200, height / 2 + 200, 400, 200, 100, 20, 10);
translation(100, 50, 400, 200, 100, 20, -5);
fillColor(500, 500, "FFFF00");
clearMatrix("FF0000");
clearMatrix("00FF00");
closeEventSDL();
return 0;
}