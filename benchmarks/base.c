#define N 64
int W[N][N];
int input[N];
int output[N];

void print_int(int val) {
    char buf[32];
    int len = 0;
    int tmp = val < 0 ? 0 : val;
    if (tmp == 0) { buf[len++] = '0'; }
    else {
        char rev[32]; int rlen = 0;
        while (tmp > 0) { rev[rlen++] = '0' + (tmp % 10); tmp /= 10; }
        for (int i = rlen-1; i >= 0; i--) buf[len++] = rev[i];
    }
    buf[len++] = '\n';
    asm volatile("li a7, 64\nli a0, 1\nmv a1, %0\nmv a2, %1\necall\n"
        : : "r"(buf), "r"(len) : "a7", "a0", "a1", "a2");
}

void _start() {
    for (int i = 0; i < N; i++) {
        input[i] = (i % 2 == 0) ? (i + 1) : -(i + 1);
        for (int j = 0; j < N; j++)
            W[i][j] = (i + j) % 10 + 1;
    }

    for (int i = 0; i < N; i++) {
        long acc = 0;
        for (int j = 0; j < N; j++)
            acc += (long)W[i][j] * (long)input[j];  // plain C multiply-accumulate
        output[i] = (int)(acc > 0 ? acc : 0);        // ReLU in C
    }

    print_int(output[0]);
    print_int(output[63]);
    asm volatile("li a7, 93\nli a0, 0\necall\n");
}
