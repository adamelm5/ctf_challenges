# Audit initial de `ctf_dns`

Audit non destructif réalisé le 17 novembre 2026 sur le conteneur déjà présent.
Aucun test de crash ni d'exploitation n'a été exécuté.

| Vérification | Résultat observé |
|---|---|
| Image | `scenario-1-dns_service` (image locale) |
| État | conteneur en cours d'exécution |
| Paquet glibc | `libc6 2.19-18+deb8u10`, `amd64`, installé |
| Bibliothèque chargée | `/lib/x86_64-linux-gnu/libc-2.19.so` |
| Binaire | `/app/resolver`, ELF x86-64, lié dynamiquement à `libc.so.6` |
| Processus | PID 1 nommé `resolver`, commande `./resolver` |
| NSS | `hosts: files dns` |
| Réseaux | `scenario-1_net_internal1` et `scenario-1_net_internal2` |
| Isolation inspectée | non privilégié; rootfs non read-only; aucune limite mémoire configurée; aucune capacité explicitement ajoutée/retirée |
| Montages | aucun montage déclaré |

## Conclusion

Le chemin dynamique/NSS attendu est présent, mais la version Debian observée
`2.19-18+deb8u10` inclut le correctif de CVE-2015-7547. **Ce conteneur n'est
donc pas une preuve d'environnement vulnérable** et ne doit pas servir à
revendiquer un crash attribuable à cette CVE. Les réseaux multiples et les
limites d'isolation relevées méritent une revue séparée avant tout usage de
laboratoire.

Cet audit ne prouve ni l'absence de tout défaut ni le comportement d'un autre
build. Il n'a pas inspecté le digest du build local, ni déclenché de résolution
adversariale.
