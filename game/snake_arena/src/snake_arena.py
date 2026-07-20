import random
import sys
from dataclasses import dataclass

import pygame
from utils.constants import (
    BLACK,
    BLUE,
    GRAY,
    GREEN,
    ORANGE,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    VIOLET,
    WHITE,
    YELLOW,
)

GRID_WIDTH = 40
GRID_HEIGHT = 28
CELL_SIZE = 20
BOARD_WIDTH = GRID_WIDTH * CELL_SIZE
BOARD_HEIGHT = GRID_HEIGHT * CELL_SIZE
BOARD_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2
BOARD_Y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2

ROUND_TIME_SECONDS = 30
ROUND_COUNTDOWN_SECONDS = 3
ROUND_RESULT_SECONDS = 2
MAX_ROUNDS = 5
TARGET_ROUND_WINS = 3

INITIAL_LENGTH = 6
MIN_SURVIVE_LENGTH = 2
DAMAGE_LENGTH = 3
INVULNERABLE_SECONDS = 0.6
SHIELD_INVULNERABLE_SECONDS = 0.3
SPEED_BOOST_SECONDS = 3.0
POWERUP_SPAWN_INTERVAL_SECONDS = 6
DOUBLE_FOOD_CHARGES = 2
BITE_SEGMENTS = 1
BITE_COOLDOWN_SECONDS = 0.5
EVENT_INTERVAL_SECONDS = 18
EVENT_DURATION_SECONDS = 10

START_SPEED = 8.0
MAX_SPEED = 13.0
SPEED_STEP_SECONDS = 20
FPS = 60

PLAYER_COLORS = [RED, BLUE, GRAY, GREEN]

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

PLAYER_CONTROLS = [
    {pygame.K_w: UP, pygame.K_s: DOWN, pygame.K_a: LEFT, pygame.K_d: RIGHT},
    {pygame.K_UP: UP, pygame.K_DOWN: DOWN, pygame.K_LEFT: LEFT, pygame.K_RIGHT: RIGHT},
    {pygame.K_t: UP, pygame.K_g: DOWN, pygame.K_f: LEFT, pygame.K_h: RIGHT},
    {pygame.K_i: UP, pygame.K_k: DOWN, pygame.K_j: LEFT, pygame.K_l: RIGHT},
]

SPAWN_DATA = [
    ((5, 5), RIGHT),
    ((GRID_WIDTH - 6, GRID_HEIGHT - 6), LEFT),
    ((GRID_WIDTH - 6, 5), LEFT),
    ((5, GRID_HEIGHT - 6), RIGHT),
]

POWERUP_SPEED = "speed"
POWERUP_SHIELD = "shield"
POWERUP_DOUBLE_FOOD = "double_food"
POWERUP_TYPES = [POWERUP_SPEED, POWERUP_SHIELD, POWERUP_DOUBLE_FOOD]

EVENT_FOOD_FRENZY = "food_frenzy"
EVENT_GLOBAL_SHIELD = "global_shield"
EVENT_DOUBLE_FOOD_SCORE = "double_food_score"
EVENT_TYPES = [EVENT_FOOD_FRENZY, EVENT_GLOBAL_SHIELD, EVENT_DOUBLE_FOOD_SCORE]
EVENT_LABELS = {
    EVENT_FOOD_FRENZY: "Event: Food Frenzy (+1 food)",
    EVENT_GLOBAL_SHIELD: "Event: Global Shield (+1 shield)",
    EVENT_DOUBLE_FOOD_SCORE: "Event: Double Food Score (2x)",
}
EVENT_COLORS = {
    EVENT_FOOD_FRENZY: ORANGE,
    EVENT_GLOBAL_SHIELD: BLUE,
    EVENT_DOUBLE_FOOD_SCORE: GREEN,
}


@dataclass
class PowerUpState:
    position: tuple[int, int]
    power_type: str


@dataclass
class EventState:
    event_type: str
    ends_at: float


