#!/usr/bin/python3
import socket,select, json, sys, os, shlex, ssl, hashlib

# une fonction qui chercher un fichier json dans le repetoire data return true s'il existe false sinon
def file_exist(filename):
    file_path = os.path.join('.','data',filename)
    if os.path.exists(file_path) == True :
        return True
    return False

# cette fonction permet de retourner le dictionnaire  
def load_dico(filename: str):
    file_path = os.path.join('.','data',filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            # si c'est bien un dictionnaire
            if isinstance(data, dict):
                return data
            return {}
        except Exception:
            return {}

# save_dico permet de sauvegarder notre dico dans le .json
def save_dico(filename, dico):
    dico_file = os.path.join('.','data',filename)
    with open(dico_file, 'w', encoding='utf-8') as f:
        json.dump(dico, f, ensure_ascii=False, indent=4)

# cette fonction nous permet de communiquer avec le serveur master
def master_query(host,port,data):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cafile="./tls/ca.pem")
    context.check_hostname = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ssock = context.wrap_socket(s)
        ssock.connect((host, port))
        ssock.sendall(data.encode('utf-8'))
        data = ssock.recv(1500)
        msg1 = data
        length = int(data.decode().split(" ")[1])
        data=ssock.recv(length)
        msg2 = data
        ssock.close()
        s.close()
        return msg1.decode() , msg2.decode()

# get_command est la fonction qui permet de récuperer une valeur du dictionnaire
# si elle n'as pas la réponse elle envoie une requête au serveur maitre s'il existe
def get_command(sc,dico,key,master_ip,master_port,datarecv,is_admin,l):
# on cherche la clé et on l'a renvoie 
    if key in dico:
        msg =f"OK {len(dico[key])}\n"
        sc.sendall(msg.encode('utf-8'))
        msg =f"{dico[key]}\n"
        sc.sendall(msg.encode('utf-8'))
        if is_admin[sc] == False:
                sc.close()
                l.remove(sc)          
    else:
        # on demande au seveur maitre
        if master_ip != None:
            msg1, msg2 = master_query(master_ip,master_port,datarecv)
            sc.sendall(msg1.encode())
            sc.sendall(msg2.encode())
            if is_admin[sc] == False:
                sc.close()
                l.remove(sc)
        else:
            # msg d'erreur
            err_msg(sc,"cette clé n'existe pas\n",is_admin,l)

# cette fonction permet de retrouver les prefixe elle a le même fonctionnement de get 
# sauf que elle cherche tout ce qui commence par ce préfixe
def pref_command(sc,dico,key,master_ip,master_port,data,is_admin,l):
    # pour chercher les pref on a besoin d'un booléen et 2 liste pour stocker les clés valeurs
    found = False
    prefix_key = []
    prefix_value =[]
    # on chercher les clés
    for k, v in dico.items():
        if k.startswith(key):
            prefix_key.append(k)
            prefix_value.append(v)
            found = True
# si on trouve on les ajoutes dans le message on envoie d'abord OK avec la longueur du message ensuite le msg
    if found == True:
        msg2 = f"Les clés-valeur dont la clé a pour préfixe {key}: "
        for i in range(0,len(prefix_key)):
            msg2 = msg2 + f" {prefix_key[i]} \"{prefix_value[i]}\""
        msg2 += ".\n"
        msg1 = f"OK {len(msg2)}\n"
        sc.sendall(msg1.encode("utf-8"))
        sc.sendall(msg2.encode("utf-8"))
        if is_admin[sc] == False:
            sc.close()
            l.remove(sc)
# on envoie la requête au serveur maître pour voir s'il trouve chez lui les clé
    else :
        if master_ip != None:
            msg1, msg2 = master_query(master_ip,master_port,data)
            sc.sendall(msg1.encode())
            sc.sendall(msg2.encode())
            if is_admin[sc] == False:
                sc.close()
                l.remove(sc)
        # message d'erreur
        else: 
            err_msg(sc,"il y'as pas de clé contenant ce préfixe.\n",is_admin,l)

# del_command permet à l'admin de supprimer des clés elle solicite pas de server maître
def del_command(sc,filename,dico,key):
    # si on trouve on supprime sinon on envoi un message d'erreur
    if key in dico:
        del dico[key]
        save_dico(filename,dico)
        msg2 = "La clé a été supprimé.\n"
        msg1 = f"OK {len(msg2)}\n"
        sc.sendall(msg1.encode("utf-8"))
        sc.sendall(msg2.encode("utf-8"))
    else: 
        msg2 = "La clé n’existe pas.\n"
        msg1 = f"ERR {len(msg2)}"
        sc.sendall(msg1.encode("utf-8"))
        sc.sendall(msg2.encode("utf-8"))

# set_command permet à l'admin d'ajouter des clés ou de changer la valeur des clés elle solicite pas de server maître
def set_command(sc,filename,dico,key,value):    
        if key in dico:
            msg2 = "La clé a été modifier.\n"
        else :
            msg2 = "La clé à été ajouté avec sa valeur.\n"
        dico[key] = value
        save_dico(filename,dico)
        msg1 = f"OK {len(msg2)}\n"
        sc.sendall(msg1.encode("utf-8"))
        sc.sendall(msg2.encode("utf-8"))

