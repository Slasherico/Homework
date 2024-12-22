import pygame
from time import sleep
import random

from pygame.locals import *

# Constants
SCREEN_WIDTH = 800  # Adjusted for landscape
SCREEN_HEIGHT = 600  # Adjusted for landscape
COYOTE_SPAWN_RATE = 30  # Frames until a new coyote spawns
BULLET_SPEED = 10
PLAYER_SPEED = 15
PLAYER_WIDTH = 50  # Width of the sheriff
PLAYER_HEIGHT = 50  # Height of the sheriff
COYOTE_WIDTH = 50  # Width of the coyote
COYOTE_HEIGHT = 50  # Height of the coyote
BULLET_WIDTH = 10  # Width of the bullet
BULLET_HEIGHT = 20  # Height of the bullet
COYOTE_SPEED = 2  # Speed of the coyotes

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.player_x = 200
        self.player_y = 200
        self.keys = [False, False, False, False]
        self.running = True
        self.score = 0
        self.frames = 0
        self.game_over = False
        
        # Load and resize images
        self.player = pygame.image.load("images/sheriff.png")
        self.player = pygame.transform.scale(self.player, (PLAYER_WIDTH, PLAYER_HEIGHT))
        
        self.coyote_image = pygame.image.load("images/coyote.png")
        self.coyote_image = pygame.transform.scale(self.coyote_image, (COYOTE_WIDTH, COYOTE_HEIGHT))
        
        self.bullet_image = pygame.image.load("images/bullet.png")
        self.bullet_image = pygame.transform.scale(self.bullet_image, (BULLET_WIDTH, BULLET_HEIGHT))
        
        self.background = pygame.image.load("images/background.png")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Scale background
        
        # Load sounds
        self.shoot_sound = pygame.mixer.Sound("sounds/shoot.wav")
        self.hit_sound = pygame.mixer.Sound("sounds/hit.wav")
        self.groan_sound = pygame.mixer.Sound("sounds/groan.wav")  # Load groaning sound
        
        self.bullets = []
        self.coyotes = []
        self.spawn_coyote()

    def spawn_coyote(self):
        while True:
            x = random.randint(0, SCREEN_WIDTH - COYOTE_WIDTH)  # Adjust for coyote width
            y = random.randint(0, SCREEN_HEIGHT - COYOTE_HEIGHT)  # Adjust for coyote height
            # Ensure coyote does not spawn under the player
            if not (self.player_x < x < self.player_x + PLAYER_WIDTH and self.player_y < y < self.player_y + PLAYER_HEIGHT):
                self.coyotes.append([x, y])
                break

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == K_UP:
                    self.keys[0] = True
                elif event.key == K_DOWN:
                    self.keys[1] = True
                elif event.key == K_LEFT:
                    self.keys[2] = True
                elif event.key == K_RIGHT:
                    self.keys[3] = True
                elif event.key == K_SPACE:
                    self.shoot()
            if event.type == pygame.KEYUP:
                if event.key == K_UP:
                    self.keys[0] = False
                if event.key == K_DOWN:
                    self.keys[1] = False
                if event.key == K_LEFT:
                    self.keys[2] = False
                if event.key == K_RIGHT:
                    self.keys[3] = False

    def shoot(self):
        bullet_x = self.player_x + 20  # Adjust bullet position based on sheriff's position
        bullet_y = self.player_y
        self.bullets.append([bullet_x, bullet_y])
        self.shoot_sound.play()  # Play shoot sound

    def player_pos(self):
        if self.keys[0] and self.player_y > 0:
            self.player_y -= PLAYER_SPEED
        if self.keys[1] and self.player_y < SCREEN_HEIGHT - PLAYER_HEIGHT:  # Adjust for player height
            self.player_y += PLAYER_SPEED
        if self.keys[2] and self.player_x > 0:
            self.player_x -= PLAYER_SPEED
        if self.keys[3] and self.player_x < SCREEN_WIDTH - PLAYER_WIDTH:  # Adjust for player width
            self.player_x += PLAYER_SPEED

        # Move bullets
        for bullet in self.bullets:
            bullet[1] -= BULLET_SPEED  # Move bullet upwards
        self.bullets = [bullet for bullet in self.bullets if bullet[1] > 0]  # Remove off-screen bullets

        # Move coyotes towards the player
        for coyote in self.coyotes:
            if coyote[0] < self.player_x:
                coyote[0] += COYOTE_SPEED
            elif coyote[0] > self.player_x:
                coyote[0] -= COYOTE_SPEED
            if coyote[1] < self.player_y:
                coyote[1] += COYOTE_SPEED
            elif coyote[1] > self.player_y:
                coyote[1] -= COYOTE_SPEED

        # Check for collisions
        self.check_collisions()

    def check_collisions(self):
        for bullet in self.bullets:
            for coyote in self.coyotes:
                if (bullet[0] in range(coyote[0], coyote[0] + COYOTE_WIDTH) and  # Adjust for coyote width
                    bullet[1] in range(coyote[1], coyote[1] + COYOTE_HEIGHT)):  # Adjust for coyote height
                    self.coyotes.remove(coyote)
                    self.bullets.remove(bullet)
                    self.score += 1
                    self.hit_sound.play()  # Play hit sound
                    break

        # Check if the player collides with any coyote
        for coyote in self.coyotes:
            if (self.player_x in range(coyote[0], coyote[0] + COYOTE_WIDTH) and  # Adjust for coyote width
                self.player_y in range(coyote[1], coyote[1] + COYOTE_HEIGHT)):  # Adjust for coyote height
                self.game_over = True
                self.groan_sound.play()  # Play groaning sound
                self.mute_all_sounds()  # Mute all sounds
                self.freeze_game()  # Freeze the game

    def mute_all_sounds(self):
        # Stop all sound effects
        self.shoot_sound.stop()
        self.hit_sound.stop()
        self.groan_sound.stop()

    def freeze_game(self):
        # Freeze the game for a short duration
        sleep(2)  # Adjust the duration as needed

    def display(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.player, (self.player_x, self.player_y))

        # Draw bullets
        for bullet in self.bullets:
            self.screen.blit(self.bullet_image, (bullet[0], bullet[1]))

        # Draw coyotes
        for coyote in self.coyotes:
            self.screen.blit(self.coyote_image, (coyote[0], coyote[1]))

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        # Display game over screen if applicable
        if self.game_over:
            self.display_game_over()

        pygame.display.flip()

    def display_game_over(self):
        font = pygame.font.Font(None, 72)
        game_over_text = font.render('You Died', True, (255, 0, 0))
        score_text = font.render(f'Coyotes Killed: {self.score}', True, (0, 0, 0))  # Change text color to black
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 10))

    def run(self):
        while self.running:
            self.handle_events()
            if not self.game_over:
                self.player_pos()
                self.display()
                self.frames += 1
                
                # Spawn a new coyote every COYOTE_SPAWN_RATE frames
                if self.frames % COYOTE_SPAWN_RATE == 0:
                    self.spawn_coyote()

                sleep(0.05)
            else:
                sleep(0.1)  # Slow down the loop when game is over

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()