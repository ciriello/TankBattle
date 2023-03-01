"""
Bestandsnaam  : vcsprite.py
Module        : vcsprite
Student       : V. Ciriello
Studentnummer : 800008924
Leerlijn      : Python
Datum:        : september 2018
"""
import pygame
import math
from pygame.math import Vector2
from vcmodel import SCREEN_HEIGHT, SCREEN_WIDTH, SpritePos


def calculate_new_xy(speed, angle):
    """ function to calculate new x and y sprite speed """
    angle_in_radians = math.radians(angle)
    new_speed_x = speed * math.cos(angle_in_radians)
    new_speed_y = speed * math.sin(angle_in_radians)
    return new_speed_x, new_speed_y


class BulletSprite(pygame.sprite.Sprite):
    """
    Bullet Sprite Class
    """
    BULLET_SPEED = 15

    def __init__(self, pos, angle, image, bulletList):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.bulletList = bulletList

        # ref to image
        self.orig_image = self.image
        self.pos = Vector2(pos)  # The original center position/pivot point.
        self.offset = Vector2(0, 0)  # We shift the sprite 50 px to the right.
        self.angle = angle
        self.speed = BulletSprite.BULLET_SPEED

        self.pos_x = pos[0]
        self.pos_y = pos[1]
        x, y = calculate_new_xy(self.speed, self.angle)
        self.speed_x = x
        self.speed_y = y
        self.rotate()

    def update(self):
        x, y = calculate_new_xy(self.speed, self.angle)
        self.pos_x += x
        self.pos_y += y
        self.validate_speed()
        self.rect.center = (self.pos_x, self.pos_y)

    def validate_speed(self):
        if self.pos_x >= SCREEN_WIDTH or self.pos_x <= 0:
            self.speed = 0

        if self.pos_y >= SCREEN_HEIGHT or self.pos_y <= 0:
            self.speed = 0

        if self.speed == 0:
            self.bulletList.remove(self)

    def rotate(self):
        """Rotate the image of the sprite around a pivot point."""
        self.image = pygame.transform.rotozoom(self.orig_image, -self.angle, 1)
        offset_rotated = self.offset.rotate(self.angle)
        self.rect = self.image.get_rect(center=self.pos + offset_rotated)


class TankSprite(pygame.sprite.Sprite):
    """
    Tank Sprite Class
    """
    SPEED_STEP = 0.1
    ANGLE_STEP = 4
    MAX_SPEED  = 5
    SHOOT_INTERVAL = 30

    def __init__(self, pos, image, ballImage):
        super().__init__()
        self.image = image
        self.ballImage = ballImage
        self.rect = self.image.get_rect(center=pos)

        # ref to image
        self.orig_image = self.image
        self.pos = Vector2(pos)  # The original center position/pivot point.
        self.offset = Vector2(0, 0)  # We shift the sprite 50 px to the right.
        self.angle = 0
        self.speed = 0

        self.pos_x = pos[0]
        self.pos_y = pos[1]
        x, y = calculate_new_xy(self.speed, self.angle)
        self.speed_x = x
        self.speed_y = y
        self.shoot_threshold = TankSprite.SHOOT_INTERVAL

    def set_center(self, center):
        self.pos_x = center[0]
        self.pos_y = center[1]

    def set_angle(self, angle):
        self.angle = angle

    def dec_angle(self):
        self.angle -= TankSprite.ANGLE_STEP

    def inc_angle(self):
        self.angle += TankSprite.ANGLE_STEP

    def inc_speed(self):
        self.speed += TankSprite.SPEED_STEP
        if self.speed >= TankSprite.MAX_SPEED:
            self.speed = TankSprite.MAX_SPEED

    def dec_speed(self):
        self.speed -= TankSprite.SPEED_STEP
        if self.speed <= -TankSprite.MAX_SPEED:
            self.speed = -TankSprite.MAX_SPEED

    def breaks(self):
        self.speed = self.speed / 1.2
        if math.fabs(self.speed) <= 0.1:
            self.speed = 0

    def shoot(self, bulletList):
        if self.shoot_threshold < TankSprite.SHOOT_INTERVAL:
            return

        self.shoot_threshold = 0
        pos = self.pos_x, self.pos_y
        tank_bullet = BulletSprite(pos, self.angle, self.ballImage, bulletList)
        bulletList.add(tank_bullet)

    def update(self):
        x, y = calculate_new_xy(self.speed, self.angle)
        self.speed_x = x
        self.speed_y = y
        self.pos_x += self.speed_x
        self.pos_y += self.speed_y
        self.rotate()
        self.validate_speed()
        self.shootTreshold()
        self.rect.center = (self.pos_x, self.pos_y)

    def validate_speed(self):
        if self.pos_x >= SCREEN_WIDTH or self.pos_x <= 0:
            self.speed = 0
            if self.pos_x <= 0:
                self.pos_x = 0
            elif self.pos_x >= SCREEN_WIDTH:
                self.pos_x = SCREEN_WIDTH

        if self.pos_y >= SCREEN_HEIGHT or self.pos_y <= 0:
            self.speed = 0
            if self.pos_y <= 0:
                self.pos_y = 0
            elif self.pos_y >= SCREEN_HEIGHT:
                self.pos_y = SCREEN_HEIGHT

    def shootTreshold(self):
        self.shoot_threshold += 1
        if self.shoot_threshold >= TankSprite.SHOOT_INTERVAL:
            self.shoot_threshold = TankSprite.SHOOT_INTERVAL

    def rotate(self):
        """Rotate the image of the sprite around a pivot point."""
        # Rotate the image.
        self.image = pygame.transform.rotozoom(self.orig_image, -self.angle, 1)
        # Rotate the offset vector.
        offset_rotated = self.offset.rotate(self.angle)
        # Create a new rect with the center of the sprite + the offset.
        self.rect = self.image.get_rect(center=self.pos + offset_rotated)

    def get_state(self):
        """Will return a JSON state object to send to server to update other clients"""
        center = self.rect.center
        angle = self.angle
        state = {
            center: center,
            angle: angle
        }
        aState = SpritePos(center, angle)
        # print(aState.center, aState.angle)
        return aState
