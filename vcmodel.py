"""
Bestandsnaam  : vcmodel.py
Module        : vcmodel
Student       : V. Ciriello
Studentnummer : 800008924
Leerlijn      : Python
Datum:        : september 2018
"""
import pickle
from vcexceptions import JSONDecodableException

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class DePickable(object):
    """
    Deze klasse levert de dePickle methode
    hiermee is een sub-klasse in staat zichzelf
    te instantieren als object vanuit een Pickle
    """
    @staticmethod
    def dePickle(data):
        return pickle.loads(data)


class Pickable(object):
    """
    Deze klasse levert de asPickle methode
    hiermee is een sub-klasse in staat zichzelf
    om te zetten van object naar Pickle
    """
    def asPickle(self):
        return pickle.dumps(self)


class ConnectInfo(Pickable, DePickable):
    """
    Multi-inherence toegepast. Pickable en DePickable
    Pickable: kan zichzelf picklen
    DePickable: kan zichzelf als object terugzetten van een pickle
    Klasse bevat client en spelers connect informatie en de status
    """

    """Class State"""
    NEW = 'NEW'
    ACCEPTED = 'ACCEPTED'
    NOTACCEPTED = 'NOTACCEPTED'

    def __init__(self, clientIdentifier, playerName, udpPort, address):
        self.__status = self.NEW
        self.__address = address
        self.__udpPort = udpPort
        self.__playerName = playerName
        self.__clientIdentifier = clientIdentifier
        self.__playerColor = None  # wordt door de server bepaald

    def get_status(self):
        return self.__status

    def set_status(self, status):
        self.__status = status

    def get_playerName(self):
        return self.__playerName

    def get_clientIdentifier(self):
        return self.__clientIdentifier

    def get_udpPort(self):
        return self.__udpPort

    def get_address(self):
        return self.__address

    def get_playerColor(self):
        return self.__playerColor

    def set_playerColor(self, color):
        self.__playerColor = color


class ClientGameInfo(Pickable, DePickable):
    """
    Multi-inherence toegepast. Pickable en DePickable
    Pickable: kan zichzelf picklen
    DePickable: kan zichzelf als object terugzetten van een pickle
    Klasse bevat de gameinformatie. Bevat de positie van de sprites
    van een specifieke client (clientId).
    """
    def __init__(self, clientId, spritePos, color):
        self.__spriteColor = color
        self.__clientId = clientId
        self.__spritePos = spritePos

    def get_clientId(self):
        return self.__clientId

    def get_spritePos(self):
        return self.__spritePos


class SpritePos(object):
    """
    Sprite positie and hoek (Angle) Klasse
    """
    def __init__(self, center, angle):
        self.__center = center
        self.__angle = angle

    def get_angle(self):
        return self.__angle

    def get_center(self):
        return self.__center


class ClientList(object):
    """
    Bevat een lijst van alle verbonden clients
    """
    def __init__(self):
        self.__clients = []

    def get_clients(self):
        return self.__clients

    def add_client(self, client):
        self.__clients.append(client)
        return self.__clients

    def remove_client(self, client):
        self.__clients.remove(client)
        return self.__clients


class ClientDataContainer(Pickable, DePickable):
    """
    Bevat de positie gegevens van alle clients
    """
    def __init__(self):
        self.__data = {}

    def addData(self, clientGameInfo):
        clientId = clientGameInfo.get_clientId()
        self.__data[clientId] = clientGameInfo

    def clearData(self):
        self.__data = {}

    def set_data(self, data):
        self.__data = data

    def get_data(self):
        return self.__data


class JSONDecodable(object):
    """
    Interface voor het implementeren van een JSONDecodable object
    een object wat zichzelf kan initieren met JSON data
    """
    def decode(self, jsonData):
        pass


class ClientConfig(JSONDecodable):
    """
    De configuratie klasse voor de client. Kan zichzelf initieren
    aan de hand van JSON data
    """
    def __init__(self):
        self.baseUDPPort = None
        self.clientIp = None
        self.serverIp = None
        self.tcpServerPort = None
        self.udpServerPort = None

    def decode(self, jsonData):
        try:
            self.baseUDPPort = jsonData['baseUDPPort']
            self.clientIp = jsonData['clientIp']
            self.serverIp = jsonData['serverIp']
            self.tcpServerPort = jsonData['tcpServerPort']
            self.udpServerPort = jsonData['udpServerPort']

        except KeyError as k:
            raise JSONDecodableException('Fout in het zoeken van config parameter {0}'.format(k.args))

        except ValueError as v:
            raise JSONDecodableException('Fout in het parsen van de JSON waarde: {0}'.format(v.args))

        return self


class ServerConfig(JSONDecodable):
    """
    De configuratie klasse voor de server. Kan zichzelf initieren
    aan de hand van JSON data
    """
    def __init__(self):
        self.address = None
        self.tcpPort = None
        self.udpPort = None

    def decode(self, jsonData):
        try:
            self.address = jsonData['address']
            self.tcpPort = jsonData['tcpPort']
            self.udpPort = jsonData['udpPort']

        except KeyError as k:
            raise JSONDecodableException('Fout in het zoeken van config parameter {0}'.format(k.args))

        except ValueError as v:
            raise JSONDecodableException('Fout in het parsen van de JSON waarde: {0}'.format(v.args))

        return self


class ServerProps(object):
    """
    Server Properties Klasse
    """
    def __init__(self, clientList, lock, address, udpPort, tcpPort, numberOfClientsToAccept):
        self.clientList = clientList
        self.lock = lock
        self.address = address
        self.udpPort = udpPort
        self.tcpPort = tcpPort
        self.numberOfClientsToAccept = numberOfClientsToAccept


class ClientProps(object):
    """
    Client Properties Klasse
    """
    def __init__(self, clientIdentifier, baseUdpPort, clientIp, clientUdpPort, serverIp,
                 serverTcpPort, serverUdpPort, clientDataContainer, playerName, playerColor):
        self.clientIdentifier = clientIdentifier
        self.baseUdpPort = baseUdpPort
        self.clientIp = clientIp
        self.clientUdpPort = clientUdpPort
        self.serverIp = serverIp
        self.serverTcpPort = serverTcpPort
        self.serverUpdPort = serverUdpPort
        self.clientDataContainer = clientDataContainer
        self.playerName = playerName
        self.playerColor = playerColor