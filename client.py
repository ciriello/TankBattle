"""
Bestandsnaam  : client.py
Naam          : TankBattleGameClient
Student       : V. Ciriello
Studentnummer : 800008924
Leerlijn      : Python
Datum:        : september 2018
"""
import uuid
import vcutils
from vcnetwork import TCPConnectClient, UDPClientBroadcastReceiver
from vcgame import Game
from vcmodel import ClientDataContainer, ClientProps, ClientConfig

CONFIGF = 'config_client.json'

if __name__ == '__main__':
    """
    The Tank Battle Client
    """

    """
    Laden van het configuratie bestand voor de Client
    Als het laden niet lukt zal het programma stoppen
    omdat het zonder configuratie gegevens niet kan
    functioneren.
    """
    try:
        configuration = vcutils.parseConfig(CONFIGF, ClientConfig)
    except vcutils.ConfigFileException as err:
        print(err)
        exit(1)

    """
    Genereer een unique ID voor de Client instantie.
    Wordt gebruikt om de client te identificeren als
    er game data informatie over het netwerk binnen
    komt.
    """
    clientId = str(uuid.uuid4())

    """
    Spelersnaam en kleur
    De kleur van de speler wordt bepaald door de server
    De eerste client krijgt de kleur Blauw, De tweede Rood
    """
    playerName = 'Mister X'
    playerColor = None  # wordt door de server bepaald

    """
    Client Data Container
    bevat alle game data van de players/clients. Dat wil zeggen
    De positie en hoek van de tegenstanders.
    """
    clientDataContainer = ClientDataContainer()
    UDPCLIENT_PORT = 0  # Wordt later toegewezen bij de initiatie van de UDPClientBroadcastReceiver

    """
    De instelling van de client worden in een specifieke klasse
    opgeslagen
    """
    clientProps = ClientProps(
        clientId,
        configuration.baseUDPPort,
        configuration.clientIp,
        UDPCLIENT_PORT,
        configuration.serverIp,
        configuration.tcpServerPort,
        configuration.udpServerPort,
        clientDataContainer,
        playerName,
        playerColor
    )

    """Start de UDP listener om gamedata te ontvangen van de server"""
    udpListener = UDPClientBroadcastReceiver(clientProps)
    clientProps.clientUdpPort = udpListener.get_port()  # udppoort wordt hier toegewezen
    udpListener.start()

    """Start de TCP connectie om deze Client aan te melden bij de Server"""
    tcpClient = TCPConnectClient(clientProps)
    tcpClient.connect()
    clientProps.playerColor = tcpClient.get_playerColor()

    """Staat de server connectie toe. Dan SPELEN maar!!!"""
    if tcpClient.isAllowedToConnect():
        theGame = Game(clientProps, udpListener)
        theGame.run()
        udpListener.close()
        tcpClient.close()
    else:
        print('Sorry maximum number of clients reached')
