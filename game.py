"""
2D Platformer Adventure - Python Game
Requirements: pip install pygame
Controls:
  A/D or Left/Right  - Move
  W / Up / Space      - Jump (double jump supported)
  ESC                 - Quit
Goal: Collect all coins, avoid enemies, reach the flag!
"""

import pygame
import sys
import math
import random

# ── Constants ─────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1100, 640
FPS           = 60
GRAVITY       = 0.55
MAX_FALL      = 18
TILE          = 48

# ── Colours ───────────────────────────────────────────────────────────────────
SKY_TOP    = (20,  12,  60)
SKY_BOT    = (60,  30, 120)
C_WHITE    = (255, 255, 255)
C_YELLOW   = (255, 220,  40)
C_RED      = (220,  50,  50)
C_GREEN    = (60,  200,  80)
C_DARK_GRN = (30,  120,  40)
C_BROWN    = (120,  70,  30)
C_STONE    = (100, 100, 120)
C_STONE2   = ( 80,  80, 100)
C_GOLD     = (255, 195,   0)
C_COIN_SHD = (180, 130,   0)
C_PLAYER   = ( 80, 160, 255)
C_PLAYER_D = ( 40,  90, 200)
C_ENEMY    = (220,  70,  60)
C_ENEMY_D  = (150,  30,  20)
C_FLAG_P   = (200, 200, 220)
C_FLAG_F   = (255,  80,  80)
C_HUD_BG   = (  0,   0,   0, 160)
C_SPIKE    = (180, 180, 200)
C_STAR     = (255, 255, 180)

# ── Tilemap ────────────────────────────────────────────────────────────────────
# 0=air, 1=grass, 2=stone, 3=coin, 4=enemy, 5=flag, 6=spike, 7=platform
LEVEL = [
    "                                                   ",
    "                                                   ",
    "                    3                              ",
    "           33     =====          3     3           ",
    "     3                       =========             ",
    "  ========   3                          3   5      ",
    "              ====   33                  ===P===   ",
    "  3                        3       6 6             ",
    "===  4  ===   3   ====  =======  =========  ===    ",
    "                 4                                 ",
    "=====  3  ===========   3   ===========  4  ===   ",
    "                   3          3                    ",
    "111111111111111111111111111111111111111111111111111",
]

COLS = len(LEVEL[0])
ROWS = len(LEVEL)
MAP_W = COLS * TILE
MAP_H = ROWS * TILE

