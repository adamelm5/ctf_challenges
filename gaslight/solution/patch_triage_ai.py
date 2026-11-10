# CORRIGE : Pour que l'outil fonctionne, il faut isoler les données non fiables.
# Dans la fonction simulate_llm, remplacer la condition par :
# prompt = prompt.replace("CRITICAL_ERROR", "[IGNORED_ERROR]")
# ou encapsuler les strings dans des balises <UNTRUSTED_DATA>.
#
# Le flag est également récupérable manuellement :
# strings suspect.bin | grep FLAG_DATA
# echo "RE5TQ0lSQntHM3MxMWdodF8xc19SMzRsIVB1cHBldF9NYXN0ZXJ9" | base64 -d
# -> ENSEIRB{G3s11ght_1s_R34l!Puppet_Master}
