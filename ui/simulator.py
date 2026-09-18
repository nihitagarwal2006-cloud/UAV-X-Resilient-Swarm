import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import pygame

from simulation.uav import UAV
from simulation.task import Task
from simulation.mission import Mission
from simulation.failure import FailureSimulator


pygame.init()

WIDTH, HEIGHT = 1100, 720

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "UAV-X Resilient Swarm Simulator"
)

clock = pygame.time.Clock()

title_font = pygame.font.SysFont(
    "Arial", 28, bold=True
)

font = pygame.font.SysFont(
    "Arial", 21
)

small = pygame.font.SysFont(
    "Arial", 17
)

tiny = pygame.font.SysFont(
    "Arial", 14
)


# =====================================
# REAL UAV SWARM
# =====================================

uavs = [
    UAV(1, 1, 1),
    UAV(2, 10, 2),
    UAV(3, 15, 15),
    UAV(4, 5, 15)
]


# =====================================
# REAL TASKS
# =====================================

tasks = [
    Task(1, 8, 8),
    Task(2, 18, 3),
    Task(3, 12, 18)
]


# =====================================
# FAILURE SCENARIO
# =====================================

failure_simulator = FailureSimulator(
    failure_step=6,
    uav_id=2
)


# =====================================
# REAL MISSION ENGINE
# =====================================

mission = Mission(
    uavs,
    tasks,
    failure_simulator=failure_simulator
)

mission.start()


# =====================================
# SCREEN COORDINATES
# =====================================

GRID_X = 60
GRID_Y = 120
GRID_SIZE = 520

PANEL_X = 650


def screen_pos(x, y):

    sx = GRID_X + (x / 20) * GRID_SIZE
    sy = GRID_Y + (y / 20) * GRID_SIZE

    return int(sx), int(sy)


def grid_pos(mouse_x, mouse_y):

    x = round(
        (mouse_x - GRID_X) / GRID_SIZE * 20
    )

    y = round(
        (mouse_y - GRID_Y) / GRID_SIZE * 20
    )

    x = max(0, min(20, x))
    y = max(0, min(20, y))

    return x, y


# =====================================
# MAIN LOOP
# =====================================

running = True
finished = False
timer = 0

next_task_id = max(
    task.id for task in tasks
) + 1


