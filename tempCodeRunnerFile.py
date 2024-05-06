import pygame
import os
import sys
import random
import time


class GameObject:
    def __init__(self, position, scale):
        self.rect = pygame.Rect(position[0], position[1], scale[0], scale[1])


class Character(GameObject):
    def __init__(self, position=(50, 50)):
        super().__init__(position, (110, 110))
        self.original_image = pygame.image.load("./assets/palyer-1.png")
        self.image = pygame.transform.scale(self.original_image, self.rect.size)
        self.has_key = False

    def move(self, dx, dy, walls, screen_width, screen_height, camera_x, camera_y):
        old_x, old_y = self.rect.x, self.rect.y

        self.rect.x += dx
        self.rect.y += dy

        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self.rect.x, self.rect.y = old_x, old_y
                break

        self.rect.x = max(0, min(self.rect.x, screen_width - self.rect.width - camera_x))
        self.rect.y = max(0, min(self.rect.y, screen_height - self.rect.height - camera_y))

    def collect_key(self, keys):
        for key in keys:
            if self.rect.colliderect(key.rect):
                key.collected = True
                self.has_key = True
                keys.remove(key)
                break


class Wall(GameObject):
    def __init__(self, pos, desc):
        if desc == "horizontal":
            image_path = "./assets/horizontal-2.png"
        elif desc == "vertical":
            image_path = "./assets/vertikal-2.png"
        super().__init__(pos, (120, 120))
        self.original_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.original_image, self.rect.size)


class Key(GameObject):
    def __init__(self, pos):
        super().__init__(pos, (60, 60))
        self.original_image = pygame.image.load("./assets/kunci.png")
        self.image = pygame.transform.scale(self.original_image, self.rect.size)
        self.collected = False


class Door(GameObject):
    def __init__(self, pos):
        super().__init__(pos, (60, 60))


