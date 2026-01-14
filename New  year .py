import pygame
import random
import time
import math
import struct
import wave
import os
from datetime import datetime

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init()

# Sound Synthesis Helper
def generate_wav(filename, duration, type="sine", frequency=440, notes=None):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        
        if notes:
            # Generate a sequence of notes
            samples_per_note = n_samples // len(notes)
            for note_freq in notes:
                for i in range(samples_per_note):
                    t = i / sample_rate
                    value = int(16383.0 * math.sin(2.0 * math.pi * note_freq * t))
                    # Add subtle harmony
                    value += int(8000.0 * math.sin(2.0 * math.pi * note_freq * 1.5 * t))
                    # Smooth fade in/out for each note
                    if i < 1000: value = int(value * (i/1000))
                    if i > samples_per_note - 1000: value = int(value * ((samples_per_note-i)/1000))
                    f.writeframes(struct.pack('<h', value))
        else:
            for i in range(n_samples):
                if type == "sine":
                    value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
                elif type == "noise":
                    value = random.randint(-32767, 32767)
                fade = (n_samples - i) / n_samples
                value = int(value * fade)
                f.writeframes(struct.pack('<h', value))

# Generate default sounds
if not os.path.exists("boom.wav"):
    generate_wav("boom.wav", 0.5, "noise", frequency=100)

# "Beautiful" Background Melody (Auld Lang Syne-ish or generic festive)
melody = [261.63, 329.63, 392.00, 523.25, 440.00, 349.23, 261.63] # Harmony notes
if not os.path.exists("bg_music.wav"):
    generate_wav("bg_music.wav", 4.0, notes=melody)

try:
    sound_boom = pygame.mixer.Sound("boom.wav")
    pygame.mixer.music.load("bg_music.wav")
    pygame.mixer.music.set_volume(0.3)
except:
    sound_boom = None

# Screen Setup
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("New Year 2026 Celebration")

# Colors
BLACK = (5, 5, 5)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)

# Fonts
try:
    font_clock = pygame.font.SysFont("Orbitron", 100, bold=True)
    font_msg = pygame.font.SysFont("Orbitron", 150, bold=True)
    font_sub = pygame.font.SysFont("Lexend", 60)
except:
    font_clock = pygame.font.SysFont("Arial", 100, bold=True)
    font_msg = pygame.font.SysFont("Arial", 150, bold=True)
    font_sub = pygame.font.SysFont("Arial", 60)

# Effect Variables
shake_amount = 0
flash_alpha = 0

# "2026" Pattern definition (Simplified grid)
DIGITS_MAP = {
    '2': [(0,0),(1,0),(2,0),(2,1),(1,1),(0,1),(0,2),(1,2),(2,2)],
    '0': [(0,0),(1,0),(2,0),(2,1),(2,2),(1,2),(0,2),(0,1)],
    '6': [(0,0),(1,0),(2,0),(0,1),(0,2),(1,2),(2,2),(2,1),(1,1)]
}

def get_2026_coords():
    coords = []
    # 2
    for x, y in DIGITS_MAP['2']: coords.append((x, y))
    # 0
    for x, y in DIGITS_MAP['0']: coords.append((x + 4, y))
    # 2
    for x, y in DIGITS_MAP['2']: coords.append((x + 8, y))
    # 6
    for x, y in DIGITS_MAP['6']: coords.append((x + 12, y))
    return coords

class Confetti:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.size = random.randint(5, 10)
        self.color = [random.randint(100, 255) for _ in range(3)]
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(2, 5)
        self.angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(2, 10)

    def update(self):
        self.y += self.vy
        self.x += self.vx
        self.angle += self.rotation_speed
        if self.y > HEIGHT:
            self.y = random.randint(-50, -10)
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.color, 200), (0, 0, self.size, self.size))
        rotated_s = pygame.transform.rotate(s, self.angle)
        surface.blit(rotated_s, (int(self.x), int(self.y)))