@dataclass
class SnakeState:
    player_id: int
    color: tuple[int, int, int]
    body: list[tuple[int, int]]
    direction: tuple[int, int]
    next_direction: tuple[int, int]
    alive: bool = True
    pending_growth: int = 0
    round_food: int = 0
    invulnerable_until: float = 0.0
    shield_charges: int = 0
    speed_boost_until: float = 0.0
    double_food_charges: int = 0
    speed_extra_progress: float = 0.0
    bite_cooldown_until: float = 0.0


def is_reverse(current_direction, candidate_direction):
    return (
        current_direction[0] == -candidate_direction[0]
        and current_direction[1] == -candidate_direction[1]
    )


def in_bounds(cell):
    x, y = cell
    return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT


def create_body_from_head(head, direction, length):
    dx, dy = direction
    return [(head[0] - dx * i, head[1] - dy * i) for i in range(length)]


def spawn_players(num_players):
    players = []
    for idx in range(num_players):
        head, direction = SPAWN_DATA[idx]
        body = create_body_from_head(head, direction, INITIAL_LENGTH)
        players.append(
            SnakeState(
                player_id=idx + 1,
                color=PLAYER_COLORS[idx],
                body=body,
                direction=direction,
                next_direction=direction,
            )
        )
    return players


def occupied_cells(players):
    cells = set()
    for snake in players:
        if snake.alive:
            cells.update(snake.body)
    return cells


def get_target_food_count(num_players):
    if num_players >= 3:
        return 2
    return 1


def spawn_food(players, foods=None, powerup=None):
    blocked = occupied_cells(players)
    for food in foods or []:
        blocked.add(food)
    if powerup is not None:
        blocked.add(powerup.position)
    free_cells = [
        (x, y)
        for x in range(GRID_WIDTH)
        for y in range(GRID_HEIGHT)
        if (x, y) not in blocked
    ]
    if not free_cells:
        return None
    return random.choice(free_cells)


def spawn_powerup(players, foods, existing_powerup):
    blocked = occupied_cells(players)
    for food in foods:
        blocked.add(food)
    if existing_powerup is not None:
        blocked.add(existing_powerup.position)

    free_cells = [
        (x, y)
        for x in range(GRID_WIDTH)
        for y in range(GRID_HEIGHT)
        if (x, y) not in blocked
    ]
    if not free_cells:
        return None

    return PowerUpState(
        position=random.choice(free_cells),
        power_type=random.choice(POWERUP_TYPES),
    )


def find_safe_position_for_snake(snake, players, target_length=None):
    preferred_head, preferred_dir = SPAWN_DATA[snake.player_id - 1]
    snake_length = target_length if target_length is not None else len(snake.body)
    candidates = [preferred_head]
    for y in range(2, GRID_HEIGHT - 2):
        for x in range(2, GRID_WIDTH - 2):
            candidates.append((x, y))

    for head in candidates:
        body = create_body_from_head(head, preferred_dir, snake_length)
        if all(in_bounds(cell) for cell in body):
            blocked = set()
            for other in players:
                if other.player_id != snake.player_id and other.alive:
                    blocked.update(other.body)
            if not any(cell in blocked for cell in body):
                snake.body = body
                snake.direction = preferred_dir
                snake.next_direction = preferred_dir
                return True
    return False


def apply_damage(snake, players, now_seconds):
    if snake.shield_charges > 0:
        snake.shield_charges -= 1
        snake.invulnerable_until = now_seconds + SHIELD_INVULNERABLE_SECONDS
        return
    if not snake.alive:
        return

    new_length = max(MIN_SURVIVE_LENGTH, len(snake.body) - DAMAGE_LENGTH)
    snake.body = snake.body[:new_length]

    if not find_safe_position_for_snake(snake, players, new_length):
        # Fallback: keep the snake alive at minimum length even in crowded states.
        preferred_head, preferred_dir = SPAWN_DATA[snake.player_id - 1]
        snake.body = create_body_from_head(
            preferred_head, preferred_dir, MIN_SURVIVE_LENGTH
        )
        snake.direction = preferred_dir
        snake.next_direction = preferred_dir

    snake.alive = True
    snake.invulnerable_until = now_seconds + INVULNERABLE_SECONDS


