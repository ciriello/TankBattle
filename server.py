"""
Bestandsnaam  : server.py
Naam          : TankBattleGameServer
Student       : V. Ciriello
Studentnummer : 800008924
Leerlijn      : Python
Datum:        : september 2018
"""
from threading import Lock
from vcnetwork import TCPConnectServerThreaded, UDPServer
from vcmodel import ServerProps, ClientList, ServerConfig
import time
import vcutils

"""
Start udp server to receive client broadcasts
:param address: IP to listen on (server)
:param port: PORT to listen on (server
:return: void
"""

CONFIGF = 'config_server.json'

if __name__ == "__main__":
    print('Server is starting')
    lock = Lock()
    """
        Laden van het configuratie bestand voor de Server
        Als het laden niet lukt zal het programma stoppen
        omdat het zonder configuratie gegevens niet kan
        functioneren.
        """
    try:
        configuration = vcutils.parseConfig(CONFIGF, ServerConfig)
    except vcutils.ConfigFileException as err:
        print(err)
        exit(1)

    clientList = ClientList()
    numberOfClientsToAccept = 2  # constante waarde
    serverProps = ServerProps(
        clientList,
        lock,
        configuration.address,
        configuration.udpPort,
        configuration.tcpPort,
        numberOfClientsToAccept
    )

    """
    Startup the UDP socket server for client to broadcast game data to
    """
    udpserver = UDPServer(serverProps)
    udpserver.start()

    """
    Startup the TCP socket server for client to connect
    """
    tcpServer = TCPConnectServerThreaded(serverProps)
    tcpServer.start()

    """
    Waiting for all sockets to start up before continuing
    """
    time.sleep(1)
    print('Ready to accept control commands')

    running = True
    while running:
        try:
            cmd = input("cmd >")
            if cmd == 'help':
                print('Command available:\n')
                print('quit [shutdown server]')
                print('list [list connected clients]')
                print('\n')

            elif cmd == 'list':
                print(tcpServer.get_clients())

            elif cmd == "quit":
                print('Server is closing connections...\n')
                break

            else:
                print('Unknown command type "help" for more')

        except KeyboardInterrupt:
            running = False
            break

    print('stopping...')
    udpserver.close()
    udpserver.join()
    tcpServer.stop()
    print('Shutdown completed')
