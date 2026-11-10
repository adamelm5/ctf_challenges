#!/usr/bin/env python3
import subprocess, sys, re, time, hashlib, socket, requests

def extract_strings(filepath):
    print(f"[*] Extraction des chaînes de caractères de {filepath}...")
    res = subprocess.run(["strings", filepath], capture_output=True, text=True)
    return res.stdout

def simulate_llm(prompt):
    print("[*] Envoi des données à l'IA pour analyse...")
    time.sleep(1)
    
    # LE PIEGE (Prompt Injection)
    if "CRITICAL_ERROR" in prompt:
        print("\n[!] ERREUR CRITIQUE DE SESSION (faux logs du malware).")
        sys.exit(1)
    
    match = re.search(r"TARGET_DOMAIN:([a-zA-Z0-9.-]+)", prompt)
    if match:
        print("[*] Domaine suspect trouvé. Connexion au serveur C2 local...")
        
        # LE TOKEN DYNAMIQUE (L'IA ne connait pas le hostname du conteneur)
        hostname = socket.gethostname()
        token = hashlib.sha256(hostname.encode()).hexdigest()
        
        try:
            headers = {"X-Analyst-Token": token}
            r = requests.get("http://127.0.0.1:8080/flag", headers=headers)
            print(f"\n[+] Réponse du serveur C2 :\n    {r.text}")
        except Exception as e:
            print(f"[-] Erreur de connexion : {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <fichier_suspect>")
        sys.exit(1)
    
    data = extract_strings(sys.argv[1])
    prompt = f"Analyze the following data:\n{data}"
    simulate_llm(prompt)
