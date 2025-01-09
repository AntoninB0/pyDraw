#include "../libs/fill.h"

POS pop(Stack *stack) {
    return stack->data[--stack->size];
}

bool isEmpty(Stack *stack) {
    return stack->size == 0;
}

void freeStack(Stack *stack) {
    free(stack->data);
}

void fill(int x, int y, SDL_Color color2Change, SDL_Color colorReplace) {
    if (!compareSDLColors(color2Change, colorReplace)) {

        Stack stack = { .data = malloc(100 * sizeof(POS)), .size = 0, .capacity = 100 };
        if (stack.data == NULL) {
            fprintf(stderr, "Allocation de la pile échouée.\n");
            exit(1);
        }

        push(&stack, (POS){x, y});

        while (!isEmpty(&stack)) {
            POS item = pop(&stack);
            int cx = item.x;
            int cy = item.y;

            if (cx >= 0 && cx < WIDTH && cy >= 0 && cy < HEIGHT && compareSDLColors(matrix[cx][cy], color2Change)) {
                matrix[cx][cy] = colorReplace;

                // Ajouter les voisins si valides
                if (cx + 1 < WIDTH && compareSDLColors(matrix[cx + 1][cy], color2Change)) push(&stack, (POS){cx + 1, cy});
                if (cx - 1 >= 0 && compareSDLColors(matrix[cx - 1][cy], color2Change)) push(&stack, (POS){cx - 1, cy});
                if (cy + 1 < HEIGHT && compareSDLColors(matrix[cx][cy + 1], color2Change)) push(&stack, (POS){cx, cy + 1});
                if (cy - 1 >= 0 && compareSDLColors(matrix[cx][cy - 1], color2Change)) push(&stack, (POS){cx, cy - 1});
            }
        }

        freeStack(&stack);
    }
}

void fillColor(int x, int y, char *hex){
    SDL_Color color = defineColor(hex);
    fill(x, y, pixelColor(x, y), color);
    renderMatrix();
}

void push(Stack *stack, POS pos) {
    if (stack->size >= stack->capacity) {
        stack->capacity *= 2;
        stack->data = realloc(stack->data, stack->capacity * sizeof(POS));
        if (stack->data == NULL) {
            fprintf(stderr, "Réallocation de la pile échouée.\n");
            exit(1);
        }
    }
    stack->data[stack->size++] = pos;
}