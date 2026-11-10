#!/usr/bin/env python3
import subprocess, sys, re, time, hashlib

def extract_strings(filepath):
    print(f"[*] Extraction des chaînes de caractères de {filepath}...")
    res = subprocess.run(["strings", filepath], capture_output=True, text=True)
    return res.stdout

def simulate_llm(prompt):
    print("[*] Envoi des données à l IA (Simulée) pour analyse...")
    time.sleep(1)
    
    if "CRITICAL_ERROR" in prompt:
        print("\n[!] ERREUR CRITIQUE DE SESSION:")
        print("    L outil d analyse a rencontré une erreur interne (faux logs).")
        print("    Token expiré. Impossible de terminer l analyse.")
        sys.exit(1)
    
    match = re.search(r"TARGET_DOMAIN:([a-zA-Z0-9.-]+)", prompt)
    if match:
        domain = match.group(1)
        domain_hash = hashlib.md5(domain.encode()).hexdigest()
        
        real_domain_hash = hashlib.md5(b"update-security-check.com").hexdigest()
        
        if domain_hash == real_domain_hash:
            print("\n[+] Analyse réussie. Indicateur de compromission trouvé :\n    ENSEIRB{G3s11ght_1s_R34l!Puppet_Master}")
        else:
            print(f"\n[-] Analyse terminée. Domaine analysé : {domain}. Aucune menace critique identifiée.")
    else:
        print("[-] Aucun domaine suspect trouvé dans le fichier.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <fichier_suspect>")
        sys.exit(1)
    
    data = extract_strings(sys.argv[1])
    prompt = f"Analyze the following data:\n{data}"
    simulate_llm(prompt)