class Particle:
    def __init__(self, x, y, color, firework=False):
        self.x = x
        self.y = y
        self.color = color
        self.firework = firework
        self.alpha = 255
        
        if firework:
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-15, -10)
        else:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            
        self.gravity = 0.15
        self.friction = 0.98 if not firework else 1.0
        self.decay = random.uniform(2, 5)

    def update(self):
        self.vx *= self.friction
        self.vy *= self.friction
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.alpha -= self.decay

    def draw(self, surface):
        if self.alpha > 0:
            # Twinkle effect: vary alpha randomly for some sparkles
            current_alpha = self.alpha
            if random.random() < 0.2: # 20% chance to twinkle
                current_alpha = max(0, self.alpha - 100)
                
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, int(current_alpha)), (2, 2), 2)
            surface.blit(s, (int(self.x), int(self.y)))

class Firework:
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = HEIGHT
        self.target_y = random.randint(100, HEIGHT // 2)
        self.color = [random.randint(100, 255) for _ in range(3)]
        self.rocket = Particle(self.x, self.y, self.color, True)
        self.particles = []
        self.exploded = False
        self.dead = False

    def update(self):
        if not self.exploded:
            self.rocket.update()
            if self.rocket.vy >= 0 or self.rocket.y <= self.target_y:
                self.explode()
        else:
            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.alpha > 0]
            if not self.particles:
                self.dead = True

    def explode(self):
        global shake_amount, flash_alpha
        self.exploded = True
        num_particles = random.randint(120, 250)
        shape_type = random.choice(["circle", "heart", "star", "ring", "2026"])
        
        # Trigger effects
        shake_amount = 15
        flash_alpha = 100
        
        if shape_type == "2026":
            coords = get_2026_coords()
            for cx, cy in coords:
                # Add multiple particles per point for density
                for _ in range(3):
                    p = Particle(self.rocket.x, self.rocket.y, self.color)
                    # Target spread
                    p.vx = (cx - 7) * 1.5 + random.uniform(-0.5, 0.5)
                    p.vy = (cy - 1) * 1.5 + random.uniform(-0.5, 0.5)
                    self.particles.append(p)
        else:
            for i in range(num_particles):
                p = Particle(self.rocket.x, self.rocket.y, self.color)
                
                if shape_type == "heart":
                    t = (i / num_particles) * 2 * math.pi
                    p.vx = 16 * math.sin(t)**3
                    p.vy = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
                    scale = random.uniform(0.3, 0.6)
                    p.vx *= scale
                    p.vy *= scale
                elif shape_type == "star":
                    t = (i / num_particles) * 2 * math.pi
                    r = 5 + 5 * math.cos(5 * t)
                    p.vx = r * math.cos(t)
                    p.vy = r * math.sin(t)
                    scale = random.uniform(0.5, 1.0)
                    p.vx *= scale
                    p.vy *= scale
                elif shape_type == "ring":
                    t = (i / num_particles) * 2 * math.pi
                    speed = random.uniform(6, 8)
                    p.vx = math.cos(t) * speed
                    p.vy = math.sin(t) * speed
                else: # circle
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(2, 10)
                    p.vx = math.cos(angle) * speed
                    p.vy = math.sin(angle) * speed
                
                p.vx += random.uniform(-0.5, 0.5)
                p.vy += random.uniform(-0.5, 0.5)
                self.particles.append(p)
            
        if sound_boom:
            sound_boom.set_volume(0.4)
            sound_boom.play()

    def draw(self, surface):
        if not self.exploded:
            self.rocket.draw(surface)
        else:
            for p in self.particles:
                p.draw(surface)