class Screen:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.font_title = pygame.font.Font("./assets/fonts/Gameplay.ttf", 60)
        self.font_info = pygame.font.Font(None, 48)

    def draw_initial_screen(self, game_status=None, score=None):
        self.screen.fill((47, 79, 79))
        title_text = self.font_title.render("Telusur game", True, (210, 180, 140))
        text_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title_text, text_rect)

        if game_status == "success" and score is not None:
            result_text = self.font_info.render(f"Selamat! Skor Anda: {score}", True, (255, 255, 255))
            result_rect = result_text.get_rect(center=(self.screen.get_width() // 2, 200))
            self.screen.blit(result_text, result_rect)
        elif game_status == "fail":
            result_text = self.font_info.render("Game Over!", True, (255, 255, 255))
            result_rect = result_text.get_rect(center=(self.screen.get_width() // 2, 200))
            self.screen.blit(result_text, result_rect)

        start_button = pygame.Rect(300, 350, 350, 70)
        pygame.draw.rect(self.screen, (139, 69, 19), start_button)
        start_text = self.font_title.render("Main", True, (255, 255, 255))
        text_rect = start_text.get_rect(center=start_button.center)
        self.screen.blit(start_text, text_rect)

        exit_button = pygame.Rect(300, 450, 350, 70)
        pygame.draw.rect(self.screen, (139, 69, 19), exit_button)
        exit_text = self.font_title.render("Keluar", True, (255, 255, 255))
        text_rect = exit_text.get_rect(center=exit_button.center)
        self.screen.blit(exit_text, text_rect)

        pygame.display.flip()
        return start_button, exit_button

    def draw_result_screen(self, message, score):
        self.screen.fill((47, 79, 79))
        title_text = self.font_title.render(f"{message} Skor Anda: {score}", True, (210, 180, 140))
        text_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(title_text, text_rect)

        play_again_button = pygame.Rect(250, 350, 450, 70)
        pygame.draw.rect(self.screen, (139, 69, 19), play_again_button)
        play_again_text = self.font_title.render("Main Lagi", True, (255, 255, 255))
        text_rect = play_again_text.get_rect(center=play_again_button.center)
        self.screen.blit(play_again_text, text_rect)

        exit_button = pygame.Rect(300, 450, 350, 70)
        pygame.draw.rect(self.screen, (139, 69, 19), exit_button)
        exit_text = self.font_title.render("Keluar", True, (255, 255, 255))
        text_rect = exit_text.get_rect(center=exit_button.center)
        self.screen.blit(exit_text, text_rect)

        pygame.display.flip()
        return play_again_button, exit_button

    def draw_timer(self, time_left):
        timer_text = self.font_info.render(f"Waktu: {time_left}", True, (255, 255, 255))
        self.screen.blit(timer_text, (10, 10))


class Game:
    def __init__(self):
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.display.set_caption("Labirin PBO")

        self.screen = Screen()
        self.clock = pygame.time.Clock()
        self.surface = pygame.image.load("./assets/surface-soil.png")
        self.time_limit = 60  # Time limit for the game in seconds

        self.obstacles = [
            [" HHHHHHHHHHHHHHHHHHHV",
             "                    V",
             "V HHHHHHHHHHHHHHHHH V",
             "V                   V",
             "V                   V",
             "V HHV  HHHHHHHHHHHV V",
             "V   V             V V",
             "V   VK            H V",
             "V   HHV HHHHV       V",
             "V     H     HHHHHHH H",
             "V                    E",
             "VVVVVVVVVVVVVVVVVVVVV"],

            [" HHHHHHHHHHHHHHHHHHHV",
             "                    V",
             "V HHHHHHHHHHHHHHHHH V",
             "V                   V",
             "V HHHHHHHHHHHHHHHHH V",
             "V                   V",
             "V V   V V         V V",
             "V V   V V         V V",
             "V HHHHV HHHVHHHHHHV V",
             "V     H   KV      H H",
             "V          V         E",
             "VVVVVVVVVVVVVVVVVVVVV"],

            [" HHHHHHHHHHHHHHHHHHHV",
             "                    V",
             "V   HHHHHHHHHHHHHH  V",
             "V                   V",
             "V   HHHHHHHHHHHHHH  V",
             "V                   V",
             "V   V            V  V",
             "V   V            V  V",
             "V   HHV HHHHHHHHHV  V",
             "V     HK         V  H",
             "V                V   E",
             "VVVVVVVVVVVVVVVVVVVVV"]
        ]

        self.reset_game()

    def reset_game(self):
        self.character = Character()
        self.walls = []
        self.keys = []
        self.selected_obstacle = random.choice(self.obstacles)

        x = y = 0
        for row in self.selected_obstacle:
            for col in row:
                if col == "H":
                    self.walls.append(Wall((x, y), "horizontal"))
                if col == "V":
                    self.walls.append(Wall((x, y), "vertical"))
                if col == "K":
                    self.keys.append(Key((x, y)))
                if col == "E":
                    self.close_door = Door((x, y))
                x += 120
            y += 120
            x = 0

        self.camera_x = 0
        self.camera_y = 0
        self.current_screen = "initial"
        self.start_time = time.time()
        self.game_status = None
        self.score = 0

    def main_game_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.current_screen == "initial":
                        start_button, exit_button = self.screen.draw_initial_screen(self.game_status, self.score)
                        if start_button.collidepoint(mouse_pos):
                            return True
                        elif exit_button.collidepoint(mouse_pos):
                            pygame.quit()
                            sys.exit()
                    elif self.current_screen == "success":
                        play_again_button, exit_button = self.screen.draw_result_screen("Selamat!", self.score)
                        if play_again_button.collidepoint(mouse_pos):
                            self.current_screen = "initial"
                            self.reset_game()
                            return True
                        elif exit_button.collidepoint(mouse_pos):
                            pygame.quit()
                            sys.exit()
                    elif self.current_screen == "fail":
                        play_again_button, exit_button = self.screen.draw_result_screen("Game Over!", 0)
                        if play_again_button.collidepoint(mouse_pos):
                            self.current_screen = "initial"
                            self.reset_game()
                            return True
                        elif exit_button.collidepoint(mouse_pos):
                            pygame.quit()
                            sys.exit()

            if self.current_screen == "initial":
                self.screen.draw_initial_screen(self.game_status, self.score)
            elif self.current_screen == "success":
                self.screen.draw_result_screen("Selamat!", self.score)
            elif self.current_screen == "fail":
                self.screen.draw_result_screen("Game Over!", 0)

    def start(self):
        while True:
            if self.main_game_loop():
                self.character.rect.topleft = (0, 0)
                running_game = True
                self.start_time = time.time()
                while running_game:
                    self.clock.tick(60)
                    elapsed_time = int(time.time() - self.start_time)
                    time_left = max(self.time_limit - elapsed_time, 0)

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running_game = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                running_game = False

                    key = pygame.key.get_pressed()
                    dx, dy = 0, 0
                    if key[pygame.K_LEFT]:
                        dx = -5
                    if key[pygame.K_RIGHT]:
                        dx = 5
                    if key[pygame.K_UP]:
                        dy = -5
                    if key[pygame.K_DOWN]:
                        dy = 5
                    self.character.move(dx, dy, self.walls, 4270, 3500, self.camera_x, self.camera_y)
                    self.character.collect_key(self.keys)  # Check for key collection

                    self.camera_x = max(0, min(self.character.rect.x, 1730))
                    self.camera_y = max(0, min(self.character.rect.y, 845))

                    self.screen.screen.blit(self.surface, (0, 0))

                    for wall in self.walls:
                        self.screen.screen.blit(wall.image, (wall.rect.x - self.camera_x, wall.rect.y - self.camera_y))

                    self.screen.screen.blit(self.character.image, (self.character.rect.x - self.camera_x, self.character.rect.y - self.camera_y))

                    for key in self.keys:
                        if not key.collected:
                            self.screen.screen.blit(key.image, (key.rect.x - self.camera_x, key.rect.y - self.camera_y))

                    pygame.draw.rect(self.screen.screen, (0, 0, 0),
                                     (self.close_door.rect.x - self.camera_x, self.close_door.rect.y - self.camera_y, 60, 60))

                    self.screen.draw_timer(time_left)
                    pygame.display.flip()

                    if time_left <= 0 or (self.character.has_key and self.character.rect.colliderect(self.close_door.rect)):
                        running_game = False
                        if self.character.has_key and self.character.rect.colliderect(self.close_door.rect):
                            self.score = time_left * 5
                            self.current_screen = "success"
                            self.game_status = "success"
                        else:
                            self.score = 0
                            self.current_screen = "fail"
                            self.game_status = "fail"

                self.screen.screen.fill((0, 0, 0))
                self.reset_game()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.start()
