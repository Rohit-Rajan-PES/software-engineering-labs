import random
import pygame


class Anvil:
    def __init__(self, screen_width, speed_multiplier=1.0):
        self.screen_width = screen_width

        self.width = 40
        self.height = 32

        self.x = random.randint(20, screen_width - self.width - 20)

        self.y = -self.height

        # Base anvil speed
        base_speed = random.uniform(4.5, 7.0)

        # Apply dynamic difficulty multiplier
        self.speed = base_speed * speed_multiplier

    def update(self):
        self.y += self.speed

    def is_off_screen(self, screen_height):
        return self.y > screen_height + 10

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def render(self, surface):
        # Warning color based on anvil speed
        if self.speed >= 10:
            # Very fast
            color = (255, 60, 40)

        elif self.speed >= 8:
            # Fast
            color = (255, 150, 40)

        else:
            # Normal
            color = (120, 120, 130)

        # Top part of anvil
        top_rect = pygame.Rect(int(self.x) + 4, int(self.y), self.width - 8, 14)

        pygame.draw.rect(surface, color, top_rect, border_radius=2)

        # Main body
        base_rect = pygame.Rect(int(self.x), int(self.y) + 14, self.width, 18)

        pygame.draw.rect(surface, (80, 80, 90), base_rect, border_radius=3)

        # Colored outline to make the warning state visible
        pygame.draw.rect(surface, color, base_rect, width=1, border_radius=3)

