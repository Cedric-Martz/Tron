import curses
import time
import random
from collections import deque

def init_colors():
    """
    Initialize color pairs for players and walls.
    """
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)


def draw_walls(stdscr, width, height):
    """
    Draw the border walls of the game area.
    """
    for x in range(width - 1):
        stdscr.addstr(0, x, " ", curses.color_pair(3))
        stdscr.addstr(height - 1, x, " ", curses.color_pair(3))
    for y in range(height - 1):
        stdscr.addstr(y, 0, " ", curses.color_pair(3))
        stdscr.addstr(y, width - 1, " ", curses.color_pair(3))


def menu(stdscr):
    """
    Display the main menu and return the chosen game mode.
    """
    stdscr.clear()
    stdscr.addstr(2, 2, "=== TRON ===", curses.A_BOLD)
    stdscr.addstr(4, 2, "1. Play vs AI")
    stdscr.addstr(5, 2, "2. Multiplayer (2 players)")
    stdscr.addstr(6, 2, "3. Multiplayer (3 players)")
    stdscr.addstr(7, 2, "4. Multiplayer (4 players)")
    stdscr.addstr(9, 2, "Choose an option (1/2/3/4): ")
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key in [ord('1'), ord('2'), ord('3'), ord('4')]:
            return int(chr(key))


def difficulty_menu(stdscr):
    """
    Display the difficulty selection menu and return the chosen difficulty.
    """
    difficulties = [
        "dumb as fuck",
        "easy",
        "medium",
        "hard",
        "harder",
        "you will die"
    ]
    stdscr.clear()
    stdscr.addstr(2, 2, "Choose AI difficulty:", curses.A_BOLD)
    for idx, diff in enumerate(difficulties):
        stdscr.addstr(4 + idx, 4, f"{idx+1}. {diff}")
    stdscr.addstr(11, 2, "Select (1-6): ")
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key in [ord(str(i)) for i in range(1, 7)]:
            return key - ord('1')


def configure_keys(stdscr, player_name):
    """
    Ask the user to configure movement keys for a player.
    Returns a dict with key codes for UP, DOWN, LEFT, RIGHT.
    """
    stdscr.clear()
    stdscr.addstr(2, 2, f"Key configuration for {player_name}:", curses.A_BOLD)
    stdscr.addstr(4, 2, "Press the key for UP: ")
    stdscr.refresh()
    up = stdscr.getch()
    stdscr.addstr(5, 2, "Press the key for DOWN: ")
    stdscr.refresh()
    down = stdscr.getch()
    stdscr.addstr(6, 2, "Press the key for LEFT: ")
    stdscr.refresh()
    left = stdscr.getch()
    stdscr.addstr(7, 2, "Press the key for RIGHT: ")
    stdscr.refresh()
    right = stdscr.getch()
    stdscr.clear()
    stdscr.refresh()
    return {'UP': up, 'DOWN': down, 'LEFT': left, 'RIGHT': right}


