#!/usr/bin/python3
import socket, sys, ssl

def main():
    if len(sys.argv) != 6:
        print("Usage: la commande n'est pas bien utilisé. ")
        print("La Commande marche comme suit :")
        print ("dico_client.py <host> <port> <dictionnaire> <command> \"<clé>\"")
        print("la clé est entre guillemets")
        sys.exit(1)

   # on defini les arguments 
    host = sys.argv[1]
    port = int(sys.argv[2])
    dico = sys.argv[3]
    command = sys.argv[4]
    key = sys.argv[5]
    # le payload
    message = f"{dico} {command} \"{key}\"\n"

    # le context
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cafile="./tls/ca.pem")
    context.check_hostname = False
    # on se connecte, on envoie le message avec le socket ssl et on recoie la réponse dans data
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ssock = context.wrap_socket(s)
        ssock.connect((host, port))
        ssock.sendall(message.encode('utf-8'))
        #on prend d'abord la longueur du message et on l'affiche
        data = ssock.recv(1024)
        print(data.decode('utf-8'))
        length = int(data.decode().split(" ")[1].split('\n')[0])
        data=ssock.recv(length+100)
        print(data.decode('utf-8'))
        ssock.close()
        exit()

if __name__ == "__main__":
    main()
