"""
Bestandsnaam  : vcnetwork.py
Module        : vcnetwork
Student       : V. Ciriello
Studentnummer : 800008924
Leerlijn      : Python
Datum:        : september 2018
"""
import socket
import errno
from threading import Thread
from vcmodel import ClientGameInfo, ConnectInfo, ClientDataContainer
from vcdecorators import monitorPerformance


RECVBUF = 4096


class TCPConnectServerThreaded(Thread):
    @monitorPerformance
    def __init__(self, serverProps):
        """
        TCP Server Klasse. Deze klasse is aan de server kant verantwoordelijk
        voor het ontvangen van connectie en spelers gegevens van de Client
        De client dient initieel te verbinden met de server en de specifieke
        client gegevens door sturen. Deze klasse wordt in een eigen Thread
        uitgevoerd. De main-thread blijft dan beschikbaar.

        Als de client verbindt met deze TCP server zal deze klasse en Thread
        starten specifiek voor de verbonden Client om middels die Thread
        informatie uit te wisselen. Dit zorgt ervoor dat de TCP server zelf
        nieuwe connecties kan blijven ontvangen en dus niet Blocking is.

        :param port: number
        """
        Thread.__init__(self)
        self.numberOfClients = serverProps.numberOfClientsToAccept
        self.__clientList = serverProps.clientList
        self.socket = None
        self.address = (serverProps.address, serverProps.tcpPort)
        self.isListening = True
        print('TCP Server Initialized')

    def run(self):
        """
        Starten van de TCP socket Server
        :return:
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create tcp socket
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.address)
        self.socket.listen(5)

        while self.isListening:
            try:
                print('Listening for client connections on TCP port %s' % self.address[1])
                client, address = self.socket.accept()
            except OSError as err:
                print('Error: ', err)
                return False
            except socket.error:
                print('TCP Connect Server Socket Error', socket.error)
                return False
            """
            Hier wordt een specifieke Thread voor de verbonden Client opgestart
            en uitgevoerd
            """
            Thread(target=self.clientListener, args=(client, address)).start()

        self.stop()

    def stop(self):
        """
        Stop TCP Data
        :return:
        """
        self.isListening = False
        self.socket.close()

    def clientListener(self, client, address):
        """
        Deze methode wordt in de Thread uitgevoerd voor een specifieke client
        De ze methode ontvangt connectie en spelers gegevens van de Client
        en valideert of connectie tot het spel mogelijk is. De status wordt
        teruggestuurd naar de client. Dit gebeurt middels een Pickled object.
        :param client:
        :param address:
        :return:
        """
        running = True
        while running:
            try:
                print('Client Thread waiting for data')
                clientData = client.recv(RECVBUF)
                if clientData:
                    connectInfo = self.newClient(address, clientData)
                    client.send(connectInfo.asPickle())
                else:
                    running = False

            except Exception as err:
                print('Message: ', err)
                print('Closing client connection on address %s' % address)
                client.close()
                return False  # exit loop

    @monitorPerformance
    def newClient(self, address, clientData):
        """If client is accepted, send back acceptance notice"""
        connectInfo = ConnectInfo.dePickle(clientData)
        numOfClients = len(self.__clientList.get_clients())
        if numOfClients < self.numberOfClients:
            self.__clientList.add_client(connectInfo)
            connectInfo.set_status(ConnectInfo.ACCEPTED)
            """Even is RED, Odd is BLUE"""
            if numOfClients % 2 != 0:
                connectInfo.set_playerColor('RED')
            else:
                connectInfo.set_playerColor('BLUE')
        else:
            connectInfo.set_status(ConnectInfo.NOTACCEPTED)
        return connectInfo

    def get_clients(self):
        return self.__clientList


class TCPConnectClient(object):
    """
    Deze klasse is de TCP Connect Client klasse. Deze klasse wordt
    gebruikt door de Client om zich te verbinden met de TCP Server
    Deze klasse gebruikt een Pickle om client en spelers gegevens
    te communiceren met de Server.
    """
    @monitorPerformance
    def __init__(self, clientProps):
        self.__connectProps = ConnectInfo(
            clientProps.clientIdentifier,
            clientProps.playerName,
            clientProps.clientUdpPort,
            clientProps.clientIp
        )
        self.__address = (clientProps.serverIp, clientProps.serverTcpPort)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.__address)

    def connect(self):
        self.client.send(self.__connectProps.asPickle())
        response = self.client.recv(RECVBUF)
        connectInfo = ConnectInfo.dePickle(response)
        self.__connectProps = connectInfo

    def close(self):
        self.client.close()

    def isAllowedToConnect(self):
        if self.__connectProps.get_status() == ConnectInfo.NOTACCEPTED:
            return False
        else:
            return True

    def get_playerColor(self):
        return self.__connectProps.get_playerColor()


class UDPClient(object):
    """
    Client Socket Class
    Deze klasse verstuurt de positie van een Client naar de Server
    """
    def __init__(self, addr, playerColor):
        self.server_udp = addr
        self.playerColor = playerColor
        self.server_messages = []


    def send(self, clientId, spritePos):
        clientGameInfo = ClientGameInfo(clientId, spritePos, self.playerColor)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(clientGameInfo.asPickle(), self.server_udp)


class UDPServer(Thread):
    """
    De client UDP Server
    Deze socket luistert naar alle inkomende game data van alle clients
    en broadcast deze informatie weer door naar alle overige clients
    """
    def __init__(self, serverProps):
        Thread.__init__(self)
        self.__address = serverProps.address
        self.__port = serverProps.udpPort
        self.__serversocket = None
        self.__listening = True
        # self.__clientData = {}
        self.__broadcaster = UDPBroadcastSender(serverProps.clientList)
        print("UDP Server initialized")

    def run(self):
        self.__serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__serversocket.bind((self.__address, self.__port))
        print("Listening for game data on UDP port %s" % str(self.__port))
        while self.__listening:
            try:
                data, addr = self.__serversocket.recvfrom(RECVBUF)
            except socket.error:
                print('Server UDP Listener error')
                self.__listening = False
                break

            try:
                """ De-pickle pickled data into class ClientGameInfo """
                clientGameInfo = ClientGameInfo.dePickle(data)
                self.__broadcaster.broadcast(clientGameInfo)
            except Exception as err:
                print("Error in reading data from client: ", err)

        print('closing server socket')
        self.close()

    def close(self):
        self.__listening = False
        self.__serversocket.close()


class UDPBroadcastSender(object):
    """
    UDPBroadcastSender Klasse
    Deze klasse verstuurt alle ClientGameInfo objecten naar
    alle clients die bekend zijn in de clientList
    """
    def __init__(self, clientList):
        self.__clientList = clientList             # Connected Clients
        self.__clientData = ClientDataContainer()  # Clients Game Data

    def broadcast(self, clientGameInfo):
        self.__clientData.addData(clientGameInfo)
        clients = self.__clientList.get_clients()
        for client in clients:
            self.__sendData(client.get_udpPort(), client.get_address())

    def __sendData(self, udpPort, address):
        pickledData = self.__clientData.asPickle()
        sendsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sendsocket.sendto(pickledData, (address, udpPort))


class UDPClientBroadcastReceiver(Thread):
    """
    De UDP server aan de client kant.
    Deze UDP server ontvangt de objecten met de spritelocaties
    """
    def __init__(self, clientProps):
        Thread.__init__(self)
        self.__clientDataContainer = clientProps.clientDataContainer
        self.__address = clientProps.clientIp
        self.__port = clientProps.baseUdpPort
        self.__socket = None
        self.__listening = True
        self.initAndBindFreePort()

    def initAndBindFreePort(self):
        """Initializeer en claim een UDP poort"""
        numOfRetries = 0
        bound = False
        while numOfRetries < 3:
            """
            Probeer de UDP port te claimen. Lukt dat niet omdat deze bezet is, verhoog
            dan het poortnummer met 1 en probeer nogmaals. Doe dit maximaal 3 keer. 
            """
            try:
                self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.__socket.bind((self.__address, self.__port))
                bound = True
                break
            except socket.error as err:
                if err.errno == errno.EADDRINUSE:
                    self.__port += 1
                    numOfRetries += 1
            print('UDP Listening on port %s' % str(self.__port))

        if not bound:
            raise Exception('Error while creating UDP port')


    def run(self):
        """Voer thread code uit"""
        print("Listening for incoming game data on UDP port %s" % str(self.__port))
        while self.__listening:
            try:
                data, addr = self.__socket.recvfrom(RECVBUF)
            except OSError:
                self.close()

            try:
                """ De-pickle pickled data into class ClientDataContainer """
                clientDataContainer = ClientDataContainer.dePickle(data)
                self.__clientDataContainer.set_data(clientDataContainer.get_data())
            except Exception as err:
                print("Error in reading data from client: ", err)

        self.__socket.close()

    def close(self):
        """Stop de socket"""
        self.__listening = False
        self.__socket.close()

    def get_port(self):
        """Getter voor portnummer"""
        return self.__port

