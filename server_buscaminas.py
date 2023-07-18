'''
Esta practica se enfoca en la sincornización de hilos con la finalidad de asignar un turno por cada cliente que se
conecta al servidor.
'''

import socket, random, pickle, sys, threading

serverAddress = "localhost"
port = 65430
HEADER = 512

class Servidor:

    def __init__(self, players) -> None:
        self.threads = []
        self.connections = []
        self.players = players
        self.lock = threading.Lock()
        self.count_players = 0
        self.level = ()
        self.current_turn = 0
        self.barrier = threading.Barrier(self.players)
        self.aux = [-1] * 5

    
    def num_players(self, client_conn):

        self.count_players += 1
        if self.count_players > self.players:
            message = 'Lo sentimos, el total de jugadores requeridos para la partida se ha completado, por favor intente mas tarde'
        else:
            message = self.count_players
        
        #Envia como respuesta el numero de jugador o en caso contrario un mensaje rechazo 
        client_conn.send(pickle.dumps(message))
        return self.count_players <= self.players


    def connection_initial(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.bind((serverAddress, port))
            s.listen(1)
            print('Servidor Escuchando')
            #threads = []    #Arreglo de hilos por cada cliente que se conecta
            while True:
        
                conn_client, addr = s.accept() #Bloquea la ejecución del flujo hasta que algun cliente externo se conecta
                if not self.num_players(conn_client):
                    break

                level = conn_client.recv(HEADER)   #Recibe los datos principales correspondientes al nivel seleccionado por el usuario

                print("aux111: ", self.check_threads())
                #Si no hay "level" rompe la conexión 
                if not level:
                    break
                else:
                    datos = pickle.loads(level) #Carga la tupla recibida que contiene información sobre el nivel 
                    if datos != True:   #True corresponde al caso en que el jugador no es el primero en conectarse
                        self.level = datos
                        count_mines = 0
                        matrix = self.build_buscaminas(self.level)
                    #Envia como respuesta el nivel proporcionado por el primer jugador a los demás jugadores que se conecten  
                    conn_client.send(pickle.dumps(self.level))
                print("hilos: ", self.check_threads(), self.threads)
                #Crea un hilo para cada nuevo cliente que se conecta
                id_thread_client = self.count_players - 1
                thread_client = threading.Thread(target = self.new_client, args = (conn_client, addr, matrix, id_thread_client, count_mines))
                thread_client.start()   #Inicia el hilo del cliente nuevo
                self.threads.append(thread_client)   #Agrega el hilo al arreglo "threads" para su verificacion futura
                self.connections.append(conn_client)    #Agrega la conexión al arreglo "connections" para uso futuro

            print("Cliente Desconectado", addr)

    
    #Funcion ejecutada para cada cliente nuevo conectado mediante su respectivo hilo de ejcución
    def new_client(self, conn, address, matrix, id_client, count=0):

        print(f"NUEVA CONEXIÓN {address}.")
        #ARREGLO DE ID DE PROCESO HILO ENTRANTE
        #index_conn = self.connections.index(conn)
        print("Id_client: ", id_client)
        #with conn:
            #Se define un ciclo "while" para mantener una comunicación bilateral indefinida entre cliente y servidor
        while True:

            self.barrier.wait()
            print("index: ", id_client)
            if id_client == self.current_turn:
                self.lock.acquire()

                self.waiting_turn_message(id_client, self.aux)            
                print(matrix)   #Muestra el tablero por el lado del servidor

                #Recibe las coordenadas del cliente a traves de un arreglo
                data_len = self.connections[id_client].recv(HEADER)
            
                #Si no hay data_len, automaticamente rompe el bucle while y cirra conexión mediante "with conn"
                if not data_len:
                    break
                else:
                    data_point = b''
                    data_point += conn.recv(int(data_len))
                    data_deserial = pickle.loads(data_point)
                    i1, j1, mine, client_matrix = data_deserial    #Desempaqueta las coordenadas recibidas del cliente
                    self.aux[4] = (i1, j1, mine)  #Realiza un copia de las coordenadas para reenviarlas a cada cliente y actualizar su tablero

                resp = self.clic(matrix, client_matrix, i1, j1, mine)
                if isinstance(resp, int) == True:
                    self.aux[0] = resp
                else:
                    self.aux[0] = 2
                    self.aux[1] = client_matrix

                if resp == 0:
                    self.aux[1] = matrix
                    self.game_over(id_client, self.aux)

                count += self.check_mines(matrix,i1,j1)
                self.aux[2] = count
                
                print(self.aux)
                self.send_package(conn, self.aux)
                self.current_turn = (self.current_turn + 1) if self.current_turn < (self.players - 1) else 0 
                print("CURRENT_TURN AFTER", self.current_turn)
                self.lock.release()


    def waiting_turn_message(self, current_id, aux):
        
        for index, conn_client in enumerate(self.connections):
            #Verifica si el cliente actual es el que tiene el turno y envia un valor booleano a cada cliente segun corresponda el turno
            if permission := index == current_id:
                pass
            aux[3] = permission
            conn_client.send(pickle.dumps(aux))

    '''
    def check_threads(self):

        flag = 0
        print(self.threads)
        if self.threads:
            for thread in self.threads:
                    #print(thread)
                    if thread.is_alive():
                        flag = flag + 1
                    else:
                        pass
                        #print("Todos los hilos han muerto")
                        
            return 1 if (flag != 0) else 0
        else:
            return 0
    ''' 
    
    def build_buscaminas(self, datos):
    
        i, j, mines = datos
        campo = self.matriz(i, j, 0)

        a = 0
        #Este while rellena la matriz de minas "*".
        while self.cont(campo,"*") < mines:
            campo[random.randint(0,i-1)][random.randint(0,j-1)] = "*"
            a += 1
        
        for x in range(i):
            for y in range(j):
                if campo[x][y] != "*":
                    count = 0
                    for a in [1,0,-1]:
                        for b in [1,0,-1]:
                            try:
                                if campo[x+a][y+b] == "*":
                                    if (x+a>-1 and y+b > -1):
                                        count += 1
                            except:
                                pass
                    campo[x][y]=count
        
        return campo
    
            
    def clic(self, campo, campoShow, i=1, j=1, mina="n"):
        """Función que simula un click"""
        i = int(i) - 1
        j = int(j) - 1

        #print("1: ", campoShow)
        #input("PAUSE")

        if mina == "s":
            campoShow[i][j] = "*"
            return 1
        else:
            if campo[i][j] == "*":
                return 0
            
            elif campoShow[i][j] != 0:
                campoShow[i][j] = campo[i][j]
                if campoShow[i][j] == 0:
                    for a in [1,0,-1]:
                        for b in [1,0,-1]:
                            try:
                                if (i+a > -1 and j+b > -1):
                                    campoShow = self.clic(campo,campoShow,i+1+a,j+1+b,"n")
                            except:
                                pass
        #print("CAMPO: ", campoShow)
        return campoShow


    def send_package(self, conn, data):
        data_serial = pickle.dumps(data)
        data_len = str(len(data_serial))
        data = bytes(f"{data_len:<{HEADER}}", "utf-8") + data_serial
        conn.sendall(data)


    def game_over(self, current_id, aux):

        for index, conn_client in enumerate(self.connections):
            if index != current_id:
                conn_client.send(pickle.dumps(aux))


    def cont(self, m, b):
        """Cuenta la cantidad de veces que se repite b en la matriz m"""
        c = 0
        for a in range(len(m)):
            c = c + m[a].count(b)

        return(c)
    

    def check_mines(self, matrix, i, j):
        #Verifica las minas seleccionadas
        count = 0
        i = int(i) - 1
        j = int(j) - 1
        campo = list(matrix)

        #for i in range(len(matrix)):
            #for j in range(len(matrix)):
        if matrix[i][j] == "*":
                    #print("+"+client_matrix[i][j]+"+ +"+matrix[i][j]+"+")
            count += 1

        return count


    def matriz(self, i, j, s):
        #Devuelve una matriz de dimensiones i * j rellena de s
        m = []
        for a in range(i):
            m.append([])
            for b in range(j):
                m[a].append(s)

        return(m)    
   

if __name__ == '__main__':
    
    players = int(input('Ingrese el numero de jugadores: '))
    servidor = Servidor(players)
    servidor.connection_initial()

