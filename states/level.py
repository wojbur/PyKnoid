from turtle import st
import pygame
from pathlib import PurePath
from math import cos, sin
from math import pi as PI
from csv import reader

from states.state import State


vector = pygame.math.Vector2
# from states.main_menu import MainMenu

class GameLevel(State):
    def __init__(self, game):
        State.__init__(self, game)

        # Define sprite groups
        self.player_group = pygame.sprite.Group()
        self.ball_group = pygame.sprite.Group()
        self.block_group = pygame.sprite.Group()
        self.stage = 2

        # Initialize player and ball objects
        self.player = Player(self.game, self)
        self.ball = Ball(self.game, self, self.player.rect.centerx, self.player.rect.top-3, PI)
        # self.block = Block(self.game, self, 40, 80)

        # Load level layout
        with open(PurePath('stages', 'standard_set.csv')) as file:
            csv_reader = reader(file, delimiter=";")
            stage_layouts = list(csv_reader)
            start_row = self.stage + (self.stage-1)*20
            end_row = start_row + 20
            self.stage_layout = stage_layouts[start_row:end_row]
        
        # Create blocks grid
        for i in range(len(self.stage_layout)):
            for j in range(len(self.stage_layout[i])):
                if self.stage_layout[i][j]:
                    Block(self.game, self, self.stage_layout[i][j], 40+j*60, 80+i*30)

    
    def update(self, delta_time, keys):
        if keys['escape']:
            self.exit_state()
        self.player.update(delta_time, keys)
        self.ball.update(delta_time, keys)
        self.game.reset_keys()

    def render(self, surface):
        surface.fill((0, 0, 0))
        self.player.render(surface)
        self.ball.render(surface)
        self.block_group.draw(surface)

class Player(pygame.sprite.Sprite):
    def __init__(self, game, level):
        super().__init__()
        self.game = game
        self.level = level

        self.image = pygame.image.load(PurePath(game.sprites_dir, 'player', 'paddle.png'))
        self.rect = self.image.get_rect()
        self.rect.centerx = game.GAME_WIDTH/2
        self.rect.bottom = game.GAME_HEIGHT - 14

        self.level.player_group.add(self)

        self.width = self.rect[2]
    
    def update(self, delta_time, keys):
        # Scale mouse position to the display surface
        mouse_x = pygame.mouse.get_pos()[0] * (self.game.GAME_WIDTH / self.game.SCREEN_WIDTH)
        self.rect.centerx = mouse_x
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.game.GAME_WIDTH:
            self.rect.right = self.game.GAME_WIDTH

    def render(self, surface):
        surface.blit(self.image, self.rect)
        

class Ball(pygame.sprite.Sprite):
    def __init__(self, game, level, x, y, angle):
        super().__init__()
        self.game = game
        self.level = level

        self.image = pygame.image.load(PurePath(game.sprites_dir, 'ball', 'ball.png'))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 400
        self.angle = angle

        # Kinematic vectors
        self.position = vector(x, y)
        self.velocity = vector(sin(self.angle)*self.speed, cos(self.angle)*self.speed)
    
    def update(self, delta_time, keys):
        self.position += self.velocity * delta_time
        self.rect.center = self.position
        self.bounce()
        self.player_collide()
        self.block_collide()

    def render(self, surface):
        surface.blit(self.image, self.rect)
    
    def player_collide(self):
        if pygame.sprite.spritecollide(self, self.level.player_group, False):
            ball_x = self.rect.centerx
            player_x = self.level.player.rect.centerx
            player_width = self.level.player.width

            # Set new ball angle depending on collide position - the closer to player center the more vertical the angle
            # The 0.8 is there to ensure min bounce angle is 18deg so that the ball don't bounce too horizontally
            self.angle = PI + 0.8 * PI * (player_x - ball_x)/player_width

            # Set new ball velocity
            self.velocity[1] *= -1
            self.velocity = vector(sin(self.angle)*self.speed, cos(self.angle)*self.speed)
    
    def block_collide(self):
        collision_tolerance = 4
        collided_block = pygame.sprite.spritecollide(self, self.level.block_group, True)
        if collided_block:

            # Collision from the bottom
            if abs(collided_block[0].rect.bottom - self.rect.top) < collision_tolerance and self.velocity[1] < 0:
                print('bottom')
                self.velocity[1] *= -1
            # Collision from the top
            if abs(collided_block[0].rect.top - self.rect.bottom) < collision_tolerance and self.velocity[1] > 0:
                print('top')
                self.velocity[1] *= -1
            # Collision from the left
            if abs(collided_block[0].rect.left - self.rect.right) < collision_tolerance and self.velocity[0] > 0:
                print('left')
                self.velocity[0] *= -1
            # Collision from the right
            if abs(collided_block[0].rect.right - self.rect.left) < collision_tolerance and self.velocity[0] < 0:
                print('right')
                self.velocity[0] *= -1
            

    def bounce(self):
        if self.rect.right >= self.game.GAME_WIDTH or self.rect.left <= 0:
            self.velocity[0] *= -1
        if self.rect.top <= 0:
            self.velocity[1] *= -1


class Block(pygame.sprite.Sprite):
    def __init__(self, game, level, code, x, y):
        super().__init__()
        self.game = game
        self.level = level
        self.code = code

        self.image = pygame.image.load(PurePath(game.sprites_dir, 'blocks', f'{self.code}.png'))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.level.block_group.add(self)

    def render(self, surface):
        surface.blit(self.image, self.rect)


class Powerup():
    pass
