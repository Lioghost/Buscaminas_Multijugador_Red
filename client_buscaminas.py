import socket, pickle, os, time, sys, copy

serverAddress = "localhost"
port = 65430
HEADER = 512

class Client:
    
    def __init__(self) -> None:
        self.matrix = []
        self.storage = []
        self.mines = 0
        self.num_player = 0
        self.start_time = 0


    def initial_response(self, server_conn):
        data = server_conn.recv(1024)
        if not data:
            return
        else:
            data = pickle.loads(data)
            if isinstance(data, str):   #Verifica si se trata de un mensaje y no de un entero correspondiente al turno
                print(data)
                return 0
            else:
                self.num_player = data
                return data


    def start_level(self):
        #Inicia el juego
        print('######--BUSCAMINAS--######')
        print("Selecciona un nivel")
        level = input("(1) PRINCIPIANTE\n(2) EXPERTO\nNivel: ")

        match level:
            case "1":
                return (9, 9, 10)
            case "2":
                return (16, 16, 40)


    def connection_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((serverAddress, port))
            
        match x := self.initial_response(s):
            #Define el tipo de accion a ejecutar {0: El jugador ya no fue aceptado, 1: Jugador iniciador, 2:Jugadores secundarios)
            case 0:
                s.close()
                sys.exit()
            case 1:
                #Permite solicitar al usuario el nivel de deficultad por ser el primer jugador
                level = self.start_level()
                self.start_time = time.time()
                #i, j, mines = level #Desempaqueta la respuesta del nivel de dificultad
                start = pickle.dumps(level)     #Serializa la tupla de datos que contienen el nivel de dificultad
                s.send(start)   #Se envian al servidor los datos sobre el nivel deseado por el usuario
            case _:
                s.send(pickle.dumps(True))

        #Recibe como dato una tupla que contiene el nivel seleccionado por el primer jugaor, no importa el numero de jugador
        data_len = s.recv(HEADER)
        i, j, self.mines = pickle.loads(data_len) 
        print("data_len", data_len)
    
        self.matriz(i,j,"#")    #Inicia un tablero de juego para el usuario con el nivel seleccionado
        self.communication_server(s, i, j)


    def matriz(self, i, j, s):
        #Devuelve una matriz de dimensiones i * j rellena de s
        m = []
        for a in range(i):
            m.append([])
            for b in range(j):
                m[a].append(s)

        self.matrix = m
 

    def printmin(self, campo, i, j):
        #Función que imprime la matriz en un formato agradable para el usuario
        #campoprint = list(campo)
        campoprint = copy.deepcopy(campo)

        x = "  "
        ascii = 65
        #Crea numeracion horizontal con letras
        for j in range(0, i):
            x += " " + chr(j + ascii)

        print("".join(x))
        for p in range(len(campoprint)):
            for t in range(len(campoprint[0])):
                if len(str(campoprint[p][t])) == 1:
                    campoprint[p][t]=str(campoprint[p][t])+" "  #Agrega un espacio a los elementos de la matriz para que se vea mejor

            #Define formato de numeracion vertical con espacios de acuerdo a la cantidad de digitos
            if (p + 1) < 10:
                print(" " + str(p+1)+ " " + "".join(campoprint[p]))
            else:
                print(str(p+1)+ " " + "".join(campoprint[p]))


    def cont(self, b):
        #Cuenta la cantidad de veces que se repite b en la matriz m
        c = 0
        for a in range(len(self.matrix)):
            c += self.matrix[a].count(b)

        return(c)
        
        
    def cronometer(self):
        for h in range(0, 24):
            for m in range(0, 60):
                for s in range(0, 60):
                    os.system('cls')
                    return f"{h}:{m}:{s}"
                    time.sleep(1)


    def communication_server(self, conn_server, i, j):
        while True:

            os.system("cls")

            op = 0
            def upload_data():
                '''Permite actualizar el tablero de cada jugador mientras no es el turno de ese jugador mediante un ciclo, el cual se rompe cuando el
                servidor envía una señal de turno''' 
                while True:
                    num_mines = self.mines - self.cont("* ")
                    print(f"MINAS RESTANTES TOTALES: {num_mines}\nJUGADOR: {self.num_player}")
                    self.printmin(self.matrix,i,j)
                    print("Esperando turno......")
                    data = conn_server.recv(HEADER) #Espera como respuesta un arreglo que cada item contiene un dato diferente, incluyendo el turno
                    data_deserial = pickle.loads(data)
                    #print(data_deserial)

                    #Del try siguiente se ejecuta "except" cuando es la primera vez que se conecta el jugador para mostrar el tablero y no hay datos previos de coordenadas
                    try:
                        i1, j1, mine = data_deserial[4]
                        tupla_aux = (i1, j1)
                        self.storage.append(tupla_aux)
                    except:
                        i1, j1 = (0,0)
                    option = self.review_selection(data_deserial, i, j, i1, j1) #Retorna None si es la primera ejecucion del juego y no hay datos previos de coordenadas rebidas en el arreglo
                    '''Actualiza tablero del jugador independientemente de si es su turno o no con los datos nuevos recibidos del servidor permitiendo incorporar una 
                    mina al formato de impresion y asi poder realizar un conteo de minas'''
                    self.printmin(self.matrix,i,j)
                
                    if option == -1:
                        return option
                    os.system("cls")
                    #Rompe el ciclo si se recibe la señal de turno para ese jugador, por el contrario continua repitiendose hasta que sea su turno con finalidad de actualizar el tablero 
                    if data_deserial[3] == True:
                        break
            
            op = upload_data()
            if op == -1:
                break
            
            num_mines = self.mines - self.cont("* ")
            print(f"MINAS RESTANTES TOTALES: {num_mines}\nJUGADOR: {self.num_player}")
            self.printmin(self.matrix,i,j)
            aux = []
            p1 = int(input("\nFila: "))
            p2 = ord(input("Columna: ").upper()) - 64
            p3 = input("Colocar mina? (s/n): ").lower()

            aux.append(p1)
            aux.append(p2)
            aux.append(p3)
            aux.append(self.matrix)
            i1, j1, mine = p1, p2, p3
            data_serial = pickle.dumps(aux)
            data_len = str(len(data_serial))
            data = bytes(f"{data_len:<{HEADER}}", "utf-8") + data_serial
            conn_server.sendall(data)
        
            data_len = conn_server.recv(HEADER)
        
            if not data_len:
                break
            else:
                data = b''
                data += conn_server.recv(int(data_len))
                data_deserial = pickle.loads(data)
                #print("dataserial: ", data_deserial)
                #input("pause")

                option = self.review_selection(data_deserial, i, j, i1, j1)

                if option == -1:
                    break
                elif option == 0:
                    pass
                else:
                    continue

            self.printmin(self.matrix,i1,j1)
        final = time.time()
        #print(f"Tiempo Transcurrido: {final - self.start_time}")

    #Revisa la respuesta recibida por el servidor y dependiendo de ella ejecuta alguna acción
    def review_selection(self, data_deserial, i, j, i1, j1):

        if data_deserial[2] == self.mines:
            os.system("cls")
            print("\tGANASTE!!!!")
            return -1

        match data_deserial[0]:
            case 0:
                print("\t¡¡¡BOOOOOOOOOM!!!\n")
                self.printmin(data_deserial[1], i, j)
                input("\n\tGAME OVER!...\n\tENTER!")
                return -1
            case 1:
                self.matrix[i1-1][j1-1] = "*"
                return 1
            case 2:
                try:
                    self.matrix = data_deserial[1]
                except:
                    pass
                return 0


client1 = Client()
client1.connection_server()