# cette fonction nous permet d'optimiser l'écriture et de rendre lisible le code
# elle gére l'envoie des message d'erreur
def err_msg(sc,err,is_admin,l):
    msg = f"ERR {len(err)}\n"
    sc.sendall(msg.encode())
    sc.sendall(err.encode())
    if is_admin[sc] == False:
        sc.close()
        l.remove(sc)

# cette fonction est centrale pour le login elle permet de vérifier si un user à rentrer le bon mot de passe
# le mdp de l'admin est stocker dans le répertoire mdp
def verif_mdp_admin(mdp):
    with open("./mdp/mdp_admin.txt",'r') as f:
        admin_hash = f.read().strip()
    mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()

    if mdp_hash == admin_hash :
        return True
    return False
    

# la fonction main gére les socket avec select et ssl                        
def main():
    if len(sys.argv) != 2 and len(sys.argv) !=3:
        print("Serveur: la commande n'est pas bien utilisée. ")
        print("La Commande marche comme suit :")
        print("./dico_server.py <serveur_maitre> <port>")
        print("le serveur maitre est de la forme suivante ip:port.")
        print("la commande <serveur_maitre> ne doit pas être utilisé pour le lancement des serveurs maître.")
        sys.exit(1)

    # ip , port du serveur maître
    master_ip = None
    master_port = None

    
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    elif len(sys.argv) == 3:
        master_ip = sys.argv[1].split(':')[0]
        master_port = int(sys.argv[1].split(':')[1])
        port = int(sys.argv[2])
    # on regarde si le on a pas la même adresse du serveur et serveur maitre
    if (master_ip == "localhost" or master_ip =="127.0.0.1") and master_port == port :
        master_ip = None
        master_port = None

    #création du socket TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", port))
    server.listen(5)
    print(f"Serveur en écoute sur le port {port}...")
    
    # création du context ssl
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="./tls/server.pem",keyfile="./tls/server.key")

    # liste des admin et socket
    is_admin = {}
    l = [server]
    # gestion des sockets avec select
    while True:
        s_ready,_,_=select.select(l,[],[])
        for s in s_ready:
            if s == server :
                # nouvelle connexion
                s_client, addr = server.accept()
                ssl_client = context.wrap_socket(s_client,server_side=True)
                l.append(ssl_client)
                is_admin[ssl_client] = False
            else :
                # un client à envoyer une requête
                datarecv = s.recv(1500).decode('utf-8')
                data = shlex.split(datarecv)
                print(data)
                # dans cette partie on va gérer la réponses en analysant la requête envoyer
                if len(data) == 0:
                    s.close()
                    l.remove(s)
                elif len(data) == 1:
                    # fermeture de la connexion avec l'admin
                    if (data[0] == "exit") and (is_admin[s] == True):
                        s.close()
                        l.remove(s)
                    else : 
                        err_msg(s,"commande incorrecte ou vous n'avez pas l'autorisation de l'utiliser.",is_admin,l)
                elif len(data) == 2:
                    # gestion de la connexion admin
                    if data[0] == "login" and verif_mdp_admin(data[1]) == True:    
                        msg2 = "Bienvenue admin.\n"
                        msg1 = f"OK {len(msg2)}\n"
                        s.sendall(msg1.encode())
                        s.sendall(msg2.encode())
                        is_admin[s]= True
                    else :
                        err_msg(s,"Mot de passe incorrecte.",is_admin,l)
                elif len(data) == 3 :
                    # gestion des commandes get, pref et del
                    if file_exist(data[0]):
                        dico_file = data[0]
                        dico = load_dico(dico_file)
                        command = data[1]
                        key = data[2]
                        if command == "get":
                            get_command(s,dico,key,master_ip,master_port,datarecv,is_admin,l)
                        elif command == "pref":
                            pref_command(s,dico,key,master_ip,master_port,datarecv,is_admin,l)
                        elif command == "del" and is_admin[s] == True:
                            del_command(s,dico_file,dico,key)
                        else :
                            err_msg(s,"la commande incorrecte ou vous n'avez pas l'autorisation de l'utiliser.",is_admin,l)
                    # si le dictionnaire n'existe pas on demande au serveur maître
                    else:
                        if master_ip != None:
                            msg1 ,msg2 = master_query(master_ip,master_port,datarecv)
                            s.sendall(msg1.encode())
                            s.sendall(msg2.encode())
                        else :
                            err_msg(s,"dictionnaire n'existe pas",is_admin,l)
                elif len(data) == 4 :
                    #gestion de la commande set
                    if file_exist(data[0]):
                        dico_file = data[0]
                        dico = load_dico(dico_file)
                        command = data[1]
                        key = data[2]
                        value = data[3]
                        if command == "set" and is_admin[s] == True:
                            set_command(s,dico_file,dico,key,value)
                        else :
                            err_msg(s,"la commande incorrecte ou vous n'avez pas l'autorisation de l'utiliser.",is_admin,l)
                    else:
                        if master_ip != None:
                            msg = master_query(master_ip,master_port,datarecv)
                            s.sendall(msg)
                        else :
                            err_msg(s,"dictionnaire n'existe pas",is_admin,l)
                else :
                    err_msg(s,"argument incorrecte.",is_admin,l)

if __name__ == "__main__":
    main()