def apply_powerup(snake, powerup_type, now_seconds):
    if powerup_type == POWERUP_SPEED:
        snake.speed_boost_until = (
            max(snake.speed_boost_until, now_seconds) + SPEED_BOOST_SECONDS
        )
    elif powerup_type == POWERUP_SHIELD:
        snake.shield_charges += 1
    elif powerup_type == POWERUP_DOUBLE_FOOD:
        snake.double_food_charges += DOUBLE_FOOD_CHARGES


def apply_event(players, event_type):
    if event_type == EVENT_GLOBAL_SHIELD:
        for snake in players:
            if snake.alive:
                snake.shield_charges += 1


def get_snake_steps_for_tick(snake, now_seconds):
    steps = 1
    if now_seconds < snake.speed_boost_until:
        snake.speed_extra_progress += 0.5
        if snake.speed_extra_progress >= 1.0:
            steps += 1
            snake.speed_extra_progress -= 1.0
    else:
        snake.speed_extra_progress = 0.0
    return steps


def get_tick_speed(round_elapsed_seconds):
    increments = int(round_elapsed_seconds // SPEED_STEP_SECONDS)
    return min(START_SPEED + increments, MAX_SPEED)


def cell_rect(cell, inset=0):
    x, y = cell
    return pygame.Rect(
        BOARD_X + x * CELL_SIZE + inset,
        BOARD_Y + y * CELL_SIZE + inset,
        CELL_SIZE - inset * 2,
        CELL_SIZE - inset * 2,
    )


def draw_cell(screen, cell, color):
    pygame.draw.rect(screen, color, cell_rect(cell))


def darken_color(color, factor=0.65):
    return tuple(max(0, min(255, int(channel * factor))) for channel in color)


def draw_powerup_marker(screen, powerup):
    rect = cell_rect(powerup.position)
    pygame.draw.rect(screen, VIOLET, rect)
    inner = rect.inflate(-6, -6)

    if powerup.power_type == POWERUP_SPEED:
        pygame.draw.polygon(
            screen,
            WHITE,
            [
                (inner.left + 1, inner.centery - 3),
                (inner.centerx - 1, inner.centery),
                (inner.left + 1, inner.centery + 3),
            ],
        )
        pygame.draw.polygon(
            screen,
            WHITE,
            [
                (inner.centerx + 1, inner.centery - 3),
                (inner.right - 1, inner.centery),
                (inner.centerx + 1, inner.centery + 3),
            ],
        )
    elif powerup.power_type == POWERUP_SHIELD:
        pygame.draw.circle(screen, WHITE, inner.center, max(3, inner.width // 2), 2)
    elif powerup.power_type == POWERUP_DOUBLE_FOOD:
        font = pygame.font.Font(None, 16)
        label = font.render("2x", True, WHITE)
        screen.blit(
            label,
            (
                rect.centerx - label.get_width() // 2,
                rect.centery - label.get_height() // 2,
            ),
        )


def draw_event_visual(screen, active_event):
    if active_event is None:
        return
    color = EVENT_COLORS[active_event.event_type]
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT)
    overlay = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
    overlay.fill((*color, 22))
    screen.blit(overlay, (BOARD_X, BOARD_Y))
    pygame.draw.rect(screen, color, board_rect, 3)


def draw_powerup_legend(screen):
    font = pygame.font.Font(None, 22)
    tiny = pygame.font.Font(None, 14)
    legend_x = BOARD_X + BOARD_WIDTH + 10
    legend_y = BOARD_Y + 14
    screen.blit(font.render("Powerups", True, WHITE), (legend_x, legend_y))

    entries = [
        (POWERUP_SPEED, "Speed"),
        (POWERUP_SHIELD, "Shield"),
        (POWERUP_DOUBLE_FOOD, "2x Food"),
    ]
    for idx, (power_type, label_text) in enumerate(entries):
        y = legend_y + 24 + idx * 24
        pygame.draw.rect(screen, VIOLET, pygame.Rect(legend_x, y, 16, 16))
        if power_type == POWERUP_SPEED:
            pygame.draw.polygon(
                screen,
                WHITE,
                [(legend_x + 3, y + 5), (legend_x + 7, y + 8), (legend_x + 3, y + 11)],
            )
            pygame.draw.polygon(
                screen,
                WHITE,
                [
                    (legend_x + 9, y + 5),
                    (legend_x + 13, y + 8),
                    (legend_x + 9, y + 11),
                ],
            )
        elif power_type == POWERUP_SHIELD:
            pygame.draw.circle(screen, WHITE, (legend_x + 8, y + 8), 5, 2)
        else:
            screen.blit(tiny.render("2x", True, WHITE), (legend_x + 2, y + 3))
        screen.blit(font.render(label_text, True, WHITE), (legend_x + 22, y))


def draw_board(screen, players, foods, powerup, active_event=None):
    screen.fill(BLACK)
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT)
    pygame.draw.rect(screen, (20, 20, 20), board_rect)

    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if (x + y) % 2 == 0:
                rect = pygame.Rect(
                    BOARD_X + x * CELL_SIZE,
                    BOARD_Y + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )
                pygame.draw.rect(screen, (26, 26, 26), rect)

    draw_event_visual(screen, active_event)
    pygame.draw.rect(screen, WHITE, board_rect, 2)

    for food in foods:
        draw_cell(screen, food, YELLOW)
    if powerup is not None:
        draw_powerup_marker(screen, powerup)

    draw_powerup_legend(screen)

    now_seconds = pygame.time.get_ticks() / 1000.0
    for snake in players:
        if not snake.alive:
            continue
        flashing = (
            now_seconds < snake.invulnerable_until and int(now_seconds * 12) % 2 == 0
        )
        if flashing:
            continue
        snake_draw_color = (
            darken_color(snake.color) if snake.shield_charges > 0 else snake.color
        )
        for segment in snake.body:
            draw_cell(screen, segment, snake_draw_color)


def draw_hud(
    screen,
    players,
    round_wins,
    round_index,
    round_time_left,
    now_seconds,
    active_event,
):
    hud_font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 24)
    timer_text = hud_font.render(
        f"Round {round_index}/{MAX_ROUNDS}  Time: {round_time_left}", True, WHITE
    )
    screen.blit(timer_text, (12, 8))
    if active_event is not None:
        remaining = max(0, int(active_event.ends_at - now_seconds))
        event_color = EVENT_COLORS[active_event.event_type]
        banner = pygame.Rect(10, 28, 340, 20)
        pygame.draw.rect(screen, event_color, banner, border_radius=6)
        pygame.draw.rect(screen, WHITE, banner, 1, border_radius=6)
        event_text = small_font.render(
            f"{EVENT_LABELS[active_event.event_type]}  {remaining}s", True, BLACK
        )
        screen.blit(event_text, (banner.x + 8, banner.y + 2))

    base_y = 52
    for idx, snake in enumerate(players):
        length = len(snake.body) if snake.alive else 0
        effects = []
        if snake.shield_charges > 0:
            effects.append(f"Shield:{snake.shield_charges}")
        if now_seconds < snake.speed_boost_until:
            speed_left = max(0, int(snake.speed_boost_until - now_seconds))
            effects.append(f"Speed:{speed_left}s")
        if snake.double_food_charges > 0:
            effects.append(f"2xFood:{snake.double_food_charges}")
        if now_seconds < snake.bite_cooldown_until:
            bite_left = max(0, int((snake.bite_cooldown_until - now_seconds) * 10))
            effects.append(f"BiteCD:{bite_left / 10:.1f}s")
        effect_text = f"  {' | '.join(effects)}" if effects else ""
        text = (
            f"P{snake.player_id}  Wins:{round_wins[idx]}  "
            f"Len:{length}  Food:{snake.round_food}{effect_text}"
        )
        label = small_font.render(text, True, snake.color)
        screen.blit(label, (12, base_y + idx * 22))


