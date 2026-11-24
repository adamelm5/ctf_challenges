# CTF pédagogique — BatiRenov (4 épreuves chaînées)

Scénario : pentest complet sur l'infrastructure d'une PME fictive "BatiRenov".
Challenge à exécuter **uniquement** dans un environnement Docker isolé, sans
accès Internet.

## Progression

| # | Épreuve | Compétence | Sous-dossier |
|---|---------|-----------|--------------|
| 1 | Pwn DNS | format string + buffer overflow ret2win | `epreuve1_pwn/` |
| 2 | MITM télécom | ARP spoofing, RTP/DTMF RFC 2833 | `epreuve2_mitm/` |
| 3 | Crypto | padding oracle (CVE-2016-2107) | `epreuve3_crypto/` |
| 4 | Web RCE | Log4Shell blind/OOB via DNS | `epreuve4_web_rce/` |

## Lancement

```bash
./init_env.sh                 # génère la clé API partagée (.env)
docker compose up --build -d
ssh analyste@localhost -p 2224   # mot de passe : ENSEIRB2026
```

## Topologie

- `dns_net`   (172.28.0.0/24) : cible DNS + attaquant
- `pbx_net_a` (10.0.10.0/24)  : ext100 + routeur + attaquant
- `pbx_net_b` (10.0.20.0/24)  : ext101 + log_ingest + routeur + attaquant

Le bridge Docker ne route **pas** entre réseaux : c'est le conteneur `routeur`
qui fait passerelle (deux interfaces, IP forwarding, iptables FORWARD).

## Note sur `log_ingest`

Le service `log_ingest` (Spring Boot + Log4j 2.14.1) est protégé par un header
`X-Api-Key` (synchronisé via `.env`). Un firewall iptables **bloque tout trafic
sortant TCP non local** ; seul le **DNS sortant (UDP/53)** vers l'attaquant est
autorisé. Ceci force la variante *blind/OOB* de Log4Shell (callback DNS, puis
exfiltration via sous-domaines encodés) — les callbacks LDAP/RMI classiques ne
fonctionneront pas.

## Comptes

- SSH attaquant : `analyste` / `ENSEIRB2026`

## Nettoyage

```bash
docker compose down -v
rm -f .env
```
