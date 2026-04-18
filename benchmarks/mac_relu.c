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
        register long acc asm("a0") = 0;
        for (int j = 0; j < N; j++) {
            register long a asm("a1") = W[i][j];
            register long b asm("a2") = input[j];
            // MAC: funct7=0x00, funct3=0x1, opcode=0x2B, rd=a0, rs1=a1, rs2=a2
            // 0000000 01100 01011 001 01010 0101011 = 0x00C5852B
            asm volatile(".word 0x00C5852B\n"
                : "+r"(acc) : "r"(a), "r"(b));
        }
        // ReLU: funct7=0x16, funct3=0x1, opcode=0x2B, rd=rs1=rs2=a0
        asm volatile(".insn r 0x2B, 0x1, 0x16, %0, %0, %0"
            : "+r"(acc));
        output[i] = (int)acc;
    }

    print_int(output[0]);
    print_int(output[63]);
    asm volatile("li a7, 93\nli a0, 0\necall\n");
}
