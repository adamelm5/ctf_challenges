#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <resolv.h>

int main(int argc, char *argv[]) {
    char *server = NULL, *hostname = NULL;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--server") && i+1 < argc) server = argv[++i];
        else hostname = argv[i];
    }
    if (!hostname) { fprintf(stderr, "Usage: %s [--server IP:PORT] <hostname>\n", argv[0]); return 1; }
    if (server) {
        char ip[64]; int port = 53; char *c = strchr(server, ':');
        if (c) { *c = 0; port = atoi(c+1); }
        strncpy(ip, server, sizeof(ip)-1);
        res_init();
        _res.nsaddr_list[0].sin_family = AF_INET;
        _res.nsaddr_list[0].sin_addr.s_addr = inet_addr(ip);
        _res.nsaddr_list[0].sin_port = htons(port);
        _res.nscount = 1;
    }
    struct addrinfo h, *r; memset(&h, 0, sizeof(h));
    h.ai_family = AF_UNSPEC; h.ai_socktype = SOCK_STREAM;
    int ret = getaddrinfo(hostname, NULL, &h, &r);
    if (ret) { fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(ret)); return 1; }
    printf("Resolution OK for %s\n", hostname);
    freeaddrinfo(r); return 0;
}