def draw_center_message(screen, message, sub_message=None):
    title_font = pygame.font.Font(None, 68)
    sub_font = pygame.font.Font(None, 36)
    title = title_font.render(message, True, WHITE)
    screen.blit(
        title,
        (
            SCREEN_WIDTH // 2 - title.get_width() // 2,
            SCREEN_HEIGHT // 2 - title.get_height(),
        ),
    )
    if sub_message:
        sub = sub_font.render(sub_message, True, YELLOW)
        screen.blit(
            sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, SCREEN_HEIGHT // 2 + 10)
        )


def process_direction_key(event, players):
    if event.type != pygame.KEYDOWN:
        return
    for idx, snake in enumerate(players):
        if not snake.alive:
            continue
        controls = PLAYER_CONTROLS[idx]
        if event.key in controls:
            candidate = controls[event.key]
            if not is_reverse(snake.direction, candidate):
                snake.next_direction = candidate


def move_snakes_one_tick(players, now_seconds):
    old_heads = {}
    planned_heads = {}
    steps_by_player = {}

    for snake in players:
        if not snake.alive:
            continue
        snake.direction = snake.next_direction
        steps_by_player[snake.player_id] = get_snake_steps_for_tick(snake, now_seconds)
        head = snake.body[0]
        old_heads[snake.player_id] = head

    max_steps = max(steps_by_player.values(), default=0)
    for step_index in range(max_steps):
        for snake in players:
            if not snake.alive:
                continue
            if step_index >= steps_by_player[snake.player_id]:
                continue
            current_head = snake.body[0]
            new_head = (
                current_head[0] + snake.direction[0],
                current_head[1] + snake.direction[1],
            )
            planned_heads[snake.player_id] = new_head
            snake.body.insert(0, new_head)
            if snake.pending_growth > 0:
                snake.pending_growth -= 1
            else:
                snake.body.pop()

    return old_heads, planned_heads


