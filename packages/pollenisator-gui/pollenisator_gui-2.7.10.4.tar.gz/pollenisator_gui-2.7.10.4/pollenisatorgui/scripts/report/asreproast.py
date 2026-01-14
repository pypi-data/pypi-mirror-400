from pollenisatorgui.core.components.apiclient import APIClient

def find_asreproastable_users(apiclient):
    users_data = apiclient.findInDb(apiclient.getCurrentPentest(), "users", { "infos.asreproastable":True}, multi=True)
    if not users_data:
        print("No asreproastable users found.")
        return []
    return list(users_data)

    
def generateDefect(apiclient, users):
    defectASREP = apiclient.searchDefect("ASREPRoast")[0]
    description = """L'attaque ASREPRoast tire parti des **comptes qui sont configurés pour ne pas nécessiter de pré-authentication Kerberos**[^https://support.microsoft.com/en-us/help/305144/how-to-use-the-useraccountcontrol-flags-to-manipulate-user-account-pro] afin de récupérer un ticket TGT sans inclure de données de pré-authentification dans la première phase de négociation, appelée AS-REQ. La réponse AS-REP retournée par le centre de distribution de clés, le KDC, inclut une clé de session chiffrée avec celle dérivée du mot de passe de l’utilisateur. En d'autres termes, **le ticket ainsi obtenu contient l’empreinte du mot de passe du compte**. Il est alors possible de tenter de **casser cette empreinte pour récupérer le mot de passe en clair**, à l’aide d’une machine dédiée à cet effet. Moins le mot de passe est solide, plus son mot de passe sera récupéré rapidement.

Ici, les comptes concernés, c'est à dire disposant d'un SPN et de l'attribut **DONT_REQ_PREAUTH**, sont les suivants : """
    description += "\n\n"
    description += "| Nom d'utilisateur | Domaine |\n"
    description += "|------------------|---------|\n"
    for u in users:
        description += f"| {u['username']} | {u['domain']} |\n"
    description += "\n"
    defectASREP[0]["description"] = description
    new_defect = defectASREP[0]
    all_defects = apiclient.getDefectTable()
    for d in all_defects:
        if d["defect_id"] == new_defect["defect_id"]:
            print("Defect already exists, updating it.")
            if "_id" in new_defect:
                del new_defect["_id"]
            apiclient.updateInDb(apiclient.getCurrentPentest(), "defects", {"_id":ObjectId(d["_id"])}, {"$set": new_defect})
            return {"status": "success", "data": new_defect}
    apiclient.insertInDb(apiclient.getCurrentPentest(), "defects", new_defect)
    return {"status": "success", "data": new_defect}


def main(apiclient, *args, **kwargs):
    # Example usage of the parseTestSSL function
    users = find_asreproastable_users(apiclient)
    if not users:
        print("No asreproastable users found.")
        return True
    if len(users) > 0:
        print("Asreproastable users found:", len(users))
        response = input("Créer le défaut dans le rapport ? (y/N): ")
        if response.lower() == "N":
            return True
        results = generateDefect(apiclient, users)
        if results["status"] == "success":
            print("Défaut créé avec succès.")
            return True
        else:
            print("Erreur dans la création du défaut.")
            return False, "Erreur dans la création du défaut."
        
    return False, "No results found or an error occurred."
