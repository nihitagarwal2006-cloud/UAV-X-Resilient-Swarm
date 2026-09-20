import sys
import os
import math
import time

import pygame

# ============================================================
# PROJECT IMPORTS
# ============================================================

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from simulation.uav import UAV
from simulation.task import Task
from simulation.mission import Mission
from simulation.failure import FailureSimulator
from scenarios.config import ScenarioConfig


# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()

WIDTH = 1440
HEIGHT = 900

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "UAV-X | Resilient BVIOS Swarm Challenge"
)

clock = pygame.time.Clock()


# ============================================================
# REAL MAP CONFIGURATION
# ============================================================

# The simulation grid is projected onto a real geographic area.
# This is a generic urban disaster-response sample zone.
MAP_CENTER_LAT = 19.0760
MAP_CENTER_LON = 72.8777
MAP_LAT_SPAN = 0.045
MAP_LON_SPAN = 0.055
MAP_ZOOM = 14
MAP_TILE_SIZE = 256
MAP_CACHE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "map_cache"
)
MAP_USER_AGENT = (
    "UAV-X-Resilient-Swarm/1.0 "
    "(educational simulation)"
)

try:
    os.makedirs(MAP_CACHE_DIR, exist_ok=True)
except OSError:
    pass


# ============================================================
# COLORS — PREMIUM DARK COMMAND CENTER
# ============================================================

BG = (6, 12, 20)
BG_2 = (9, 17, 28)

PANEL = (11, 21, 33)
PANEL_2 = (15, 28, 43)
PANEL_3 = (18, 34, 51)

BORDER = (35, 58, 78)
BORDER_BRIGHT = (48, 92, 120)
GRID_MAJOR = (39, 58, 76)

WHITE = (239, 247, 252)
TEXT = (201, 215, 226)
MUTED = (119, 141, 158)

CYAN = (47, 184, 255)
CYAN_BRIGHT = (91, 215, 255)

GREEN = (53, 226, 133)
GREEN_SOFT = (110, 241, 164)

RED = (255, 76, 91)
RED_SOFT = (255, 125, 137)

YELLOW = (255, 190, 65)
YELLOW_SOFT = (255, 214, 115)

PURPLE = (171, 104, 255)
PURPLE_SOFT = (207, 154, 255)

ORANGE = (255, 137, 62)


# ============================================================
# FONTS
# ============================================================

FONT_XL = pygame.font.SysFont(
    "Arial",
    31,
    bold=True
)

FONT_LG = pygame.font.SysFont(
    "Arial",
    23,
    bold=True
)

FONT_MD = pygame.font.SysFont(
    "Arial",
    17,
    bold=True
)

FONT = pygame.font.SysFont(
    "Arial",
    16
)

FONT_SM = pygame.font.SysFont(
    "Arial",
    14
)

FONT_XS = pygame.font.SysFont(
    "Arial",
    12
)

FONT_MONO = pygame.font.SysFont(
    "Consolas",
    13
)


# ============================================================
# LAYOUT
# ============================================================

HEADER_H = 82

LEFT_X = 12
LEFT_W = 285

MAP_X = 309
MAP_Y = 96
MAP_W = 790
MAP_H = 570

RIGHT_X = 1112
RIGHT_W = 316

BOTTOM_Y = 680
BOTTOM_H = 190


# ============================================================
# SCENARIO LABELS
# ============================================================

SCENARIO_LABELS = {
    ScenarioConfig.NORMAL: (
        "NORMAL OPERATION",
        "Baseline swarm operation",
        GREEN
    ),
    ScenarioConfig.TECHNICAL_FAILURE: (
        "TECHNICAL FAILURE",
        "UAV failure + recovery",
        RED
    ),
    ScenarioConfig.COMMUNICATION_FAILURE: (
        "COMMUNICATION FAILURE",
        "Link loss + recovery",
        PURPLE
    ),
    ScenarioConfig.MULTIPLE_FAILURE: (
        "MULTIPLE FAILURE",
        "Multiple UAV failures",
        YELLOW
    ),
}


# ============================================================
# MISSION CREATION
# ============================================================

def create_mission(scenario_name):

    scenario = ScenarioConfig(
        scenario_name
    )

    uavs = [
        UAV(1, 1, 1),
        UAV(2, 10, 2),
        UAV(3, 15, 15),
        UAV(4, 5, 15),
        UAV(5, 18, 18)
    ]

    tasks = [
        Task(1, 8, 8),
        Task(2, 18, 3),
        Task(3, 12, 18)
    ]

    technical_failures = (
        scenario.get_technical_failures()
    )

    communication_failures = (
        scenario.get_communication_failures()
    )

    failure_simulator = None

    if technical_failures:

        failure_simulator = FailureSimulator(
            failures=technical_failures
        )

    mission = Mission(
        uavs,
        tasks,
        failure_simulator=failure_simulator
    )

    mission.start()

    return (
        mission,
        uavs,
        tasks,
        technical_failures,
        communication_failures
    )


# ============================================================
# GLOBAL STATE
# ============================================================

current_scenario = (
    ScenarioConfig.MULTIPLE_FAILURE
)

(
    mission,
    uavs,
    tasks,
    technical_failures,
    communication_failures
) = create_mission(
    current_scenario
)

running = True
finished = False
timer = 0

