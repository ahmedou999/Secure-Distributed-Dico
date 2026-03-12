#!/usr/bin/python3
import socket, sys, ssl

def main():


   # on defini les arguments 
    host = sys.argv[1]
    port = int(sys.argv[2])

    msg = ""
    for i in range(3,len(sys.argv)):
        msg = msg + " " + sys.argv[i]
    
    # le context
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cafile="./tls/ca.pem")
    context.check_hostname = False

    #on se connecte et on envoie la requête avec le socket ssl
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ssock = context.wrap_socket(s)
        ssock.connect((host, port))
        ssock.sendall(msg.encode('utf-8'))
        while True:
            data = ssock.recv(1024)
            print(data.decode('utf-8'))
            #on prend la longueur du msg 
            length = int(data.decode().split(" ")[1].split('\n')[0])
            data=ssock.recv(length+100)
            print(data.decode('utf-8'))
            #on reste dans connecté et on envoie des nouvelles requête
            query = input("===> ")
            ssock.send(query.encode())
            if query == "exit":
                break
        ssock.close()
        s.close


if __name__ == "__main__":
    main()
