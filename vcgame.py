"""
Bestandsnaam  : vcgame.py
Module        : vcgame
Student       : V. Ciriello
Studentnummer : 800008924
Leerlijn      : Python
Datum:        : september 2018
"""
import pygame
import os
from vcmodel import SCREEN_HEIGHT, SCREEN_WIDTH
from vcnetwork import UDPClient
from vcsprites import TankSprite


class Game(object):
    def __init__(self, clientProps, udpListener):
        self.__serverIp = clientProps.serverIp
        self.__serverUdpPort = clientProps.serverUpdPort
        self.__clientDataContainer = clientProps.clientDataContainer
        self.__clientId = clientProps.clientIdentifier
        self.__color = clientProps.playerColor
        self.__udpListener = udpListener

        pygame.init()
        pygame.display.set_caption("...Novi Tank Battle...")  # sets window title
        pygame.key.set_repeat(1, 60)
        self.width, self.height = SCREEN_WIDTH, SCREEN_HEIGHT  # window dimensions
        self.offset = self.height - self.width  # vertical space at top of window
        self.screen = pygame.display.set_mode((self.width, self.height))  # creates window
        self.font = pygame.font.Font(None, 72)
        self.clock = pygame.time.Clock()  # used to regulate FPS

        """
        Load Sprite Images
        """
        self.IMAGE_BLUE = pygame.image.load(os.path.join('images', 'blue-small.png')).convert_alpha()
        self.IMAGE_RED = pygame.image.load(os.path.join('images', 'red-small.png')).convert_alpha()
        self.IMAGE_BULLET = pygame.image.load(os.path.join('images', 'tank-bullet.png')).convert_alpha()
        self.IMAGE_BALL = pygame.image.load(os.path.join('images', 'canon-ball-small.png')).convert_alpha()
        self.BLACK = (150, 150, 150)

        """
        Initialize UDP Client to send game data to server
        """
        self.client = UDPClient((self.__serverIp, self.__serverUdpPort), self.__color)

        # create a sprite list for the game
        self.sprite_list = pygame.sprite.Group()

        # create a tegenstander tank
        self.tegenstander = None
        if self.__color == 'RED':
            self.__tankColor = self.IMAGE_RED
            self.__opponentTankColor = self.IMAGE_BLUE
        else:
            self.__tankColor = self.IMAGE_BLUE
            self.__opponentTankColor = self.IMAGE_RED

    def updateOpponentSprites(self):
        gameData = self.__clientDataContainer.get_data()
        for key, clientGameInfo in gameData.items():
            if key != self.__clientId:
                spritePos = clientGameInfo.get_spritePos()
                if self.tegenstander == None:
                    self.tegenstander = TankSprite(spritePos.get_center(), self.__opponentTankColor, self.IMAGE_BALL)
                    self.tegenstander.set_angle(spritePos.get_angle())
                    self.sprite_list.add(self.tegenstander)
                else:
                    self.tegenstander.set_angle(spritePos.get_angle())
                    self.tegenstander.set_center(spritePos.get_center())

    def processKeyPress(self, keys, tank):
        if keys[pygame.K_LEFT]:
            tank.dec_angle()
        if keys[pygame.K_RIGHT]:
            tank.inc_angle()
        if keys[pygame.K_UP]:
            tank.inc_speed()
        if keys[pygame.K_DOWN]:
            tank.dec_speed()
        if keys[pygame.K_b]:
            tank.breaks()
        if keys[pygame.K_SPACE]:
            tank.shoot(self.sprite_list)

    def processGameEvent(self, events):
        for event in events:
            if event.type == pygame.QUIT:  # close button pressed
                return False
        return True

    def run(self):
        """
        Main Game Loop
        """
        # create the players tank
        tank = TankSprite((100, 100), self.__tankColor, self.IMAGE_BALL)

        # add players tank to sprite list
        self.sprite_list.add(tank)
        oldPos = {}

        running = True
        while running:
            """
            Valideer de toetsaanslagen voor de besturing van de tank e.d.
            """
            keys = pygame.key.get_pressed()
            self.processKeyPress(keys, tank)

            """
            Valideer de game event en het afsluiten e.d. van het programma
            """
            running = self.processGameEvent(pygame.event.get())


            """
            Update Screen Sprites etc, etc.
            """
            self.updateOpponentSprites()
            self.sprite_list.update()
            self.screen.fill(self.BLACK);

            """
            Send sprite pos to server
            """
            myPos = tank.get_state()
            if not oldPos == myPos:
                self.client.send(self.__clientId, myPos)
            else:
                print('positie niet veranderd')

            oldPos = myPos


            """
            Draw Sprite List
            """
            self.sprite_list.draw(self.screen)

            """
            Flip Screen and Regulate FPS
            """
            pygame.display.flip()  # flips display
            self.clock.tick(60)  # regulates FPS 60fps