def refill_foods(players, foods, powerup, target_food_count):
    while len(foods) < target_food_count:
        new_food = spawn_food(players, foods, powerup)
        if new_food is None:
            break
        foods.append(new_food)


def collect_food(players, foods, round_food_multiplier=1):
    if not foods:
        return False
    eaten = False
    foods_set = set(foods)
    consumed = set()
    for snake in players:
        if snake.alive and snake.body and snake.body[0] in foods_set:
            growth = 1
            if snake.double_food_charges > 0:
                growth = 2
                snake.double_food_charges -= 1
            snake.pending_growth += growth
            snake.round_food += round_food_multiplier
            eaten = True
            consumed.add(snake.body[0])
    if consumed:
        foods[:] = [food for food in foods if food not in consumed]
    return eaten


def collect_powerup(players, powerup, now_seconds):
    if powerup is None:
        return None
    for snake in players:
        if snake.alive and snake.body and snake.body[0] == powerup.position:
            apply_powerup(snake, powerup.power_type, now_seconds)
            power_label = powerup.power_type.replace("_", " ").title()
            return f"P{snake.player_id} got {power_label}"
    return None


def resolve_bites(players, now_seconds):
    bite_immunity = set()
    bite_messages = []

    for attacker in players:
        if not attacker.alive or not attacker.body:
            continue
        if now_seconds < attacker.invulnerable_until:
            continue
        if now_seconds < attacker.bite_cooldown_until:
            continue

        attacker_head = attacker.body[0]
        for defender in players:
            if defender.player_id == attacker.player_id or not defender.alive:
                continue
            if attacker_head not in defender.body[1:]:
                continue

            stealable = max(0, len(defender.body) - MIN_SURVIVE_LENGTH)
            stolen = min(BITE_SEGMENTS, stealable)
            if stolen <= 0:
                break

            defender.body = defender.body[:-stolen]
            attacker.pending_growth += stolen
            attacker.bite_cooldown_until = now_seconds + BITE_COOLDOWN_SECONDS
            bite_immunity.add(attacker.player_id)
            bite_messages.append(
                f"P{attacker.player_id} bit P{defender.player_id} (+{stolen})"
            )
            break

    message = bite_messages[0] if bite_messages else None
    return bite_immunity, message


