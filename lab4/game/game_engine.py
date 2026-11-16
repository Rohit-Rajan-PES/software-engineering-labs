import random
import pygame

from game.player import Player
from game.anvil import Anvil


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.velocity_x = random.uniform(-3, 3)
        self.velocity_y = random.uniform(-5, -1)

        self.life = random.randint(15, 30)
        self.max_life = self.life

        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Gravity
        self.velocity_y += 0.25

        self.life -= 1

    def is_dead(self):
        return self.life <= 0

    def render(self, surface):
        alpha = int(255 * (self.life / self.max_life))

        particle_surface = pygame.Surface(
            (self.size * 2, self.size * 2), pygame.SRCALPHA
        )

        pygame.draw.circle(
            particle_surface, (180, 180, 180, alpha), (self.size, self.size), self.size
        )

        surface.blit(particle_surface, (int(self.x), int(self.y)))


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.player = Player(width, height)

        self.anvils = []
        self.particles = []

        # -------------------------
        # Difficulty
        # -------------------------

        self.spawn_delay = 700
        self.min_spawn_delay = 250

        self.difficulty_level = 0

        self.last_spawn_time = pygame.time.get_ticks()

        # -------------------------
        # Game timer
        # -------------------------

        self.start_ticks = pygame.time.get_ticks()
        self.survival_time = 0

        self.game_state = "PLAYING"

        # -------------------------
        # Screen shake
        # -------------------------

        self.shake_timer = 0
        self.shake_strength = 0

        # -------------------------
        # Fonts
        # -------------------------

        self.font_big = pygame.font.SysFont(None, 52)

        self.font_medium = pygame.font.SysFont(None, 34)

        self.font_small = pygame.font.SysFont(None, 24)

    # =========================================================
    # EVENT HANDLING
    # =========================================================

    def handle_event(self, event):
        if self.game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()

    # =========================================================
    # DIFFICULTY
    # =========================================================

    def update_difficulty(self):
        # Increase difficulty every 10 seconds.
        new_level = self.survival_time // 10

        if new_level != self.difficulty_level:
            self.difficulty_level = new_level

            # Spawn anvils more frequently.
            self.spawn_delay = max(
                self.min_spawn_delay, 700 - self.difficulty_level * 60
            )

    def get_speed_multiplier(self):
        # Increase anvil speed gradually.
        multiplier = 1.0 + self.difficulty_level * 0.12

        # Maximum multiplier of 2x.
        return min(multiplier, 2.0)

    # =========================================================
    # IMPACT EFFECT
    # =========================================================

    def create_impact_effect(self, anvil):
        impact_x = anvil.x + anvil.width // 2

        impact_y = self.height - 20

        # Create dust particles.
        for _ in range(18):
            particle = Particle(impact_x, impact_y)

            self.particles.append(particle)

        # Start screen shake.
        self.shake_timer = 8
        self.shake_strength = 5

    # =========================================================
    # PARTICLES
    # =========================================================

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()

            if particle.is_dead():
                self.particles.remove(particle)

    # =========================================================
    # SCREEN SHAKE
    # =========================================================

    def update_screen_shake(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1

            if self.shake_timer == 0:
                self.shake_strength = 0

    # =========================================================
    # GAME UPDATE
    # =========================================================

    def update(self):
        if self.game_state != "PLAYING":
            self.update_particles()
            self.update_screen_shake()
            return

        # -------------------------
        # Player movement
        # -------------------------

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()

        self.player.update()

        # -------------------------
        # Survival timer
        # -------------------------

        self.survival_time = (pygame.time.get_ticks() - self.start_ticks) // 1000

        # -------------------------
        # Dynamic difficulty
        # -------------------------

        self.update_difficulty()

        # -------------------------
        # Spawn anvils
        # -------------------------

        now = pygame.time.get_ticks()

        if now - self.last_spawn_time >= self.spawn_delay:
            speed_multiplier = self.get_speed_multiplier()

            self.anvils.append(Anvil(self.width, speed_multiplier))

            self.last_spawn_time = now

        # -------------------------
        # Collision
        # -------------------------

        player_rect = self.player.rect

        for anvil in self.anvils[:]:
            anvil.update()

            # Player collision
            if player_rect.colliderect(anvil.rect):
                self.game_state = "GAME_OVER"

            # Ground impact
            if anvil.y + anvil.height >= self.height - 20:
                self.create_impact_effect(anvil)

                if anvil in self.anvils:
                    self.anvils.remove(anvil)

                continue

            # Remove anvils that somehow
            # travel beyond the screen.
            if anvil.is_off_screen(self.height):
                if anvil in self.anvils:
                    self.anvils.remove(anvil)

        # -------------------------
        # Effects
        # -------------------------

        self.update_particles()
        self.update_screen_shake()

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):
        self.player = Player(self.width, self.height)

        self.anvils.clear()
        self.particles.clear()

        self.start_ticks = pygame.time.get_ticks()

        self.last_spawn_time = pygame.time.get_ticks()

        self.survival_time = 0

        self.spawn_delay = 700
        self.difficulty_level = 0

        self.shake_timer = 0
        self.shake_strength = 0

        self.game_state = "PLAYING"

    # =========================================================
    # RENDER
    # =========================================================

    def render(self, screen):

        # -------------------------
        # Create game surface
        # -------------------------

        game_surface = pygame.Surface((self.width, self.height))

        game_surface.fill((35, 38, 45))

        # -------------------------
        # Ground
        # -------------------------

        ground_y = self.height - 20

        pygame.draw.rect(game_surface, (70, 75, 85), (0, ground_y, self.width, 20))

        pygame.draw.line(
            game_surface, (160, 90, 40), (0, ground_y), (self.width, ground_y), 3
        )

        # -------------------------
        # Player
        # -------------------------

        self.player.render(game_surface)

        # -------------------------
        # Anvils
        # -------------------------

        for anvil in self.anvils:
            anvil.render(game_surface)

        # -------------------------
        # Particles
        # -------------------------

        for particle in self.particles:
            particle.render(game_surface)

        # -------------------------
        # Screen shake
        # -------------------------

        shake_x = 0
        shake_y = 0

        if self.shake_timer > 0:
            shake_x = random.randint(-self.shake_strength, self.shake_strength)

            shake_y = random.randint(-self.shake_strength, self.shake_strength)

        screen.fill((35, 38, 45))

        screen.blit(game_surface, (shake_x, shake_y))

        # -------------------------
        # UI
        # -------------------------

        time_surface = self.font_medium.render(
            f"Survival Time: {self.survival_time}s", True, (240, 240, 240)
        )

        screen.blit(time_surface, (20, 20))

        instruction_surface = self.font_small.render(
            "Use [A/D] or [Arrow Keys] to Dodge", True, (170, 175, 185)
        )

        screen.blit(
            instruction_surface, (self.width - instruction_surface.get_width() - 20, 25)
        )

        # -------------------------
        # Game over
        # -------------------------

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            overlay.fill((0, 0, 0, 190))

            screen.blit(overlay, (0, 0))

            game_over_surface = self.font_big.render(
                "CRUSHED! GAME OVER", True, (235, 65, 65)
            )

            screen.blit(
                game_over_surface,
                (
                    self.width // 2 - game_over_surface.get_width() // 2,
                    self.height // 2 - 60,
                ),
            )

            score_surface = self.font_medium.render(
                f"You survived: {self.survival_time} seconds", True, (255, 255, 255)
            )

            screen.blit(
                score_surface,
                (self.width // 2 - score_surface.get_width() // 2, self.height // 2),
            )

            restart_surface = self.font_small.render(
                "Press [R] to Play Again", True, (200, 200, 200)
            )

            screen.blit(
                restart_surface,
                (
                    self.width // 2 - restart_surface.get_width() // 2,
                    self.height // 2 + 50,
                ),
            )