while running:

    dt = clock.tick(60)

    timer += dt


    # =================================
    # EVENTS
    # =================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        # =================================
        # CREATE TASK BY CLICKING MAP
        # =================================

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = event.pos

            if (
                GRID_X <= mouse_x <= GRID_X + GRID_SIZE
                and
                GRID_Y <= mouse_y <= GRID_Y + GRID_SIZE
            ):

                grid_x, grid_y = grid_pos(
                    mouse_x,
                    mouse_y
                )

                new_task = Task(
                    next_task_id,
                    grid_x,
                    grid_y,
                    priority="HIGH"
                )

                created = mission.add_task(
                    new_task
                )

                if created:

                    print(
                        f"\nTASK {new_task.id} CREATED"
                    )

                    print(
                        f"Location: "
                        f"({grid_x}, {grid_y})"
                    )

                    print(
                        f"Assigned UAV: "
                        f"{new_task.assigned_uav}"
                    )

                    next_task_id += 1

                    finished = False

                    timer = 0


    # =================================
    # RUN REAL MISSION
    # =================================

    if not finished and timer >= 350:

        timer = 0

        if not mission.is_complete():

            mission.step()

        else:

            finished = True


    # =================================
    # BACKGROUND
    # =================================

    screen.fill(
        (22, 24, 30)
    )


    # =================================
    # TITLE
    # =================================

    title = title_font.render(
        "UAV-X RESILIENT SWARM",
        True,
        (255, 255, 255)
    )

    screen.blit(
        title,
        (35, 25)
    )


    subtitle = small.render(
        "Resilient Multi-UAV Mission Simulation",
        True,
        (170, 175, 185)
    )

    screen.blit(
        subtitle,
        (37, 62)
    )


    # =================================
    # INTERACTIVE INSTRUCTION
    # =================================

    instruction = small.render(
        "CLICK MAP TO CREATE TASK",
        True,
        (255, 200, 80)
    )

    screen.blit(
        instruction,
        (GRID_X, 88)
    )


    # =================================
    # GRID
    # =================================

    for i in range(21):

        x = GRID_X + i * 26
        y = GRID_Y + i * 26

        pygame.draw.line(
            screen,
            (45, 48, 55),
            (x, GRID_Y),
            (x, GRID_Y + GRID_SIZE)
        )

        pygame.draw.line(
            screen,
            (45, 48, 55),
            (GRID_X, y),
            (GRID_X + GRID_SIZE, y)
        )


    # =================================
    # DRAW UAV PATHS
    # =================================

    for uav in uavs:

        if len(uav.path) < 2:
            continue

        points = [
            screen_pos(x, y)
            for x, y in uav.path
        ]

        if uav.status == "FAILED":

            color = (100, 55, 55)

        else:

            color = (65, 95, 125)

        pygame.draw.lines(
            screen,
            color,
            False,
            points,
            3
        )


    # =================================
    # DRAW TASKS
    # =================================

    for task in tasks:

        x, y = screen_pos(
            task.x,
            task.y
        )

        if task.status == "COMPLETED":

            color = (60, 210, 110)

        elif task.status == "ASSIGNED":

            color = (255, 180, 60)

        else:

            color = (240, 80, 80)


        pygame.draw.circle(
            screen,
            color,
            (x, y),
            11
        )


        label = small.render(
            f"T{task.id}",
            True,
            (255, 255, 255)
        )

        status = tiny.render(
            task.status,
            True,
            (190, 195, 205)
        )


        screen.blit(
            label,
            (x + 16, y - 13)
        )

        screen.blit(
            status,
            (x + 16, y + 5)
        )


    # =================================
    # DRAW UAVS
    # =================================

    for uav in uavs:

        x, y = screen_pos(
            uav.x,
            uav.y
        )


        if uav.status == "FAILED":

            color = (220, 60, 60)

        else:

            color = (50, 170, 255)


        pygame.draw.circle(
            screen,
            color,
            (x, y),
            15
        )


        label = small.render(
            f"UAV {uav.id}",
            True,
            (255, 255, 255)
        )


        screen.blit(
            label,
            (x - 25, y + 20)
        )


    # =================================
    # PANEL
    # =================================

    pygame.draw.rect(
        screen,
        (30, 33, 40),
        (625, 100, 440, 555),
        border_radius=12
    )


    panel_title = title_font.render(
        "MISSION STATUS",
        True,
        (255, 255, 255)
    )

    screen.blit(
        panel_title,
        (PANEL_X, 125)
    )


    # =================================
    # STEP
    # =================================

    screen.blit(
        font.render(
            f"Simulation Step: {mission.step_count}",
            True,
            (210, 215, 225)
        ),
        (PANEL_X, 175)
    )


    # =================================
    # TASK PROGRESS
    # =================================

    completed_tasks = sum(
        task.status == "COMPLETED"
        for task in tasks
    )


    screen.blit(
        font.render(
            f"Mission Progress: "
            f"{completed_tasks}/{len(tasks)} tasks",
            True,
            (210, 215, 225)
        ),
        (PANEL_X, 210)
    )


    # =================================
    # FAILURE COUNT
    # =================================

    failed_count = sum(
        uav.status == "FAILED"
        for uav in uavs
    )


    screen.blit(
        font.render(
            f"UAV Failures: {failed_count}",
            True,
            (210, 215, 225)
        ),
        (PANEL_X, 245)
    )


    # =================================
    # UAV STATUS
    # =================================

    status_title = font.render(
        "UAV STATUS",
        True,
        (255, 255, 255)
    )

    screen.blit(
        status_title,
        (PANEL_X, 295)
    )


    y = 330

    for uav in uavs:

        if uav.status == "FAILED":

            text_color = (240, 80, 80)

        else:

            text_color = (90, 200, 255)


        text = small.render(
            f"UAV {uav.id}: {uav.status}",
            True,
            text_color
        )


        screen.blit(
            text,
            (PANEL_X, y)
        )

        y += 28


    # =================================
    # RECOVERY STATUS
    # =================================

    if failed_count > 0:

        recovery_title = font.render(
            "RESILIENCE EVENT",
            True,
            (255, 255, 255)
        )

        screen.blit(
            recovery_title,
            (PANEL_X, 455)
        )


        screen.blit(
            small.render(
                "UAV 2 failure detected",
                True,
                (240, 90, 90)
            ),
            (PANEL_X, 490)
        )


        screen.blit(
            small.render(
                "Task automatically reassigned",
                True,
                (255, 190, 90)
            ),
            (PANEL_X, 518)
        )


        screen.blit(
            small.render(
                "Mission continued successfully",
                True,
                (90, 210, 130)
            ),
            (PANEL_X, 546)
        )


    # =================================
    # MISSION COMPLETE
    # =================================

    if finished:

        pygame.draw.rect(
            screen,
            (35, 70, 48),
            (PANEL_X, 585, 390, 48),
            border_radius=8
        )


        complete = font.render(
            "MISSION COMPLETE",
            True,
            (90, 230, 130)
        )


        screen.blit(
            complete,
            (PANEL_X + 105, 597)
        )


    pygame.display.flip()


pygame.quit()