next_task_id = max(
    task.id for task in tasks
) + 1

event_log = [
    "Simulation initialized",
    "Swarm mission started",
]


# ============================================================
# OFFLINE REAL-WORLD GEO BASEMAP
# ============================================================

# The final competition demo must not depend on internet/DNS access.
# A real-world geographic basemap is bundled next to this simulator.
# It uses a real geographic extent and coastline data, with a clearly
# labelled simulated emergency road layer.  UAV-X overlays its own
# live swarm positions, tasks and paths on top of it.

OFFLINE_MAP_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "uavx_offline_geobase.png"
)

map_surface = None
map_provider_name = "OFFLINE GEO BASEMAP"
map_provider_attribution = (
    "Geographic base: Natural Earth / Basemap  •  "
    "Road layer: UAV-X response simulation"
)
map_error = None


def load_offline_map():

    global map_surface
    global map_error

    try:

        if not os.path.exists(OFFLINE_MAP_PATH):
            raise FileNotFoundError(
                "uavx_offline_geobase.png is missing"
            )

        image = pygame.image.load(
            OFFLINE_MAP_PATH
        ).convert()

        map_surface = pygame.transform.smoothscale(
            image,
            (GRID_SIZE, GRID_SIZE)
        )

        map_error = None

    except Exception as exc:

        map_surface = None
        map_error = str(exc)


def retry_map():
    """Reload the bundled map asset; no internet is required."""
    load_offline_map()


# ============================================================
# MAP COORDINATE CONVERSION
# ============================================================

# The simulator's 20x20 world is projected onto this real-world
# geographic window.  This keeps the existing algorithms untouched.

MAP_MIN_LAT = MAP_CENTER_LAT - MAP_LAT_SPAN / 2
MAP_MAX_LAT = MAP_CENTER_LAT + MAP_LAT_SPAN / 2
MAP_MIN_LON = MAP_CENTER_LON - MAP_LON_SPAN / 2
MAP_MAX_LON = MAP_CENTER_LON + MAP_LON_SPAN / 2


def grid_to_latlon(x, y):

    lon = MAP_MIN_LON + (
        x / 20.0
    ) * (MAP_MAX_LON - MAP_MIN_LON)

    # Screen/simulation Y grows downward, while latitude grows upward.
    lat = MAP_MAX_LAT - (
        y / 20.0
    ) * (MAP_MAX_LAT - MAP_MIN_LAT)

    return lat, lon


def latlon_text(x, y):

    lat, lon = grid_to_latlon(x, y)

    return (
        f"{abs(lat):.4f}°{'N' if lat >= 0 else 'S'}  "
        f"{abs(lon):.4f}°{'E' if lon >= 0 else 'W'}"
    )


# ============================================================
# MAP BACKGROUND DRAWING
# ============================================================


def draw_map_background(surface):

    if map_surface is not None:

        surface.blit(
            map_surface,
            (GRID_X, GRID_Y)
        )

        # Real-world geographic map status chip.
        rounded_rect(
            surface,
            (GRID_X + 12, GRID_Y + 12, 182, 28),
            (8, 25, 35),
            radius=8,
            border=1,
            border_color=BORDER
        )

        pygame.draw.circle(
            surface,
            GREEN,
            (GRID_X + 27, GRID_Y + 26),
            5
        )

        draw_text(
            surface,
            "REAL GEO MAP  •  OFFLINE",
            FONT_XS,
            GREEN_SOFT,
            GRID_X + 40,
            GRID_Y + 19
        )

    else:

        surface.fill(
            BG_2,
            (GRID_X, GRID_Y, GRID_SIZE, GRID_SIZE)
        )

        for i in range(0, GRID_SIZE, 42):
            pygame.draw.line(
                surface,
                (25, 38, 51),
                (GRID_X + i, GRID_Y),
                (GRID_X + i, GRID_Y + GRID_SIZE),
                1
            )
            pygame.draw.line(
                surface,
                (25, 38, 51),
                (GRID_X, GRID_Y + i),
                (GRID_X + GRID_SIZE, GRID_Y + i),
                1
            )

        centered_text(
            surface,
            "OFFLINE MAP ASSET MISSING",
            FONT_SM,
            RED_SOFT,
            pygame.Rect(
                GRID_X,
                GRID_Y + GRID_SIZE // 2 - 18,
                GRID_SIZE,
                36
            )
        )

        centered_text(
            surface,
            "Place uavx_offline_geobase.png beside simulator.py",
            FONT_XS,
            MUTED,
            pygame.Rect(
                GRID_X,
                GRID_Y + GRID_SIZE // 2 + 18,
                GRID_SIZE,
                28
            )
        )


# ============================================================
# DRAWING HELPERS
# ============================================================

def rounded_rect(
    surface,
    rect,
    color,
    radius=10,
    border=0,
    border_color=None
):

    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=radius
    )

    if border and border_color:

        pygame.draw.rect(
            surface,
            border_color,
            rect,
            width=border,
            border_radius=radius
        )


def draw_text(
    surface,
    value,
    font,
    color,
    x,
    y
):

    surface.blit(
        font.render(
            str(value),
            True,
            color
        ),
        (x, y)
    )


