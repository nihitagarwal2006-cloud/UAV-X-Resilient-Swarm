import os
import sys
import random
import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from main import build_mission
from scenarios.config import ScenarioConfig
from scenarios.gc1_config import ARENA_WIDTH_M, ARENA_HEIGHT_M, OPERATIONAL_CENTER_X_M, OPERATIONAL_CENTER_Y_M, COMMUNICATION_RANGE_M, MIN_UAV_SEPARATION_M

pygame.init()
W, H = 1440, 900
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("UAV-X | Resilient BVLOS Swarm | GC1 Scenario")
clock = pygame.time.Clock()

BG = (6, 12, 20)
PANEL = (12, 22, 35)
BORDER = (42, 67, 88)
TEXT = (225, 236, 244)
MUTED = (130, 150, 165)
CYAN = (60, 205, 255)
GREEN = (65, 225, 135)
RED = (255, 82, 95)
YELLOW = (255, 196, 70)
PURPLE = (177, 110, 255)
WHITE = (245, 250, 253)

FONT_BIG = pygame.font.SysFont("Arial", 28, bold=True)
FONT = pygame.font.SysFont("Arial", 16)
FONT_BOLD = pygame.font.SysFont("Arial", 16, bold=True)
FONT_SMALL = pygame.font.SysFont("Arial", 13)
FONT_MONO = pygame.font.SysFont("Consolas", 12)

MAP = pygame.Rect(285, 100, 790, 560)
RIGHT = pygame.Rect(1090, 100, 335, 560)
BOTTOM = pygame.Rect(15, 680, 1410, 200)

SCENARIOS = [
    (ScenarioConfig.NORMAL, "NORMAL", GREEN),
    (ScenarioConfig.TECHNICAL_FAILURE, "TECH FAILURE", RED),
    (ScenarioConfig.COMMUNICATION_FAILURE, "COMMS FAILURE", PURPLE),
    (ScenarioConfig.MULTIPLE_FAILURE, "MULTIPLE FAILURE", YELLOW),
]

scenario = ScenarioConfig.MULTIPLE_FAILURE
mission, uavs, tasks = build_mission(scenario)
running = True
paused = False

def txt(s, text, font, color, x, y):
    s.blit(font.render(str(text), True, color), (x, y))

def panel(rect):
    pygame.draw.rect(screen, PANEL, rect, border_radius=12)
    pygame.draw.rect(screen, BORDER, rect, 1, border_radius=12)

def world_to_screen(x, y):
    # x=-75 is the centre; arena begins at x=0.
    sx = MAP.left + 95 + (x / ARENA_WIDTH_M) * (MAP.width - 120)
    sy = MAP.top + 35 + (y / ARENA_HEIGHT_M) * (MAP.height - 70)
    return int(sx), int(sy)

def draw_grid():
    pygame.draw.rect(screen, (8, 18, 28), MAP, border_radius=12)
    arena_left = MAP.left + 95
    arena_top = MAP.top + 35
    arena_w = MAP.width - 120
    arena_h = MAP.height - 70
    pygame.draw.rect(screen, (13, 30, 42), (arena_left, arena_top, arena_w, arena_h), 2, border_radius=8)
    for i in range(0, 1001, 100):
        x = arena_left + int(i / 1000 * arena_w)
        y = arena_top + int(i / 1000 * arena_h)
        pygame.draw.line(screen, (24, 48, 63), (x, arena_top), (x, arena_top + arena_h))
        pygame.draw.line(screen, (24, 48, 63), (arena_left, y), (arena_left + arena_w, y))
        txt(screen, f"{i}m", FONT_SMALL, MUTED, x - 10, arena_top + arena_h + 7)
    cx, cy = world_to_screen(OPERATIONAL_CENTER_X_M, OPERATIONAL_CENTER_Y_M)
    pygame.draw.line(screen, CYAN, (cx, cy), (arena_left, cy), 2)
    pygame.draw.circle(screen, CYAN, (cx, cy), 9)
    txt(screen, "OPERATIONAL CENTRE", FONT_SMALL, CYAN, cx - 75, cy - 28)
    txt(screen, "75 m", FONT_SMALL, MUTED, cx + 28, cy + 8)

def draw_poi(task):
    x, y = world_to_screen(task.x, task.y)
    color = GREEN if task.status == "COMPLETED" else YELLOW if task.detected else RED
    pygame.draw.circle(screen, color, (x, y), 8)
    pygame.draw.circle(screen, WHITE, (x, y), 11, 1)
    txt(screen, f"P{task.id}", FONT_SMALL, WHITE, x + 12, y - 7)

def draw_uav(uav):
    x, y = world_to_screen(uav.x, uav.y)
    color = RED if uav.status == "FAILED" else CYAN
    pygame.draw.circle(screen, color, (x, y), 8)
    pygame.draw.line(screen, color, (x - 12, y), (x + 12, y), 2)
    pygame.draw.line(screen, color, (x, y - 12), (x, y + 12), 2)
    txt(screen, f"U{uav.id}", FONT_BOLD, WHITE, x + 12, y - 8)