def gather_collision_victims(
    players, old_heads, planned_heads, now_seconds, bite_immunity
):
    victims = set()
    alive = [snake for snake in players if snake.alive]

    for snake in alive:
        if now_seconds < snake.invulnerable_until:
            continue
        head = snake.body[0]
        if not in_bounds(head):
            victims.add(snake.player_id)

    for snake in alive:
        if snake.player_id in victims:
            continue
        if snake.player_id in bite_immunity:
            continue
        if now_seconds < snake.invulnerable_until:
            continue
        head = snake.body[0]
        if head in snake.body[1:]:
            victims.add(snake.player_id)

    head_map = {}
    for snake in alive:
        head = snake.body[0]
        head_map.setdefault(head, []).append(snake.player_id)
    for ids in head_map.values():
        if len(ids) > 1:
            victims.update(ids)

    for a in alive:
        for b in alive:
            if a.player_id >= b.player_id:
                continue
            if (
                planned_heads[a.player_id] == old_heads[b.player_id]
                and planned_heads[b.player_id] == old_heads[a.player_id]
            ):
                victims.add(a.player_id)
                victims.add(b.player_id)

    for snake in alive:
        if snake.player_id in victims:
            continue
        if now_seconds < snake.invulnerable_until:
            continue
        head = snake.body[0]
        for other in alive:
            if other.player_id == snake.player_id:
                continue
            if head in other.body[1:]:
                victims.add(snake.player_id)
                break

    return victims


def determine_round_winners(players, timed_out):
    alive_players = [snake for snake in players if snake.alive]
    if len(alive_players) == 1:
        return [alive_players[0].player_id - 1]

    if not timed_out:
        return []

    best_length = max((len(snake.body) if snake.alive else 0) for snake in players)
    length_tied = [
        snake
        for snake in players
        if (len(snake.body) if snake.alive else 0) == best_length
    ]
    if len(length_tied) == 1:
        return [length_tied[0].player_id - 1]

    best_food = max(snake.round_food for snake in length_tied)
    food_tied = [snake for snake in length_tied if snake.round_food == best_food]
    return [snake.player_id - 1 for snake in food_tied]


def wait_with_events(clock, seconds):
    start = pygame.time.get_ticks()
    while (pygame.time.get_ticks() - start) < int(seconds * 1000):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
        clock.tick(FPS)
    return True


def run_countdown(screen, clock, players, foods, powerup):
    for remaining in range(ROUND_COUNTDOWN_SECONDS, 0, -1):
        draw_board(screen, players, foods, powerup, None)
        draw_center_message(screen, str(remaining), "Get Ready")
        pygame.display.flip()
        if not wait_with_events(clock, 1):
            return False

    draw_board(screen, players, foods, powerup, None)
    draw_center_message(screen, "GO!")
    pygame.display.flip()
    return wait_with_events(clock, 0.6)