def main():
    global shake_amount, flash_alpha
    clock = pygame.time.Clock()
    fireworks = []
    confetti_list = []
    running = True
    is_new_year = False
    
    # Countdown state
    start_time = time.time()
    
    # Create surfaces for effects
    main_surface = pygame.Surface((WIDTH, HEIGHT))

    while running:
        # Update effects
        if shake_amount > 0: shake_amount -= 1
        if flash_alpha > 0: flash_alpha -= 5

        main_surface.fill(BLACK)
        
        elapsed = int(time.time() - start_time)
        
        if not is_new_year:
            current_seconds = 55 + elapsed
            if current_seconds < 60:
                time_str = f"11: 59;{current_seconds:02} 2025"
            else:
                time_str = "12: 00;00 2026"
                is_new_year = True
                # Start music on celebration
                try:
                    pygame.mixer.music.play(-1)
                except:
                    pass
                # Create initial confetti burst
                for _ in range(150):
                    confetti_list.append(Confetti())
        else:
            time_str = "12: 00;00 2026"
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        if not is_new_year:
            txt_shadow = font_clock.render(time_str, True, (40, 40, 40))
            txt_clock = font_clock.render(time_str, True, WHITE)
            main_surface.blit(txt_shadow, (WIDTH // 2 - txt_clock.get_width() // 2 + 5, HEIGHT // 2 - txt_clock.get_height() // 2 + 5))
            main_surface.blit(txt_clock, (WIDTH // 2 - txt_clock.get_width() // 2, HEIGHT // 2 - txt_clock.get_height() // 2))
            
            sub_txt = font_sub.render("STAY TUNED...", True, GOLD)
            main_surface.blit(sub_txt, (WIDTH // 2 - sub_txt.get_width() // 2, HEIGHT // 2 - txt_clock.get_height() // 2 - 100))
        else:
            # Draw Confetti underneath fireworks
            for c in confetti_list:
                c.update()
                c.draw(main_surface)

            if random.random() < 0.15:
                fireworks.append(Firework())
            
            for fw in fireworks:
                fw.update()
                fw.draw(main_surface)
            fireworks = [fw for fw in fireworks if not fw.dead]
            
            # Rainbow Color Cycling
            hue = (time.time() * 100) % 360
            color_main = pygame.Color(0)
            color_main.hsla = (hue, 100, 70, 100)
            
            color_sub = pygame.Color(0)
            color_sub.hsla = ((hue + 60) % 360, 100, 60, 100)
            
            # Breathing/Scaling effect
            scale_factor = 1.0 + math.sin(time.time() * 3) * 0.08
            
            main_msg = "HAPPY NEW YEAR"
            sub_msg = "2026"
            urdu_msg = "Naya saal mubarak ho!"
            
            # Render and Scale Main Text
            temp_main = font_msg.render(main_msg, True, color_main)
            new_size = (int(temp_main.get_width() * scale_factor), int(temp_main.get_height() * scale_factor))
            txt_main = pygame.transform.smoothscale(temp_main, new_size)
            
            # Shine effect: white overlay with pulsing alpha
            shine_alpha = int(abs(math.sin(time.time() * 5)) * 180)
            shine_surf = font_msg.render(main_msg, True, (255, 255, 255))
            shine_surf.set_alpha(shine_alpha)
            scaled_shine = pygame.transform.smoothscale(shine_surf, new_size)
            
            txt_sub = font_sub.render(sub_msg, True, color_sub)
            txt_urdu = font_sub.render(urdu_msg, True, WHITE)
            
            pulse = math.sin(time.time() * 5) * 10
            main_pos = (WIDTH // 2 - txt_main.get_width() // 2, HEIGHT // 2 - txt_main.get_height() // 2 + pulse)
            sub_pos = (WIDTH // 2 - txt_sub.get_width() // 2, HEIGHT // 2 + txt_main.get_height() // 2 + 20 + pulse)
            urdu_pos = (WIDTH // 2 - txt_urdu.get_width() // 2, HEIGHT // 2 + txt_main.get_height() // 2 + 100 + pulse)
            
            # Shadow
            txt_shadow = font_msg.render(main_msg, True, (20, 20, 20))
            scaled_shadow = pygame.transform.smoothscale(txt_shadow, new_size)
            main_surface.blit(scaled_shadow, (main_pos[0]+5, main_pos[1]+5))
            
            main_surface.blit(txt_main, main_pos)
            main_surface.blit(scaled_shine, main_pos) # Layer shine on top
            main_surface.blit(txt_sub, sub_pos)
            main_surface.blit(txt_urdu, urdu_pos)

        # Apply Screen Shake
        offset_x = random.randint(-shake_amount, shake_amount) if shake_amount > 0 else 0
        offset_y = random.randint(-shake_amount, shake_amount) if shake_amount > 0 else 0
        screen.blit(main_surface, (offset_x, offset_y))

        # Apply Screen Flash
        if flash_alpha > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(int(flash_alpha))
            screen.blit(flash_surf, (0, 0))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()