def centered_text(
    surface,
    value,
    font,
    color,
    rect
):

    rendered = font.render(
        str(value),
        True,
        color
    )

    surface.blit(
        rendered,
        (
            rect.centerx - rendered.get_width() // 2,
            rect.centery - rendered.get_height() // 2
        )
    )


def draw_icon_circle(
    surface,
    x,
    y,
    radius,
    color,
    symbol=None
):

    pygame.draw.circle(
        surface,
        color,
        (x, y),
        radius
    )

    if symbol:

        centered_text(
            surface,
            symbol,
            FONT_SM,
            BG,
            pygame.Rect(
                x - radius,
                y - radius,
                radius * 2,
                radius * 2
            )
        )


# ============================================================
# MAP COORDINATES
# ============================================================

GRID_X = MAP_X + 28
GRID_Y = MAP_Y + 58
GRID_SIZE = 510

# Load the bundled geographic map immediately.
load_offline_map()


def screen_pos(x, y):

    return (
        int(
            GRID_X
            + (x / 20) * GRID_SIZE
        ),
        int(
            GRID_Y
            + (y / 20) * GRID_SIZE
        )
    )


def grid_pos(mx, my):

    x = round(
        (mx - GRID_X)
        / GRID_SIZE
        * 20
    )

    y = round(
        (my - GRID_Y)
        / GRID_SIZE
        * 20
    )

    return (
        max(0, min(20, x)),
        max(0, min(20, y))
    )


# ============================================================
# UAV ICON — CUTE PROFESSIONAL QUADCOPTER
# ============================================================

def draw_uav(
    surface,
    x,
    y,
    active=True,
    scale=1.0
):

    if active:

        main = CYAN
        glow = CYAN_BRIGHT

    else:

        main = RED
        glow = RED_SOFT

    r = int(14 * scale)

    # subtle glow rings
    pygame.draw.circle(
        surface,
        PANEL_3,
        (x, y),
        r + 8
    )

    # diagonal arms
    pygame.draw.line(
        surface,
        glow,
        (x - r, y - r),
        (x + r, y + r),
        max(2, int(3 * scale))
    )

    pygame.draw.line(
        surface,
        glow,
        (x - r, y + r),
        (x + r, y - r),
        max(2, int(3 * scale))
    )

    rotor_points = [
        (x - r, y - r),
        (x + r, y - r),
        (x - r, y + r),
        (x + r, y + r),
    ]

    for rx, ry in rotor_points:

        pygame.draw.circle(
            surface,
            main,
            (rx, ry),
            max(5, int(6 * scale)),
            2
        )

        pygame.draw.circle(
            surface,
            glow,
            (rx, ry),
            max(2, int(2 * scale))
        )

    # central body
    pygame.draw.circle(
        surface,
        main,
        (x, y),
        max(7, int(8 * scale))
    )

    pygame.draw.circle(
        surface,
        glow,
        (x, y),
        max(2, int(3 * scale))
    )


# ============================================================
# TASK ICON
# ============================================================

def draw_task(
    surface,
    task
):

    x, y = screen_pos(
        task.x,
        task.y
    )

    if task.status == "COMPLETED":

        color = GREEN
        label = "COMPLETED"

    elif task.status == "ASSIGNED":

        color = YELLOW
        label = "ASSIGNED"

    else:

        color = RED
        label = "PENDING"

    # target outer ring
    pygame.draw.circle(
        surface,
        color,
        (x, y),
        13,
        2
    )

    pygame.draw.circle(
        surface,
        color,
        (x, y),
        5
    )

    # four small target ticks
    pygame.draw.line(
        surface,
        color,
        (x - 19, y),
        (x - 12, y),
        2
    )

    pygame.draw.line(
        surface,
        color,
        (x + 12, y),
        (x + 19, y),
        2
    )

    pygame.draw.line(
        surface,
        color,
        (x, y - 19),
        (x, y - 12),
        2
    )

    pygame.draw.line(
        surface,
        color,
        (x, y + 12),
        (x, y + 19),
        2
    )

    # task label card
    label_rect = pygame.Rect(
        x + 19,
        y - 14,
        86,
        34
    )

    rounded_rect(
        surface,
        label_rect,
        PANEL_3,
        7,
        1,
        BORDER
    )

    draw_text(
        surface,
        f"T{task.id}",
        FONT_SM,
        WHITE,
        label_rect.x + 8,
        label_rect.y + 3
    )

    draw_text(
        surface,
        label,
        FONT_XS,
        color,
        label_rect.x + 8,
        label_rect.y + 18
    )


# ============================================================
# SCENARIO RESET
# ============================================================

def reset_scenario(
    scenario_name
):

    global current_scenario
    global mission
    global uavs
    global tasks
    global technical_failures
    global communication_failures
    global finished
    global timer
    global next_task_id
    global event_log

    current_scenario = scenario_name

    (
        mission,
        uavs,
        tasks,
        technical_failures,
        communication_failures
    ) = create_mission(
        scenario_name
    )

    finished = False
    timer = 0

    next_task_id = max(
        task.id for task in tasks
    ) + 1

    event_log = [
        f"Scenario: "
        f"{SCENARIO_LABELS[scenario_name][0]}",
        "Swarm mission initialized",
    ]


# ============================================================
# EVENT LOG UPDATE
# ============================================================

last_failures = 0
last_recoveries = 0
last_completed = 0