def run_single_round(screen, clock, num_players, round_index, round_wins):
    players = spawn_players(num_players)
    foods = []
    base_food_count = get_target_food_count(num_players)
    powerup = None
    powerup_spawn_at = POWERUP_SPAWN_INTERVAL_SECONDS
    event_spawn_at = EVENT_INTERVAL_SECONDS
    active_event = None
    pickup_message = ""
    pickup_message_until = 0.0

    refill_foods(players, foods, powerup, base_food_count)
    if not run_countdown(screen, clock, players, foods, powerup):
        return players, [], False

    tick_accumulator = 0.0
    timed_out = False
    running = True
    round_start_ms = pygame.time.get_ticks()

    while running:
        dt = clock.tick(FPS) / 1000.0
        tick_accumulator += dt
        now_seconds = pygame.time.get_ticks() / 1000.0
        elapsed = (pygame.time.get_ticks() - round_start_ms) / 1000.0
        round_time_left = max(0, int(ROUND_TIME_SECONDS - elapsed))
        tick_interval = 1.0 / get_tick_speed(elapsed)

        if active_event is not None and now_seconds >= active_event.ends_at:
            active_event = None
            pickup_message = "Event Ended"
            pickup_message_until = now_seconds + 1.2

        if active_event is None and elapsed >= event_spawn_at:
            event_type = random.choice(EVENT_TYPES)
            active_event = EventState(
                event_type=event_type,
                ends_at=now_seconds + EVENT_DURATION_SECONDS,
            )
            apply_event(players, event_type)
            pickup_message = EVENT_LABELS[event_type]
            pickup_message_until = now_seconds + 1.6
            event_spawn_at += EVENT_INTERVAL_SECONDS

        if powerup is None and elapsed >= powerup_spawn_at:
            powerup = spawn_powerup(players, foods, powerup)
            powerup_spawn_at += POWERUP_SPAWN_INTERVAL_SECONDS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return players, [], False
            process_direction_key(event, players)

        while tick_accumulator >= tick_interval:
            tick_accumulator -= tick_interval
            old_heads, planned_heads = move_snakes_one_tick(players, now_seconds)

            food_multiplier = 2 if (
                active_event is not None
                and active_event.event_type == EVENT_DOUBLE_FOOD_SCORE
            ) else 1
            collect_food(players, foods, food_multiplier)

            current_food_target = base_food_count + (
                1
                if active_event is not None
                and active_event.event_type == EVENT_FOOD_FRENZY
                else 0
            )
            refill_foods(players, foods, powerup, current_food_target)

            powerup_message = collect_powerup(players, powerup, now_seconds)
            if powerup_message is not None:
                pickup_message = powerup_message
                pickup_message_until = now_seconds + 1.2
                powerup = None

            bite_immunity, bite_message = resolve_bites(players, now_seconds)
            if bite_message is not None:
                pickup_message = bite_message
                pickup_message_until = now_seconds + 1.0

            victims = gather_collision_victims(
                players, old_heads, planned_heads, now_seconds, bite_immunity
            )
            for snake in players:
                if snake.player_id in victims:
                    apply_damage(snake, players, now_seconds)

            living = sum(1 for snake in players if snake.alive)
            if living <= 1:
                running = False
                break

        if elapsed >= ROUND_TIME_SECONDS:
            timed_out = True
            running = False

        draw_board(screen, players, foods, powerup, active_event)
        draw_hud(
            screen,
            players,
            round_wins,
            round_index,
            round_time_left,
            now_seconds,
            active_event,
        )
        if now_seconds < pickup_message_until:
            draw_center_message(screen, pickup_message)
        pygame.display.flip()

    winners = determine_round_winners(players, timed_out)
    return players, winners, True


def render_result_overlay(screen, players, round_wins, winners):
    now_seconds = pygame.time.get_ticks() / 1000.0
    draw_board(screen, players, [], None)
    draw_hud(screen, players, round_wins, 0, 0, now_seconds, None)
    if len(winners) == 1:
        winner_player = winners[0] + 1
        draw_center_message(screen, f"Round Winner: P{winner_player}")
    elif len(winners) > 1:
        label = ", ".join([f"P{winner + 1}" for winner in winners])
        draw_center_message(screen, "Round Tie", label)
    else:
        draw_center_message(screen, "No Winner")
    pygame.display.flip()


def render_match_winner(screen, winner_index):
    screen.fill(BLACK)
    draw_center_message(
        screen,
        f"Match Winner: P{winner_index + 1}",
        "Press any key to return (ESC also works)",
    )
    pygame.display.flip()


def wait_for_any_key(clock):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return
        clock.tick(FPS)


def snake_arena_game(screen, num_players):
    clock = pygame.time.Clock()
    num_players = max(2, min(4, num_players))
    round_wins = [0 for _ in range(num_players)]
    round_index = 0
    match_winner = None

    while round_index < MAX_ROUNDS and match_winner is None:
        round_index += 1
        players, winners, keep_running = run_single_round(
            screen, clock, num_players, round_index, round_wins
        )
        if not keep_running:
            return

        for idx in winners:
            round_wins[idx] += 1

        for idx, score in enumerate(round_wins):
            if score >= TARGET_ROUND_WINS:
                match_winner = idx
                break

        render_result_overlay(screen, players, round_wins, winners)
        if not wait_with_events(clock, ROUND_RESULT_SECONDS):
            return

    if match_winner is None:
        top_score = max(round_wins)
        tied = [idx for idx, score in enumerate(round_wins) if score == top_score]
        match_winner = tied[0]

    render_match_winner(screen, match_winner)
    wait_for_any_key(clock)
