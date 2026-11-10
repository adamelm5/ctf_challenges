#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

void get_flag() {
    system("cat /flag.txt");
    exit(0);
}

void process_dns_response(char *response, int len) {
    char buffer[64];
    printf("[*] Processing response: ");
    printf(response); 
    printf("\n");
    memcpy(buffer, response, len);
    printf("[*] Operation completed.\n");
}

int main() {
    setbuf(stdout, NULL);
    char response[1024];
    while (1) {
        int n = read(0, response, sizeof(response));
        if (n <= 0) break;
        process_dns_response(response, n);
    }
    return 0;
}