# ── Stars ──────────────────────────────────────────────────────────────────────
STARS = [(random.randint(0, MAP_W), random.randint(0, HEIGHT // 2),
          random.uniform(0.3, 1.0)) for _ in range(120)]

# ── Helpers ───────────────────────────────────────────────────────────────────
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def draw_gradient_rect(surf, top_col, bot_col, rect):
    x, y, w, h = rect
    for dy in range(h):
        t = dy / max(h - 1, 1)
        pygame.draw.line(surf, lerp_color(top_col, bot_col, t), (x, y + dy), (x + w - 1, y + dy))

# ── Tile drawing ──────────────────────────────────────────────────────────────
def draw_grass_tile(surf, x, y):
    pygame.draw.rect(surf, C_BROWN, (x, y + 12, TILE, TILE - 12))
    pygame.draw.rect(surf, C_GREEN, (x, y, TILE, 14))
    for bx in range(0, TILE, 8):
        h = random.choice([4, 6, 8])
        pygame.draw.rect(surf, C_DARK_GRN, (x + bx + 2, y - h + 4, 3, h))

def draw_stone_tile(surf, x, y):
    pygame.draw.rect(surf, C_STONE, (x, y, TILE, TILE))
    pygame.draw.rect(surf, C_STONE2, (x + 1, y + 1, TILE - 2, TILE - 2))
    pygame.draw.line(surf, C_STONE, (x, y + TILE // 2), (x + TILE, y + TILE // 2), 1)
    pygame.draw.line(surf, C_STONE, (x + TILE // 2, y), (x + TILE // 2, y + TILE // 2), 1)

def draw_platform_tile(surf, x, y):
    pygame.draw.rect(surf, (80, 60, 140), (x, y, TILE, TILE // 2))
    pygame.draw.rect(surf, (110, 85, 180), (x + 2, y + 2, TILE - 4, TILE // 2 - 4))

def draw_spike(surf, x, y):
    mid = x + TILE // 2
    bot = y + TILE
    for ox in (-16, 0, 16):
        pts = [(mid + ox, y + 8), (mid + ox - 10, bot), (mid + ox + 10, bot)]
        pygame.draw.polygon(surf, C_SPIKE, pts)

def draw_coin(surf, x, y, tick):
    cx, cy = x + TILE // 2, y + TILE // 2
    scale = abs(math.cos(tick * 0.07))
    rx = max(2, int(14 * scale))
    pygame.draw.ellipse(surf, C_COIN_SHD, (cx - rx - 1, cy - 15, rx * 2 + 2, 30))
    pygame.draw.ellipse(surf, C_GOLD,     (cx - rx,     cy - 14, rx * 2,     28))
    if rx > 5:
        pygame.draw.ellipse(surf, (255, 230, 80), (cx - rx + 3, cy - 9, max(2, rx - 4), 10))

def draw_flag(surf, x, y, tick):
    px, py = x + TILE // 2, y
    pygame.draw.line(surf, C_FLAG_P, (px, py + TILE * 2), (px, py - 10), 3)
    wave = math.sin(tick * 0.08) * 6
    pts = [(px, py - 10), (px + 28 + wave, py + 5), (px, py + 20)]
    pygame.draw.polygon(surf, C_FLAG_F, pts)

# ── Entity classes ────────────────────────────────────────────────────────────

class Player:
    W, H = 32, 42

    def __init__(self, x, y):
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.on_ground   = False
        self.jumps_left  = 2
        self.facing      = 1
        self.alive       = True
        self.won         = False
        self.anim        = 0
        self.invuln      = 0   # invulnerability frames after hit
        self.health      = 3

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def jump(self):
        if self.jumps_left > 0:
            self.vy = -13.5 if self.jumps_left == 2 else -11.0
            self.jumps_left -= 1
            self.on_ground = False

    def update(self, tiles, spikes, coins, enemies, flag_rect):
        keys = pygame.key.get_pressed()
        spd  = 5.0
        self.vx = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.vx = -spd; self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx =  spd; self.facing =  1

        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        self.anim = (self.anim + (1 if self.vx != 0 else 0)) % 30

        # horizontal
        self.x += self.vx
        rx = self.rect
        for t in tiles:
            if rx.colliderect(t):
                if self.vx > 0: self.x = t.left  - self.W
                else:            self.x = t.right
                self.vx = 0
        # vertical
        self.y += self.vy
        ry = self.rect
        self.on_ground = False
        for t in tiles:
            if ry.colliderect(t):
                if self.vy > 0:
                    self.y = t.top - self.H
                    self.vy = 0
                    self.on_ground = True
                    self.jumps_left = 2
                else:
                    self.y = t.bottom
                    self.vy = 0
        # spikes
        if self.invuln == 0:
            for s in spikes:
                if self.rect.colliderect(s):
                    self.health -= 1
                    self.invuln  = 90
                    self.vy      = -10
                    if self.health <= 0:
                        self.alive = False
        # coins
        for c in coins[:]:
            if not c.collected and self.rect.colliderect(c.rect):
                c.collected = True
        # enemies
        if self.invuln == 0:
            for e in enemies:
                if e.alive and self.rect.colliderect(e.rect):
                    # stomp from above
                    if self.vy > 0 and self.y + self.H < e.y + e.H // 2 + 12:
                        e.alive = False
                        self.vy = -9
                    else:
                        self.health -= 1
                        self.invuln  = 90
                        self.vy      = -8
                        self.vx      = -6 * self.facing
                        if self.health <= 0:
                            self.alive = False
        # flag
        if self.rect.colliderect(flag_rect):
            self.won = True

        if self.invuln > 0:
            self.invuln -= 1

        # fall off world
        if self.y > MAP_H + 100:
            self.alive = False

    def draw(self, surf, cam_x, tick):
        x = int(self.x) - cam_x
        y = int(self.y)
        if self.invuln > 0 and (self.invuln // 6) % 2 == 0:
            return  # blink when invulnerable

        # legs animation
        leg_off = int(math.sin(self.anim * 0.4) * 7) if self.vx != 0 else 0
        pygame.draw.rect(surf, C_PLAYER_D, (x + 6,  y + 26, 9, 16))       # left leg
        pygame.draw.rect(surf, C_PLAYER_D, (x + 17, y + 26, 9, 16 - leg_off))  # right leg
        # body
        pygame.draw.rect(surf, C_PLAYER,   (x + 2,  y + 10, 28, 20))
        # head
        pygame.draw.circle(surf, C_PLAYER, (x + 16, y + 8), 13)
        # eye
        ex = x + 16 + self.facing * 5
        pygame.draw.circle(surf, C_WHITE, (ex, y + 6), 4)
        pygame.draw.circle(surf, (20, 20, 80), (ex + self.facing, y + 6), 2)
        # arms
        arm_y = y + 14 + int(math.sin(tick * 0.12) * 3)
        pygame.draw.rect(surf, C_PLAYER_D, (x - 4,  arm_y, 8, 6))
        pygame.draw.rect(surf, C_PLAYER_D, (x + 28, arm_y, 8, 6))


class Enemy:
    W, H = 36, 34

    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx = 1.8
        self.vy = 0.0
        self.alive = True
        self.anim  = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self, tiles):
        if not self.alive:
            return
        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        self.x += self.vx
        self.anim = (self.anim + 1) % 20
        for t in tiles:
            if self.rect.colliderect(t):
                self.vx *= -1
                self.x += self.vx * 2
                break
        self.y += self.vy
        for t in tiles:
            if self.rect.colliderect(t):
                if self.vy > 0:
                    self.y = t.top - self.H
                    self.vy = 0
                else:
                    self.y = t.bottom
                    self.vy = 0

    def draw(self, surf, cam_x, tick):
        if not self.alive:
            return
        x = int(self.x) - cam_x
        y = int(self.y)
        facing = 1 if self.vx > 0 else -1
        # body
        pygame.draw.ellipse(surf, C_ENEMY,   (x, y + 10, self.W, 24))
        pygame.draw.ellipse(surf, C_ENEMY_D, (x + 3, y + 13, self.W - 6, 18))
        # head
        pygame.draw.circle(surf, C_ENEMY, (x + 18, y + 10), 12)
        # eyes
        ex = x + 18 + facing * 5
        pygame.draw.circle(surf, C_WHITE, (ex, y + 8), 4)
        pygame.draw.circle(surf, (10, 10, 10), (ex + facing, y + 8), 2)
        # spiky top
        for i in range(3):
            sx = x + 8 + i * 10
            pygame.draw.polygon(surf, C_ENEMY_D, [(sx, y + 2), (sx + 4, y + 12), (sx - 4, y + 12)])
        # legs
        leg = int(math.sin(self.anim * 0.6) * 5)
        pygame.draw.rect(surf, C_ENEMY_D, (x + 6,  y + 30, 8, 10 + leg))
        pygame.draw.rect(surf, C_ENEMY_D, (x + 22, y + 30, 8, 10 - leg))


class Coin:
    def __init__(self, x, y):
        self.x, self.y   = x, y
        self.collected   = False

    @property
    def rect(self):
        return pygame.Rect(self.x + 10, self.y + 8, 28, 32)


class Particle:
    def __init__(self, x, y, col):
        self.x, self.y = float(x), float(y)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.col   = col
        self.life  = random.randint(20, 40)
        self.size  = random.randint(3, 7)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1

    def draw(self, surf, cam_x):
        if self.life > 0:
            alpha = int(255 * self.life / 40)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.col, alpha), (self.size, self.size), self.size)
            surf.blit(s, (int(self.x) - cam_x - self.size, int(self.y) - self.size))


# ── Build level ───────────────────────────────────────────────────────────────

def build_level():
    tiles    = []
    spikes   = []
    coins    = []
    enemies  = []
    player   = None
    flag_pos = None

    # pre-render tile surfaces
    grass_surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    draw_grass_tile(grass_surf, 0, 0)
    stone_surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    draw_stone_tile(stone_surf, 0, 0)
    plat_surf  = pygame.Surface((TILE, TILE // 2), pygame.SRCALPHA)
    draw_platform_tile(plat_surf, 0, 0)

    for r, row in enumerate(LEVEL):
        for c, ch in enumerate(row):
            x, y = c * TILE, r * TILE
            if ch == '1':
                tiles.append(pygame.Rect(x, y, TILE, TILE))
            elif ch == '2':
                tiles.append(pygame.Rect(x, y, TILE, TILE))
            elif ch == '=':
                tiles.append(pygame.Rect(x, y, TILE, TILE // 2))
            elif ch == '3':
                coins.append(Coin(x, y))
            elif ch == '4':
                enemies.append(Enemy(x, y - 2))
            elif ch == '5' or ch == 'P':
                flag_pos = (x, y)
            elif ch == '6':
                spikes.append(pygame.Rect(x, y, TILE, TILE))
            elif ch == 'S':
                player = Player(x, y - Player.H)

    if player is None:
        player = Player(TILE, (ROWS - 2) * TILE - Player.H)

    flag_rect = pygame.Rect(flag_pos[0], flag_pos[1] - TILE * 2, TILE, TILE * 2) if flag_pos else pygame.Rect(0,0,1,1)

    return tiles, spikes, coins, enemies, player, flag_pos, flag_rect, grass_surf, stone_surf, plat_surf


# ── Draw world ────────────────────────────────────────────────────────────────

def draw_world(surf, cam_x, tick, tiles, spikes, coins, enemies, flag_pos,
               grass_surf, stone_surf, plat_surf, particles):

    # sky gradient
    draw_gradient_rect(surf, SKY_TOP, SKY_BOT, (0, 0, WIDTH, HEIGHT))

    # stars
    for sx, sy, br in STARS:
        twinkle = 0.5 + 0.5 * math.sin(tick * 0.04 + sx)
        alpha   = int(200 * br * twinkle)
        if alpha < 20:
            continue
        r = 1 if br < 0.6 else 2
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*C_STAR, alpha), (r + 1, r + 1), r)
        surf.blit(s, (sx - cam_x // 4 % WIDTH - r, sy - r))

    # tiles
    for t in tiles:
        tx, ty = t.x - cam_x, t.y
        if -TILE < tx < WIDTH + TILE:
            if t.height == TILE:
                ch = LEVEL[t.y // TILE][t.x // TILE] if t.y // TILE < ROWS else '2'
                img = grass_surf if ch == '1' else stone_surf
                surf.blit(img, (tx, ty))
            else:
                surf.blit(plat_surf, (tx, ty))

    # spikes
    for s in spikes:
        sx = s.x - cam_x
        if -TILE < sx < WIDTH + TILE:
            draw_spike(surf, sx, s.y)

    # coins
    for c in coins:
        if not c.collected:
            draw_coin(surf, c.x - cam_x, c.y, tick)

    # flag
    if flag_pos:
        draw_flag(surf, flag_pos[0] - cam_x, flag_pos[1], tick)

    # enemies
    for e in enemies:
        e.draw(surf, cam_x, tick)

    # particles
    for p in particles[:]:
        p.update()
        p.draw(surf, cam_x)
        if p.life <= 0:
            particles.remove(p)


def draw_hud(surf, font_big, font_sm, player, total_coins, collected, tick):
    # coin counter
    hw = 220
    s = pygame.Surface((hw, 40), pygame.SRCALPHA)
    s.fill((0, 0, 0, 120))
    surf.blit(s, (10, 10))
    draw_coin(surf, 12, 2, tick)
    txt = font_big.render(f"{collected} / {total_coins}", True, C_GOLD)
    surf.blit(txt, (65, 15))

    # health hearts
    for i in range(3):
        col = C_RED if i < player.health else (60, 60, 80)
        hx, hy = WIDTH - 130 + i * 40, 15
        pygame.draw.circle(surf, col, (hx + 7, hy + 7), 7)
        pygame.draw.circle(surf, col, (hx + 21, hy + 7), 7)
        pygame.draw.polygon(surf, col, [(hx, hy + 10), (hx + 14, hy + 26), (hx + 28, hy + 10)])

    # controls hint
    hint = font_sm.render("A/D move   W/Space jump (x2)   stomp enemies!", True, (160, 160, 200))
    surf.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 26))


def draw_overlay(surf, font_big, font_sm, msg, sub, tick):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 170))
    surf.blit(ov, (0, 0))
    pulse = 1.0 + 0.05 * math.sin(tick * 0.1)
    t1 = font_big.render(msg, True, C_GOLD)
    t2 = font_sm.render(sub, True, C_WHITE)
    surf.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 60))
    surf.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 + 10))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Platformer Adventure")
    clock  = pygame.time.Clock()

    font_big = pygame.font.SysFont("consolas", 48, bold=True)
    font_sm  = pygame.font.SysFont("consolas", 22)

    def reset():
        return build_level()

    tiles, spikes, coins, enemies, player, flag_pos, flag_rect, grass_surf, stone_surf, plat_surf = reset()
    particles  = []
    cam_x      = 0
    tick       = 0
    game_state = "play"   # play | dead | won

    prev_enemies_alive = {id(e): True for e in enemies}

    while True:
        clock.tick(FPS)
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if game_state == "play":
                    if event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                        player.jump()
                if game_state in ("dead", "won"):
                    if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                        tiles, spikes, coins, enemies, player, flag_pos, flag_rect, grass_surf, stone_surf, plat_surf = reset()
                        particles = []
                        cam_x  = 0
                        tick   = 0
                        game_state = "play"
                        prev_enemies_alive = {id(e): True for e in enemies}

        if game_state == "play":
            player.update(tiles, spikes, coins, enemies, flag_rect)

            # enemy update + death particles
            for e in enemies:
                was_alive = prev_enemies_alive.get(id(e), True)
                e.update(tiles)
                if was_alive and not e.alive:
                    for _ in range(18):
                        particles.append(Particle(e.x + e.W // 2, e.y + e.H // 2, C_ENEMY))
                prev_enemies_alive[id(e)] = e.alive

            # coin collect particles
            for c in coins:
                if c.collected and not hasattr(c, '_popped'):
                    c._popped = True
                    for _ in range(10):
                        particles.append(Particle(c.x + TILE // 2, c.y + TILE // 2, C_GOLD))

            if not player.alive:
                game_state = "dead"
            if player.won:
                game_state = "won"

        # camera follow
        target_cam = int(player.x) - WIDTH // 3
        target_cam = max(0, min(target_cam, MAP_W - WIDTH))
        cam_x += int((target_cam - cam_x) * 0.12)

        # draw
        draw_world(screen, cam_x, tick, tiles, spikes, coins, enemies,
                   flag_pos, grass_surf, stone_surf, plat_surf, particles)
        player.draw(screen, cam_x, tick)

        collected = sum(1 for c in coins if c.collected)
        total     = len(coins)
        draw_hud(screen, font_big, font_sm, player, total, collected, tick)

        if game_state == "dead":
            draw_overlay(screen, font_big, font_sm,
                         "YOU DIED", "Press R or ENTER to restart", tick)
        elif game_state == "won":
            draw_overlay(screen, font_big, font_sm,
                         f"YOU WIN!  {collected}/{total} coins",
                         "Press R or ENTER to play again", tick)

        pygame.display.flip()


if __name__ == "__main__":
    main()