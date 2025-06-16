import curses
import time
import random

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
        score = old_players[i]['score'] if old_players else 0
        players.append({
            'x': positions[i][0],
            'y': positions[i][1],
            'dx': positions[i][2],
            'dy': positions[i][3],
            'trail': set(),
            'color': color_idx,
            'score': score
        })
    return players

def draw_scores(stdscr, players, width):
    """
    Display the scores of all players at the top of the screen,
    """
    color_names = {1: "GREEN", 2: "RED", 4: "CYAN", 6: "BLUE"}
    x = width // 2
    total_len = sum(len(color_names.get(p['color'], "P")) + len(f":{p['score']}  ") for p in players)
    x -= total_len // 2

    for p in players:
        name = color_names.get(p['color'], "P")
        score_str = f"{name}:{p['score']}  "
        stdscr.addstr(0, x, name, curses.color_pair(p['color']) | curses.A_BOLD)
        stdscr.addstr(0, x + len(name), f":{p['score']}  ", curses.A_BOLD)
        x += len(score_str)

def draw_trails(stdscr, players):
    """f
    Draw the trails for all players.
    """
    for p in players:
        for tx, ty in p['trail']:
            stdscr.addstr(ty, tx, "O", curses.color_pair(p['color']))

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
            px, py = players[idx]['dx'], players[idx]['dy']
            if key == touches['UP'] and (px, py) != (0, 1):
                players[idx]['dx'], players[idx]['dy'] = 0, -1
            elif key == touches['DOWN'] and (px, py) != (0, -1):
                players[idx]['dx'], players[idx]['dy'] = 0, 1
            elif key == touches['LEFT'] and (px, py) != (1, 0):
                players[idx]['dx'], players[idx]['dy'] = -1, 0
            elif key == touches['RIGHT'] and (px, py) != (-1, 0):
                players[idx]['dx'], players[idx]['dy'] = 1, 0

def handle_default_input(key, players):
    """
    Update player 1 direction using arrow keys.
    """
    px, py = players[0]['dx'], players[0]['dy']
    if key == curses.KEY_UP and (px, py) != (0, 1):
        players[0]['dx'], players[0]['dy'] = 0, -1
    elif key == curses.KEY_DOWN and (px, py) != (0, -1):
        players[0]['dx'], players[0]['dy'] = 0, 1
    elif key == curses.KEY_LEFT and (px, py) != (1, 0):
        players[0]['dx'], players[0]['dy'] = -1, 0
    elif key == curses.KEY_RIGHT and (px, py) != (-1, 0):
        players[0]['dx'], players[0]['dy'] = 1, 0

def ai_move(p_ai, p_human, width, height):
    """
    Simple AI for player 2: choose a safe move randomly.
    """
    possible_moves = [(0, -1), (0, 1), (1, 0), (-1, 0)]
    safe_moves = []
    for dx, dy in possible_moves:
        nx, ny = p_ai['x'] + dx, p_ai['y'] + dy
        if (nx <= 0 or nx >= width - 1 or ny <= 0 or ny >= height - 1):
            continue
        if (nx, ny) in p_ai['trail'] or (nx, ny) in p_human['trail']:
            continue
        safe_moves.append((dx, dy))
    if safe_moves:
        if random.random() < 0.2 or (p_ai['dx'], p_ai['dy']) not in safe_moves:
            p_ai['dx'], p_ai['dy'] = random.choice(safe_moves)

def move_players(players):
    """
    Move all players one step in their current direction.
    """
    for p in players:
        p['x'] += p['dx']
        p['y'] += p['dy']

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
            p['score'] += 1

def tron_multiplayer(stdscr, touches_list=None):
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
        if key == ord(' '):
            handle_pause(stdscr, width, height)
            continue

        if touches_list:
            handle_player_input(key, players, touches_list)
        else:
            handle_default_input(key, players)
            if len(players) > 1:
                ai_move(players[1], players[0], width, height)

        stdscr.refresh()
        time.sleep(0.08)


def main_menu_and_game(stdscr):
    """
    Main entry point: show menu, configure keys, and start the game.
    """
    choice = menu(stdscr)
    stdscr.clear()
    if choice == 1:
        tron_multiplayer(stdscr)
    else:
        num_players = choice
        touches_list = []
        for i in range(num_players):
            touches_list.append(configure_keys(stdscr, f"Player {i+1}"))
        tron_multiplayer(stdscr, touches_list)

if __name__ == "__main__":
    try:
        curses.wrapper(main_menu_and_game)
    except KeyboardInterrupt:
        print("GAME STOPPED")
