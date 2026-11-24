#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

void get_flag() {
    system("cat /flag.txt");
    exit(0);
}

void process_dns_packet(int sockfd, struct sockaddr_in *client_addr, socklen_t client_len, char *response, int len) {
    char buffer[64];
    char out_buf[1024];
    int out_len = 0;

    // On prépare la réponse
    out_len += sprintf(out_buf + out_len, "[*] Processing DNS packet: ");
    out_len += sprintf(out_buf + out_len, response); // FAILLE 1 : Format String
    out_len += sprintf(out_buf + out_len, "\n");
    
    // On renvoie la réponse via UDP
    sendto(sockfd, out_buf, out_len, 0, (struct sockaddr *)client_addr, client_len);

    // FAILLE 2 : Buffer Overflow
    memcpy(buffer, response, len);
    
    char *done_msg = "[*] Operation completed.\n";
    sendto(sockfd, done_msg, strlen(done_msg), 0, (struct sockaddr *)client_addr, client_len);
}

int main() {
    setbuf(stdout, NULL);
    int sockfd;
    struct sockaddr_in server_addr, client_addr;
    char buffer[1024];
    socklen_t client_len = sizeof(client_addr);

    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(53);

    bind(sockfd, (const struct sockaddr *)&server_addr, sizeof(server_addr));

    while (1) {
        int n = recvfrom(sockfd, (char *)buffer, 1024, MSG_WAITALL, (struct sockaddr *) &client_addr, &client_len);
        if (n > 0) {
            process_dns_packet(sockfd, &client_addr, client_len, buffer, n);
        }
    }
    close(sockfd);
    return 0;
}