def update_event_log(
    metrics
):

    global last_failures
    global last_recoveries
    global last_completed

    if metrics["uav_failures"] > last_failures:

        for uav in uavs:

            if uav.status == "FAILED":

                event_log.append(
                    f"UAV {uav.id} marked FAILED"
                )

                break

        last_failures = metrics[
            "uav_failures"
        ]

    if metrics["recovery_events"] > last_recoveries:

        event_log.append(
            "Recovery manager reassigned task"
        )

        last_recoveries = metrics[
            "recovery_events"
        ]

    if metrics["completed_tasks"] > last_completed:

        event_log.append(
            f"Task completed "
            f"({metrics['completed_tasks']}/"
            f"{metrics['total_tasks']})"
        )

        last_completed = metrics[
            "completed_tasks"
        ]

    if len(event_log) > 8:

        del event_log[
            :len(event_log) - 8
        ]


# ============================================================
# MAIN LOOP
# ============================================================

while running:

    dt = clock.tick(60)

    timer += dt


    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_1:

                reset_scenario(
                    ScenarioConfig.NORMAL
                )

            elif event.key == pygame.K_2:

                reset_scenario(
                    ScenarioConfig.TECHNICAL_FAILURE
                )

            elif event.key == pygame.K_3:

                reset_scenario(
                    ScenarioConfig.COMMUNICATION_FAILURE
                )

            elif event.key == pygame.K_4:

                reset_scenario(
                    ScenarioConfig.MULTIPLE_FAILURE
                )

            elif event.key == pygame.K_r:

                retry_map()


        elif event.type == pygame.MOUSEBUTTONDOWN:

            mx, my = event.pos

            # interactive task creation
            if (
                GRID_X <= mx
                <= GRID_X + GRID_SIZE
                and
                GRID_Y <= my
                <= GRID_Y + GRID_SIZE
            ):

                gx, gy = grid_pos(
                    mx,
                    my
                )

                new_task = Task(
                    next_task_id,
                    gx,
                    gy,
                    priority="HIGH"
                )

                if mission.add_task(
                    new_task
                ):

                    event_log.append(
                        f"New task T{next_task_id} created"
                    )

                    next_task_id += 1

                    finished = False

                    timer = 0


    # ========================================================
    # COMMUNICATION FAILURE EVENTS
    # ========================================================

    for failure in communication_failures:

        if mission.step_count == failure["step"]:

            uid = failure["uav_id"]

            if (
                uid in mission.uav_states
                and
                mission.uav_states[
                    uid
                ].communication_status
            ):

                mission.uav_states[
                    uid
                ].set_communication(
                    False
                )

                event_log.append(
                    f"Communication lost: UAV {uid}"
                )


    # ========================================================
    # SIMULATION STEP
    # ========================================================

    if (
        not finished
        and
        timer >= 350
    ):

        timer = 0

        if not mission.is_complete():

            mission.step()

        else:

            finished = True


    if mission.is_complete():

        finished = True


    # ========================================================
    # METRICS
    # ========================================================

    metrics = mission.get_metrics()

    update_event_log(
        metrics
    )


    # ========================================================
    # BACKGROUND
    # ========================================================

    screen.fill(BG)

    # subtle top glow
    pygame.draw.rect(
        screen,
        BG_2,
        (0, 0, WIDTH, HEADER_H)
    )


    # ========================================================
    # TOP NAVIGATION
    # ========================================================

    draw_text(
        screen,
        "UAV-X",
        FONT_XL,
        WHITE,
        22,
        19
    )

    draw_text(
        screen,
        "RESILIENT SWARM",
        FONT_XL,
        CYAN_BRIGHT,
        120,
        19
    )

    draw_text(
        screen,
        "ADAPT",
        FONT_SM,
        MUTED,
        390,
        29
    )

    draw_text(
        screen,
        "|",
        FONT_SM,
        BORDER_BRIGHT,
        435,
        29
    )

    draw_text(
        screen,
        "RECOVER",
        FONT_SM,
        MUTED,
        452,
        29
    )

    draw_text(
        screen,
        "|",
        FONT_SM,
        BORDER_BRIGHT,
        527,
        29
    )

    draw_text(
        screen,
        "COMPLETE",
        FONT_SM,
        MUTED,
        544,
        29
    )


    # simulation pill
    sim_rect = pygame.Rect(
        640,
        18,
        150,
        40
    )

    rounded_rect(
        screen,
        sim_rect,
        (19, 59, 51),
        20,
        1,
        (36, 111, 88)
    )

    pygame.draw.circle(
        screen,
        GREEN,
        (660, 38),
        6
    )

    draw_text(
        screen,
        "SIMULATION",
        FONT_SM,
        GREEN_SOFT,
        674,
        29
    )


    # scenario selector card
    scenario_rect = pygame.Rect(
        1050,
        10,
        378,
        56
    )

    rounded_rect(
        screen,
        scenario_rect,
        PANEL,
        12,
        1,
        BORDER
    )

    draw_text(
        screen,
        "SCENARIO",
        FONT_XS,
        MUTED,
        1068,
        17
    )

    scenario_label = SCENARIO_LABELS[
        current_scenario
    ]

    draw_text(
        screen,
        scenario_label[0],
        FONT_SM,
        scenario_label[2],
        1068,
        34
    )

    draw_text(
        screen,
        "1–4",
        FONT_SM,
        TEXT,
        1380,
        30
    )


    # ========================================================
    # LEFT CONTROL PANEL
    # ========================================================

    left_panel = pygame.Rect(
        LEFT_X,
        MAP_Y,
        LEFT_W,
        MAP_H
    )

    rounded_rect(
        screen,
        left_panel,
        PANEL,
        13,
        1,
        BORDER
    )


    draw_text(
        screen,
        "MISSION OVERVIEW",
        FONT_LG,
        WHITE,
        28,
        112
    )

    # live status
    live_rect = pygame.Rect(
        220,
        108,
        62,
        28
    )

    rounded_rect(
        screen,
        live_rect,
        (17, 61, 47),
        14
    )

    pygame.draw.circle(
        screen,
        GREEN,
        (234, 122),
        4
    )

    draw_text(
        screen,
        "LIVE",
        FONT_XS,
        GREEN_SOFT,
        243,
        115
    )


    draw_text(
        screen,
        "Resilient Multi-UAV",
        FONT_MD,
        WHITE,
        28,
        153
    )

    draw_text(
        screen,
        "Mission Simulation",
        FONT_SM,
        MUTED,
        28,
        177
    )


    # overview progress
    draw_text(
        screen,
        "MISSION PROGRESS",
        FONT_XS,
        MUTED,
        28,
        215
    )

    progress_rect = pygame.Rect(
        28,
        237,
        235,
        9
    )

    rounded_rect(
        screen,
        progress_rect,
        (30, 48, 63),
        5
    )

    progress = max(
        0,
        min(
            1,
            metrics["completion_rate"] / 100
        )
    )

    if progress > 0:

        fill = pygame.Rect(
            28,
            237,
            max(
                4,
                int(
                    235 * progress
                )
            ),
            9
        )

        rounded_rect(
            screen,
            fill,
            GREEN,
            5
        )

    draw_text(
        screen,
        f"{metrics['completed_tasks']}/"
        f"{metrics['total_tasks']}",
        FONT_SM,
        WHITE,
        28,
        254
    )

    draw_text(
        screen,
        f"{metrics['completion_rate']:.0f}%",
        FONT_SM,
        GREEN_SOFT,
        225,
        254
    )


    # scenario buttons
    draw_text(
        screen,
        "SCENARIO",
        FONT_XS,
        MUTED,
        28,
        295
    )

    scenario_buttons = [
        (
            "1",
            ScenarioConfig.NORMAL,
            28,
            320
        ),
        (
            "2",
            ScenarioConfig.TECHNICAL_FAILURE,
            28,
            364
        ),
        (
            "3",
            ScenarioConfig.COMMUNICATION_FAILURE,
            28,
            408
        ),
        (
            "4",
            ScenarioConfig.MULTIPLE_FAILURE,
            28,
            452
        ),
    ]

    for key, name, bx, by in scenario_buttons:

        selected = (
            name == current_scenario
        )

        color = SCENARIO_LABELS[
            name
        ][2]

        rect = pygame.Rect(
            bx,
            by,
            235,
            35
        )

        rounded_rect(
            screen,
            rect,
            (
                PANEL_3
                if selected
                else (10, 19, 30)
            ),
            8,
            1,
            color if selected else BORDER
        )

        draw_text(
            screen,
            key,
            FONT_SM,
            color,
            bx + 12,
            by + 9
        )

        draw_text(
            screen,
            SCENARIO_LABELS[
                name
            ][0],
            FONT_XS,
            WHITE if selected else MUTED,
            bx + 38,
            by + 10
        )


    # controls
    draw_text(
        screen,
        "INTERACTION",
        FONT_XS,
        MUTED,
        28,
        515
    )

    draw_text(
        screen,
        "• Click map  →  create task",
        FONT_XS,
        TEXT,
        28,
        540
    )

    draw_text(
        screen,
        "• Keys 1–4   →  switch scenario",
        FONT_XS,
        TEXT,
        28,
        562
    )

    draw_text(
        screen,
        "• Simulation advances automatically",
        FONT_XS,
        TEXT,
        28,
        584
    )


    # resilience mini-card
    mini = pygame.Rect(
        28,
        620,
        235,
        62
    )

    rounded_rect(
        screen,
        mini,
        (15, 38, 43),
        10,
        1,
        (31, 82, 84)
    )

    draw_text(
        screen,
        "RESILIENCE",
        FONT_XS,
        CYAN_BRIGHT,
        40,
        632
    )

    draw_text(
        screen,
        f"{metrics['uav_failures']} failures",
        FONT_SM,
        RED_SOFT,
        40,
        653
    )

    draw_text(
        screen,
        f"{metrics['recovery_events']} recoveries",
        FONT_SM,
        GREEN_SOFT,
        150,
        653
    )


    # ========================================================
    # MAP PANEL
    # ========================================================

    map_panel = pygame.Rect(
        MAP_X,
        MAP_Y,
        MAP_W,
        MAP_H
    )

    rounded_rect(
        screen,
        map_panel,
        PANEL,
        13,
        1,
        BORDER
    )


    draw_text(
        screen,
        "SWARM MAP",
        FONT_LG,
        WHITE,
        MAP_X + 22,
        MAP_Y + 18
    )

    draw_text(
        screen,
        "Real-time UAV positions, tasks and flight paths",
        FONT_SM,
        MUTED,
        MAP_X + 135,
        MAP_Y + 24
    )


    # map mode chips
    modes = [
        ("OSM MAP", True),
        ("GEO GRID", True),
        ("PATHS", True)
    ]

    chip_x = MAP_X + 520

    for label, active in modes:

        w = 82

        chip = pygame.Rect(
            chip_x,
            MAP_Y + 17,
            w,
            28
        )

        rounded_rect(
            screen,
            chip,
            (
                PANEL_3
                if active
                else (9, 17, 27)
            ),
            8,
            1,
            BORDER
        )

        centered_text(
            screen,
            label,
            FONT_XS,
            CYAN_SOFT if False else (
                CYAN_BRIGHT
                if active
                else MUTED
            ),
            chip
        )

        chip_x += w + 7


    # real geographic map background
    draw_map_background(screen)

    # map frame
    pygame.draw.rect(
        screen,
        BORDER_BRIGHT,
        (GRID_X, GRID_Y, GRID_SIZE, GRID_SIZE),
        1,
        border_radius=8
    )

    # geographic reference grid, kept subtle so the real map remains visible
    for i in range(1, 5):

        gx = GRID_X + int(i * GRID_SIZE / 5)
        gy = GRID_Y + int(i * GRID_SIZE / 5)

        pygame.draw.line(
            screen,
            (110, 190, 215),
            (gx, GRID_Y),
            (gx, GRID_Y + GRID_SIZE),
            1
        )

        pygame.draw.line(
            screen,
            (110, 190, 215),
            (GRID_X, gy),
            (GRID_X + GRID_SIZE, gy),
            1
        )

    # north arrow
    pygame.draw.line(
        screen,
        WHITE,
        (GRID_X + GRID_SIZE - 25, GRID_Y + 38),
        (GRID_X + GRID_SIZE - 25, GRID_Y + 13),
        2
    )
    pygame.draw.polygon(
        screen,
        WHITE,
        [
            (GRID_X + GRID_SIZE - 25, GRID_Y + 8),
            (GRID_X + GRID_SIZE - 31, GRID_Y + 20),
            (GRID_X + GRID_SIZE - 19, GRID_Y + 20)
        ]
    )
    draw_text(
        screen,
        "N",
        FONT_XS,
        WHITE,
        GRID_X + GRID_SIZE - 31,
        GRID_Y + 42
    )


    # flight paths
    for uav in uavs:

        if len(uav.path) < 2:

            continue

        points = [
            screen_pos(
                px,
                py
            )
            for px, py in uav.path
        ]

        if uav.status == "FAILED":

            path_color = (
                120,
                52,
                62
            )

        else:

            path_color = (
                35,
                124,
                171
            )

        # dashed path
        for i in range(
            0,
            len(points) - 1
        ):

            if (
                i // 3
            ) % 2 == 0:

                pygame.draw.line(
                    screen,
                    path_color,
                    points[i],
                    points[i + 1],
                    3
                )


    # tasks
    for task in tasks:

        draw_task(
            screen,
            task
        )


    # UAVs
    for uav in uavs:

        x, y = screen_pos(
            uav.x,
            uav.y
        )

        draw_uav(
            screen,
            x,
            y,
            uav.status != "FAILED",
            1.0
        )

        # label
        label = pygame.Rect(
            x - 28,
            y + 19,
            70,
            25
        )

        rounded_rect(
            screen,
            label,
            PANEL_3,
            6,
            1,
            BORDER
        )

        centered_text(
            screen,
            f"UAV {uav.id}",
            FONT_XS,
            (
                RED_SOFT
                if uav.status == "FAILED"
                else CYAN_BRIGHT
            ),
            label
        )


    # geographic zone label
    zone_rect = pygame.Rect(
        GRID_X + 12,
        GRID_Y + 12,
        188,
        40
    )

    rounded_rect(
        screen,
        zone_rect,
        (6, 18, 27),
        8,
        1,
        BORDER
    )

    draw_text(
        screen,
        "DISASTER RESPONSE ZONE",
        FONT_XS,
        CYAN_BRIGHT,
        zone_rect.x + 10,
        zone_rect.y + 7
    )

    draw_text(
        screen,
        f"{MAP_CENTER_LAT:.4f}°N  {MAP_CENTER_LON:.4f}°E",
        FONT_XS,
        WHITE,
        zone_rect.x + 10,
        zone_rect.y + 22
    )


    # map legend
    legend = pygame.Rect(
        GRID_X,
        GRID_Y + GRID_SIZE - 37,
        335,
        30
    )

    rounded_rect(
        screen,
        legend,
        (8, 16, 26),
        7,
        1,
        BORDER
    )

    legend_items = [
        ("ACTIVE", CYAN),
        ("FAILED", RED),
        ("COMPLETED", GREEN)
    ]

    lx = GRID_X + 12

    for label, color in legend_items:

        pygame.draw.circle(
            screen,
            color,
            (lx, GRID_Y + GRID_SIZE - 22),
            4
        )

        draw_text(
            screen,
            label,
            FONT_XS,
            MUTED,
            lx + 10,
            GRID_Y + GRID_SIZE - 29
        )

        lx += 92

    # Required OpenStreetMap attribution.
    draw_text(
        screen,
        "© OpenStreetMap contributors",
        FONT_XS,
        WHITE,
        GRID_X + GRID_SIZE - 175,
        GRID_Y + GRID_SIZE - 18
    )


    # ========================================================
    # RIGHT: MISSION CONTROL
    # ========================================================

    right_panel = pygame.Rect(
        RIGHT_X,
        MAP_Y,
        RIGHT_W,
        MAP_H
    )

    rounded_rect(
        screen,
        right_panel,
        PANEL,
        13,
        1,
        BORDER
    )


    draw_text(
        screen,
        "MISSION CONTROL",
        FONT_LG,
        WHITE,
        RIGHT_X + 18,
        MAP_Y + 18
    )

    draw_text(
        screen,
        "LIVE TELEMETRY",
        FONT_XS,
        MUTED,
        RIGHT_X + 18,
        MAP_Y + 47
    )


    # KPI cards
    kpi_y = MAP_Y + 75
    kpi_w = 88
    kpi_h = 73

    kpis = [
        (
            "TASKS",
            f"{metrics['completed_tasks']}/"
            f"{metrics['total_tasks']}",
            GREEN
        ),
        (
            "SUCCESS",
            f"{metrics['completion_rate']:.0f}%",
            CYAN_BRIGHT
        ),
        (
            "FAILURES",
            str(metrics["uav_failures"]),
            RED
        ),
    ]

    for i, (
        label,
        value,
        color
    ) in enumerate(kpis):

        rect = pygame.Rect(
            RIGHT_X + 18 + i * 98,
            kpi_y,
            kpi_w,
            kpi_h
        )

        rounded_rect(
            screen,
            rect,
            PANEL_2,
            10,
            1,
            BORDER
        )

        draw_text(
            screen,
            label,
            FONT_XS,
            MUTED,
            rect.x + 10,
            rect.y + 9
        )

        draw_text(
            screen,
            value,
            FONT_LG,
            color,
            rect.x + 10,
            rect.y + 32
        )


    # progress
    progress_y = MAP_Y + 160

    draw_text(
        screen,
        "MISSION PROGRESS",
        FONT_XS,
        MUTED,
        RIGHT_X + 18,
        progress_y
    )

    pbar = pygame.Rect(
        RIGHT_X + 18,
        progress_y + 24,
        RIGHT_W - 36,
        9
    )

    rounded_rect(
        screen,
        pbar,
        (28, 44, 58),
        5
    )

    if progress > 0:

        rounded_rect(
            screen,
            (
                pbar.x,
                pbar.y,
                max(
                    5,
                    int(
                        pbar.width
                        * progress
                    )
                ),
                pbar.height
            ),
            GREEN,
            5
        )


    # telemetry
    telemetry_y = MAP_Y + 208

    draw_text(
        screen,
        "TELEMETRY",
        FONT_MD,
        WHITE,
        RIGHT_X + 18,
        telemetry_y
    )

    telemetry = [
        (
            "Simulation step",
            metrics["mission_steps"],
            WHITE
        ),
        (
            "Recovery events",
            metrics["recovery_events"],
            YELLOW
        ),
        (
            "Communication failures",
            metrics["communication_failures"],
            PURPLE
        ),
    ]

    ty = telemetry_y + 34

    for label, value, color in telemetry:

        draw_text(
            screen,
            label,
            FONT_SM,
            MUTED,
            RIGHT_X + 18,
            ty
        )

        rendered = FONT.render(
            str(value),
            True,
            color
        )

        screen.blit(
            rendered,
            (
                RIGHT_X
                + RIGHT_W
                - 18
                - rendered.get_width(),
                ty
            )
        )

        ty += 27


    # UAV fleet
    fleet_y = MAP_Y + 340

    draw_text(
        screen,
        "UAV FLEET",
        FONT_MD,
        WHITE,
        RIGHT_X + 18,
        fleet_y
    )

    fleet_y += 31

    for uav in uavs:

        active = (
            uav.status != "FAILED"
        )

        color = (
            CYAN
            if active
            else RED
        )

        pygame.draw.circle(
            screen,
            color,
            (
                RIGHT_X + 25,
                fleet_y + 8
            ),
            5
        )

        draw_text(
            screen,
            f"UAV {uav.id}",
            FONT_SM,
            WHITE,
            RIGHT_X + 38,
            fleet_y
        )

        status = (
            "ACTIVE"
            if active
            else "FAILED"
        )

        rendered = FONT_SM.render(
            status,
            True,
            color
        )

        screen.blit(
            rendered,
            (
                RIGHT_X
                + RIGHT_W
                - 18
                - rendered.get_width(),
                fleet_y
            )
        )

        fleet_y += 28


    # resilience card
    resilience = pygame.Rect(
        RIGHT_X + 18,
        MAP_Y + 515,
        RIGHT_W - 36,
        54
    )

    rounded_rect(
        screen,
        resilience,
        (14, 39, 41),
        10,
        1,
        (30, 83, 84)
    )

    draw_text(
        screen,
        "RESILIENCE",
        FONT_XS,
        CYAN_BRIGHT,
        resilience.x + 13,
        resilience.y + 9
    )

    draw_text(
        screen,
        f"{metrics['uav_failures']} failures",
        FONT_SM,
        RED_SOFT,
        resilience.x + 13,
        resilience.y + 28
    )

    draw_text(
        screen,
        f"{metrics['recovery_events']} recoveries",
        FONT_SM,
        GREEN_SOFT,
        resilience.x + 150,
        resilience.y + 28
    )


    # ========================================================
    # BOTTOM PANELS
    # ========================================================

    # Event log
    log_panel = pygame.Rect(
        LEFT_X,
        BOTTOM_Y,
        620,
        BOTTOM_H
    )

    rounded_rect(
        screen,
        log_panel,
        PANEL,
        12,
        1,
        BORDER
    )

    draw_text(
        screen,
        "SYSTEM LOG",
        FONT_MD,
        WHITE,
        LEFT_X + 17,
        BOTTOM_Y + 15
    )

    draw_text(
        screen,
        "LIVE",
        FONT_XS,
        GREEN_SOFT,
        LEFT_X + 112,
        BOTTOM_Y + 18
    )

    log_y = BOTTOM_Y + 47

    for entry in event_log[-7:]:

        draw_text(
            screen,
            "›",
            FONT,
            CYAN,
            LEFT_X + 18,
            log_y
        )

        draw_text(
            screen,
            entry,
            FONT_MONO,
            TEXT,
            LEFT_X + 34,
            log_y + 1
        )

        log_y += 18


    # Task list
    task_panel = pygame.Rect(
        647,
        BOTTOM_Y,
        452,
        BOTTOM_H
    )

    rounded_rect(
        screen,
        task_panel,
        PANEL,
        12,
        1,
        BORDER
    )

    draw_text(
        screen,
        "TASK STATUS",
        FONT_MD,
        WHITE,
        665,
        BOTTOM_Y + 15
    )

    draw_text(
        screen,
        f"{metrics['completed_tasks']}/"
        f"{metrics['total_tasks']} COMPLETE",
        FONT_XS,
        GREEN_SOFT,
        950,
        BOTTOM_Y + 18
    )

    task_y = BOTTOM_Y + 50

    for task in tasks[:5]:

        if task.status == "COMPLETED":

            color = GREEN
            status = "COMPLETED"

        elif task.status == "ASSIGNED":

            color = YELLOW
            status = "IN PROGRESS"

        else:

            color = RED
            status = "PENDING"

        pygame.draw.circle(
            screen,
            color,
            (670, task_y + 8),
            5
        )

        draw_text(
            screen,
            f"T{task.id}",
            FONT_SM,
            WHITE,
            685,
            task_y
        )

        draw_text(
            screen,
            status,
            FONT_XS,
            color,
            745,
            task_y + 2
        )

        if task.assigned_uav is not None:

            draw_text(
                screen,
                f"UAV {task.assigned_uav}",
                FONT_XS,
                MUTED,
                945,
                task_y + 2
            )

        task_y += 25


    # mission statistics
    stats_panel = pygame.Rect(
        1112,
        BOTTOM_Y,
        RIGHT_W,
        BOTTOM_H
    )

    rounded_rect(
        screen,
        stats_panel,
        PANEL,
        12,
        1,
        BORDER
    )

    draw_text(
        screen,
        "MISSION STATISTICS",
        FONT_MD,
        WHITE,
        RIGHT_X + 17,
        BOTTOM_Y + 15
    )

    stats = [
        (
            "Tasks completed",
            f"{metrics['completed_tasks']}/"
            f"{metrics['total_tasks']}",
            GREEN
        ),
        (
            "Recovery events",
            str(metrics["recovery_events"]),
            YELLOW
        ),
        (
            "UAV failures",
            str(metrics["uav_failures"]),
            RED
        ),
        (
            "Mission steps",
            str(metrics["mission_steps"]),
            CYAN
        ),
        (
            "Communication failures",
            str(metrics["communication_failures"]),
            PURPLE
        ),
        (
            "Success rate",
            f"{metrics['completion_rate']:.0f}%",
            GREEN
        ),
    ]

    sy = BOTTOM_Y + 49

    for i, (
        label,
        value,
        color
    ) in enumerate(stats):

        col = i % 2
        row = i // 2

        x = RIGHT_X + 17 + col * 150
        y = sy + row * 39

        draw_text(
            screen,
            label,
            FONT_XS,
            MUTED,
            x,
            y
        )

        draw_text(
            screen,
            value,
            FONT_MD,
            color,
            x,
            y + 15
        )


    # ========================================================
    # MISSION COMPLETE BANNER
    # ========================================================

    if finished:

        complete = pygame.Rect(
            500,
            608,
            400,
            46
        )

        rounded_rect(
            screen,
            complete,
            (17, 65, 49),
            12,
            1,
            (44, 137, 96)
        )

        centered_text(
            screen,
            "✓  MISSION COMPLETE",
            FONT_MD,
            GREEN_SOFT,
            complete
        )


    # ========================================================
    # FOOTER
    # ========================================================

    draw_text(
        screen,
        "UAV-X  |  Resilient BVIOS Swarm Simulation",
        FONT_XS,
        MUTED,
        18,
        HEIGHT - 19
    )

    draw_text(
        screen,
        "ADAPT  •  RECOVER  •  CONTINUE",
        FONT_XS,
        CYAN,
        WIDTH - 210,
        HEIGHT - 19
    )


    # ========================================================
    # DISPLAY
    # ========================================================

    pygame.display.flip()


pygame.quit()
