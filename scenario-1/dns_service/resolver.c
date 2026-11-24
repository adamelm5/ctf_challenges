#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

#define PORT 8053
#define BUFFER_SIZE 1024

void handle_client(int client_sock) {
    char buffer[BUFFER_SIZE];
    memset(buffer, 0, BUFFER_SIZE);
    int n = read(client_sock, buffer, BUFFER_SIZE - 1);
    if (n <= 0) return;

    // On attend un format simple : TOKEN HOSTNAME
    char *token = strtok(buffer, " ");
    char *hostname = strtok(NULL, " \n");

    if (token == NULL || hostname == NULL) {
        write(client_sock, "ERREUR: Format attendu TOKEN HOSTNAME\n", 35);
        return;
    }

    // Verification du token (obtenu a l etape 1)
    if (strcmp(token, "medecin_7f3a9c") != 0) {
        write(client_sock, "ERREUR: Token invalide\n", 23);
        return;
    }

    write(client_sock, "Resolution en cours...\n", 23);

    // CECI EST LA PARTIE VULNERABLE (getaddrinfo avec glibc 2.19)
    struct addrinfo hints, *res;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC; // Demande IPv4 et IPv6
    hints.ai_socktype = SOCK_STREAM;

    int status = getaddrinfo(hostname, "80", &hints, &res);
    if (status != 0) {
        write(client_sock, "ERREUR: getaddrinfo a echoue (code " + status + ")\n", 45);
        return;
    }
    freeaddrinfo(res);

    // Si le crash n a pas eu lieu, on renvoie le hostname secret
    write(client_sock, "SUCCES: archive-srv.hospital.internal\n", 39);
}

int main() {
    int server_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (server_sock < 0) { perror("socket"); return 1; }

    int opt = 1;
    setsockopt(server_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(PORT);

    if (bind(server_sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind"); return 1;
    }

    listen(server_sock, 5);
    printf("DNS Service en ecoute sur le port %d\n", PORT);
    fflush(stdout);

    while (1) {
        int client_sock = accept(server_sock, NULL, NULL);
        if (client_sock < 0) continue;
        handle_client(client_sock);
        close(client_sock);
    }
    return 0;
}