def reset(new_scenario):
    global mission, uavs, tasks, scenario, paused
    scenario = new_scenario
    mission, uavs, tasks = build_mission(scenario)
    paused = False

def draw():
    screen.fill(BG)
    txt(screen, "UAV-X RESILIENT SWARM", FONT_BIG, WHITE, 18, 20)
    txt(screen, "GC1 PRELIMINARY DESIGN VERIFICATION • OFFICIAL-STYLE SCENARIO", FONT_SMALL, MUTED, 20, 55)
    status = "PAUSED" if paused else ("MISSION COMPLETE" if mission.is_complete() else "SIMULATION RUNNING")
    status_color = YELLOW if paused else GREEN
    txt(screen, status, FONT_BOLD, status_color, 1170, 30)

    panel(MAP)
    draw_grid()
    for task in tasks:
        draw_poi(task)
    for uav in uavs:
        draw_uav(uav)

    panel(RIGHT)
    txt(screen, "MISSION CONTROL", FONT_BOLD, WHITE, RIGHT.x + 18, RIGHT.y + 18)
    txt(screen, scenario.replace("GC1_", ""), FONT_SMALL, YELLOW, RIGHT.x + 18, RIGHT.y + 47)

    completed = sum(t.status == "COMPLETED" for t in tasks)
    detected = sum(t.detected for t in tasks)
    reported = sum(t.reported for t in tasks)
    failed = sum(u.status == "FAILED" for u in uavs)
    recovered = mission.metrics.recovery_events
    comm = mission.metrics.communication_failures

    rows = [
        ("POIs", f"{completed}/{len(tasks)}", GREEN),
        ("Detected", detected, CYAN),
        ("Reported", reported, CYAN),
        ("UAV Failures", failed, RED),
        ("Recovery Events", recovered, YELLOW),
        ("Comm Failures", comm, PURPLE),
        ("Sim Time", f"{mission.step_count * 5}s", WHITE),
    ]
    y = RIGHT.y + 85
    for label, value, color in rows:
        txt(screen, label, FONT_SMALL, MUTED, RIGHT.x + 18, y)
        txt(screen, value, FONT_BOLD, color, RIGHT.x + 190, y - 2)
        y += 31

    metrics_now = mission.summary()
    txt(screen, "COMMUNICATION / SAFETY", FONT_BOLD, WHITE, RIGHT.x + 18, y + 8)
    comm_rows = [
        ("Packet delivery", f"{metrics_now['packet_delivery_ratio']:.1f}%", CYAN),
        ("Avg latency", f"{metrics_now['average_packet_latency_ms']:.1f} ms", CYAN),
        ("Relay allocations", metrics_now['relay_allocations'], YELLOW),
        ("Min separation", f"{metrics_now['minimum_separation_m']:.1f} m", GREEN),
        ("Collisions", metrics_now['collision_count'], GREEN),
    ]
    y += 35
    for label, value, color in comm_rows:
        txt(screen, label, FONT_SMALL, MUTED, RIGHT.x + 18, y)
        txt(screen, value, FONT_BOLD, color, RIGHT.x + 190, y - 2)
        y += 20

    txt(screen, "GC1 CONSTRAINTS", FONT_BOLD, WHITE, RIGHT.x + 18, y + 4)
    constraints = [
        "Arena       1000 x 1000 m",
        "Comm range  100 m",
        "Max speed   5 m/s",
        "Flight time 20 min",
        "Separation  20 m",
        "Max altitude 100 m",
        "POIs        10 random",
    ]
    y += 35
    for line in constraints:
        txt(screen, line, FONT_SMALL, MUTED, RIGHT.x + 18, y)
        y += 21

    panel(BOTTOM)
    txt(screen, "SCENARIOS", FONT_BOLD, WHITE, 30, 695)
    bx = 30
    for name, label, color in SCENARIOS:
        rect = pygame.Rect(bx, 720, 180, 34)
        pygame.draw.rect(screen, (20, 35, 48) if name != scenario else color, rect, border_radius=8)
        pygame.draw.rect(screen, color, rect, 1, border_radius=8)
        txt(screen, label, FONT_SMALL, BG if name == scenario else color, bx + 15, 729)
        bx += 195

    txt(screen, "SYSTEM LOG", FONT_BOLD, WHITE, 30, 770)
    logs = mission.events[-6:]
    yy = 795
    for event in logs:
        txt(screen, event, FONT_MONO, MUTED, 30, yy)
        yy += 15

    txt(screen, "SPACE: pause/resume    R: reset    1-4: scenario", FONT_SMALL, MUTED, 1000, 848)
    pygame.display.flip()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_r:
                reset(scenario)
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                reset(SCENARIOS[event.key - pygame.K_1][0])

    if not paused and not mission.is_complete():
        mission.step()

    draw()
    clock.tick(12)

pygame.quit()