def reset_players(width, height, num_players, colors, old_players=None):
    """
    Initialize player positions, directions, trails, colors, and scores.
    """
    positions = [
        (width // 4, height // 2, 1, 0),
        (3 * width // 4, height // 2, -1, 0),
        (width // 2, height // 4, 0, 1),
        (width // 2, 3 * height // 4, 0, -1),
    ]
    players = []
    for i in range(num_players):
        color_idx = colors[i % len(colors)]
        score_choice = old_players[i]['score_choice'] if old_players else 0
        players.append({
            'x': positions[i][0],
            'y': positions[i][1],
            'delta_x': positions[i][2],
            'delta_y': positions[i][3],
            'trail': set(),
            'color': color_idx,
            'score_choice': score_choice
        })
    return players


def draw_scores(stdscr, players, width):
    """
    Display the scores of all players at the top of the screen,
    """
    color_names = {1: "GREEN", 2: "RED", 4: "CYAN", 6: "BLUE"}
    x = width // 2
    total_len = sum(len(color_names.get(p['color'], "P")) + len(f":{p['score_choice']}  ") for p in players)
    x -= total_len // 2
    for p in players:
        name = color_names.get(p['color'], "P")
        score_str = f"{name}:{p['score_choice']}  "
        stdscr.addstr(0, x, name, curses.color_pair(p['color']) | curses.A_BOLD)
        stdscr.addstr(0, x + len(name), f":{p['score_choice']}  ", curses.A_BOLD)
        x += len(score_str)


def draw_trails(stdscr, players):
    """f
    Draw the trails for all players.
    """
    for p in players:
        for trail_x, trail_y in p['trail']:
            stdscr.addstr(trail_y, trail_x, "O", curses.color_pair(p['color']))


def handle_pause(stdscr, width, height):
    """
    Pause the game when space is pressed, resume on next space.
    """
    stdscr.addstr(height // 2, width // 2 - 3, "PAUSE", curses.A_BOLD)
    stdscr.refresh()
    while True:
        k = stdscr.getch()
        if k == ord(' '):
            stdscr.clear()
            break
        time.sleep(0.05)


def handle_player_input(key, players, touches_list):
    """
    Update player directions based on key input and configured keys.
    """
    opposites = {(0, -1): (0, 1), (0, 1): (0, -1), (1, 0): (-1, 0), (-1, 0): (1, 0)}
    for idx, touches in enumerate(touches_list):
        if touches:
            generic_position_x, generic_position_y = players[idx]['delta_x'], players[idx]['delta_y']
            if key == touches['UP'] and (generic_position_x, generic_position_y) != (0, 1):
                players[idx]['delta_x'], players[idx]['delta_y'] = 0, -1
            elif key == touches['DOWN'] and (generic_position_x, generic_position_y) != (0, -1):
                players[idx]['delta_x'], players[idx]['delta_y'] = 0, 1
            elif key == touches['LEFT'] and (generic_position_x, generic_position_y) != (1, 0):
                players[idx]['delta_x'], players[idx]['delta_y'] = -1, 0
            elif key == touches['RIGHT'] and (generic_position_x, generic_position_y) != (-1, 0):
                players[idx]['delta_x'], players[idx]['delta_y'] = 1, 0


def handle_default_input(key, players):
    """
    Update player 1 direction using arrow keys.
    """
    generic_position_x, generic_position_y = players[0]['delta_x'], players[0]['delta_y']
    if key == curses.KEY_UP and (generic_position_x, generic_position_y) != (0, 1):
        players[0]['delta_x'], players[0]['delta_y'] = 0, -1
    elif key == curses.KEY_DOWN and (generic_position_x, generic_position_y) != (0, -1):
        players[0]['delta_x'], players[0]['delta_y'] = 0, 1
    elif key == curses.KEY_LEFT and (generic_position_x, generic_position_y) != (1, 0):
        players[0]['delta_x'], players[0]['delta_y'] = -1, 0
    elif key == curses.KEY_RIGHT and (generic_position_x, generic_position_y) != (-1, 0):
        players[0]['delta_x'], players[0]['delta_y'] = 1, 0


def get_possible_moves(p_ai, p_human, width, height):
    """
    Returns a list of possible moves (delta_x, delta_y) that do not collide with walls or trails.
    """
    possible_moves = [(0, -1), (0, 1), (1, 0), (-1, 0)]
    safe_moves = []
    for delta_x, delta_y in possible_moves:
        next_tested_position_x, next_tested_position_y = p_ai['x'] + delta_x, p_ai['y'] + delta_y
        if (next_tested_position_x <= 0 or next_tested_position_x >= width - 1 or next_tested_position_y <= 0 or next_tested_position_y >= height - 1):
            continue
        if (next_tested_position_x, next_tested_position_y) in p_ai['trail'] or (next_tested_position_x, next_tested_position_y) in p_human['trail']:
            continue
        safe_moves.append((delta_x, delta_y))
    return safe_moves



def flood_fill_space(start_x, start_y, width, height, ai_trail, human_trail, max_depth=20):
    """
    Explore the space around (start_x, start_y) using BFS,
    """
    visited = set()
    queue = deque()
    queue.append((start_x, start_y, 0))

    while queue:
        x, y, depth = queue.popleft()
        if (x, y) in visited or depth > max_depth:
            continue
        if x <= 0 or x >= width - 1 or y <= 0 or y >= height - 1:
            continue
        if (x, y) in ai_trail or (x, y) in human_trail:
            continue

        visited.add((x, y))
        for delta_x, delta_y in [(-1,0), (1,0), (0,-1), (0,1)]:
            queue.append((x + delta_x, y + delta_y, depth + 1))

    return len(visited)



def open_space(p_ai, p_human, width, height, delta_x, delta_y, depth):
    """
    Returns the number of open spaces in the direction (delta_x, delta_y) up to 'depth'.
    """
    next_tested_position_x, next_tested_position_y = p_ai['x'], p_ai['y']
    count = 0
    for _ in range(1, depth + 1):
        next_tested_position_x += delta_x
        next_tested_position_y += delta_y
        if (next_tested_position_x <= 0 or next_tested_position_x >= width - 1 or next_tested_position_y <= 0 or next_tested_position_y >= height - 1):
            break
        if (next_tested_position_x, next_tested_position_y) in p_ai['trail'] or (next_tested_position_x, next_tested_position_y) in p_human['trail']:
            break
        count += 1
    return count


def is_player_facing(ai_pos, human_pos, human_dir, max_distance=3):
    delta_x, delta_y = human_dir
    for i in range(1, max_distance + 1):
        generic_position_x = human_pos['x'] + delta_x * i
        generic_position_y = human_pos['y'] + delta_y * i
        if (generic_position_x, generic_position_y) == (ai_pos['x'], ai_pos['y']):
            return True
    return False


def ai_level_1(p_ai, p_human, width, height, safe_moves):
    """
    Level 1: Prefer current direction, else random safe move.
    """
    if (p_ai['delta_x'], p_ai['delta_y']) in safe_moves and random.random() < 0.85:
        return (p_ai['delta_x'], p_ai['delta_y'])
    elif safe_moves:
        straight = [move for move in safe_moves if move == (p_ai['delta_x'], p_ai['delta_y'])]
        if straight:
            return straight[0]
        else:
            return random.choice(safe_moves)
    return (p_ai['delta_x'], p_ai['delta_y'])


def ai_level_2(p_ai, p_human, width, height, safe_moves):
    """
    Level 2: Maximize open space in chosen direction.
    """
    if safe_moves:
        return max(safe_moves, key=lambda m: open_space(p_ai, p_human, width, height, m[0], m[1], 5))
    return (p_ai['delta_x'], p_ai['delta_y'])


def ai_level_3(p_ai, p_human, width, height, safe_moves):
    """
    Level 3: Maximize open space, minimize distance to human.
    """
    if safe_moves:
        human_x, human_y = p_human['x'], p_human['y']
        ai_x, ai_y = p_ai['x'], p_ai['y']
        def score_choice(m):
            next_tested_position_x, next_tested_position_y = ai_x + m[0], ai_y + m[1]
            return (-open_space(p_ai, p_human, width, height, m[0], m[1], 11),
                    abs(next_tested_position_x - human_x) + abs(next_tested_position_y - human_y))
        return min(safe_moves, key=score_choice)
    return (p_ai['delta_x'], p_ai['delta_y'])


def ai_level_4(p_ai, p_human, width, height, safe_moves):
    """
    Level 4: Minimize distance to human, then maximize open space.
    """
    if safe_moves:
        human_x, human_y = p_human['x'], p_human['y']
        ai_x, ai_y = p_ai['x'], p_ai['y']
        def score_choice(m):
            next_tested_position_x, next_tested_position_y = ai_x + m[0], ai_y + m[1]
            return (abs(next_tested_position_x - human_x) + abs(next_tested_position_y - human_y),
                    -open_space(p_ai, p_human, width, height, m[0], m[1], 11))
        return min(safe_moves, key=score_choice)
    return (p_ai['delta_x'], p_ai['delta_y'])


def ai_level_5(p_ai, p_human, width, height, safe_moves):
    """
    Level 5: Balanced AI. Avoids direct confrontation if too close, 
    favors space and centrality, mixes attack/defense.
    """
    if not safe_moves:
        return (p_ai['delta_x'], p_ai['delta_y'])

    human_x, human_y = p_human['x'], p_human['y']
    ai_x, ai_y = p_ai['x'], p_ai['y']
    center_x, center_y = width // 2, height // 2

    player_threat = is_player_facing(p_ai, p_human, (p_human['delta_x'], p_human['delta_y']), max_distance=3)

    def score_choice(m):
        next_tested_position_x, next_tested_position_y = ai_x + m[0], ai_y + m[1]
        dist_to_human = abs(next_tested_position_x - human_x) + abs(next_tested_position_y - human_y)
        space = open_space(p_ai, p_human, width, height, m[0], m[1], 15)
        dist_to_center = abs(next_tested_position_x - center_x) + abs(next_tested_position_y - center_y)

        threat_penalty = 5 if player_threat and m == (-p_human['delta_x'], -p_human['delta_y']) else 0

        return (-space + dist_to_human * 0.3 + dist_to_center * 0.2 + threat_penalty)

    return min(safe_moves, key=score_choice)



def ai_level_6(p_ai, p_human, width, height, safe_moves):
    """
    Level 6: Expert AI. Combines global awareness, flood-fill, 
    predictive avoidance, fluidity, and offensive potential.
    """
    if not safe_moves:
        return (p_ai['delta_x'], p_ai['delta_y'])

    human_x, human_y = p_human['x'], p_human['y']
    ai_x, ai_y = p_ai['x'], p_ai['y']
    center_x, center_y = width // 2, height // 2

    def score_choice(m):
        next_tested_position_x, next_tested_position_y = ai_x + m[0], ai_y + m[1]
        dist_to_human = abs(next_tested_position_x - human_x) + abs(next_tested_position_y - human_y)
        dist_to_center = abs(next_tested_position_x - center_x) + abs(next_tested_position_y - center_y)
        space = flood_fill_space(next_tested_position_x, next_tested_position_y, width, height, p_ai['trail'], p_human['trail'])
        same_dir = 0 if m == (p_ai['delta_x'], p_ai['delta_y']) else 1
        toward_player = 1 if (m[0], m[1]) == (1 if human_x > ai_x else -1 if human_x < ai_x else 0,
                                              1 if human_y > ai_y else -1 if human_y < ai_y else 0) else 0
        return (-space * 2 + dist_to_human * 0.4 + dist_to_center * 0.3 + same_dir * 1.2 - toward_player * 1.5)
    return min(safe_moves, key=score_choice)



def ai_choose_move(p_ai, p_human, width, height, safe_moves, difficulty):
    """
    Chooses the AI's move based on the difficulty and safe moves.
    """
    if difficulty == 0:
        possible_moves = [(0, -1), (0, 1), (1, 0), (-1, 0)]
        if random.random() < 0.5 or not safe_moves:
            return random.choice(possible_moves)
        else:
            return random.choice(safe_moves)
    elif difficulty == 1:
        return ai_level_1(p_ai, p_human, width, height, safe_moves)
    elif difficulty == 2:
        return ai_level_2(p_ai, p_human, width, height, safe_moves)
    elif difficulty == 3:
        return ai_level_3(p_ai, p_human, width, height, safe_moves)
    elif difficulty == 4:
        return ai_level_4(p_ai, p_human, width, height, safe_moves)
    elif difficulty == 5:
        return ai_level_5(p_ai, p_human, width, height, safe_moves)
    elif difficulty == 6:
        return ai_level_6(p_ai, p_human, width, height, safe_moves)
    return (p_ai['delta_x'], p_ai['delta_y'])


def ai_move(p_ai, p_human, width, height, difficulty=0):
    """
    AI for player 2: choose a move based on difficulty.
    difficulty: 0 (dumb as fuck), 1 (easy), 2 (medium), 3 (hard), 4 (harder), 5 (you will die)
    """
    safe_moves = get_possible_moves(p_ai, p_human, width, height)
    move = ai_choose_move(p_ai, p_human, width, height, safe_moves, difficulty)
    p_ai['delta_x'], p_ai['delta_y'] = move


def move_players(players):
    """
    Move all players one step in their current direction.
    """
    for p in players:
        p['x'] += p['delta_x']
        p['y'] += p['delta_y']


def check_collisions(players, width, height):
    """
    Check for collisions for all players.
    Returns the index of the player who crashed, or None.
    """
    for idx, p in enumerate(players):
        head = (p['x'], p['y'])
        if (head in p['trail'] or
            p['x'] <= 0 or p['x'] >= width - 1 or
            p['y'] <= 0 or p['y'] >= height - 1 or
            any(head in other['trail'] for other in players)):
            return idx
    return None


def update_trails(players):
    """
    Add the current head position to each player's trail.
    """
    for p in players:
        p['trail'].add((p['x'], p['y']))


def award_points(players, crashed_idx):
    """
    Award a point to all players except the one who crashed.
    """
    for idx, p in enumerate(players):
        if idx != crashed_idx:
            p['score_choice'] += 1


def tron_game_loop(stdscr, touches_list=None, ai_difficulty=0):
    """
    Main game loop for multiplayer and AI modes.
    """
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.keypad(True)
    init_colors()
    height, width = stdscr.getmaxyx()
    colors = [1, 2, 4, 6]
    num_players = len(touches_list) if touches_list else 2
    players = reset_players(width, height, num_players, colors)
    while True:
        draw_walls(stdscr, width, height)
        draw_scores(stdscr, players, width)
        draw_trails(stdscr, players)
        move_players(players)
        crashed_idx = check_collisions(players, width, height)
        if crashed_idx is not None:
            award_points(players, crashed_idx)
            players = reset_players(width, height, num_players, colors, players)
            stdscr.clear()
            continue
        update_trails(players)
        key = stdscr.getch()
        if key in (3, 4, 27): # CTRL+C, CTRL+D, ESC closes the game
            curses.endwin()
            exit(0)
        if key == ord(' '):
            handle_pause(stdscr, width, height)
            continue
        if touches_list:
            handle_player_input(key, players, touches_list)
        else:
            handle_default_input(key, players)
            if len(players) > 1:
                ai_move(players[1], players[0], width, height, ai_difficulty)
        stdscr.refresh()
        time.sleep(0.08)


def main_menu_and_game(stdscr):
    """
    Main entry point: show menu, configure keys, and start the game.
    """
    while True:
        choice = menu(stdscr)
        stdscr.clear()
        if choice == 1:
            ai_difficulty = difficulty_menu(stdscr)
            stdscr.clear()
            tron_game_loop(stdscr, ai_difficulty=ai_difficulty)
        else:
            touches_list = []
            for i in range(choice):
                touches_list.append(configure_keys(stdscr, f"Player {i+1}"))

            if len(touches_list) != choice:
                continue
            tron_game_loop(stdscr, touches_list)


if __name__ == "__main__":
    try:
        curses.wrapper(main_menu_and_game)
    except KeyboardInterrupt:
        pass
    curses.endwin()
