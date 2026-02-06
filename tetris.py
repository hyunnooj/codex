import pygame
import random
from dataclasses import dataclass

CELL_SIZE = 30
COLUMNS = 10
ROWS = 20
PLAY_WIDTH = COLUMNS * CELL_SIZE
PLAY_HEIGHT = ROWS * CELL_SIZE
SIDE_PANEL = 200
SCREEN_WIDTH = PLAY_WIDTH + SIDE_PANEL
SCREEN_HEIGHT = PLAY_HEIGHT
FPS = 60
DROP_EVENT = pygame.USEREVENT + 1
DROP_INTERVAL_MS = 700
SPEEDUP_INTERVAL_MS = 180000
SPEEDUP_FACTOR = 0.9
MIN_DROP_INTERVAL_MS = 50

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
]

SHAPE_COLORS = [
    (0, 240, 240),
    (240, 240, 0),
    (160, 0, 240),
    (0, 0, 240),
    (240, 160, 0),
    (0, 240, 0),
    (240, 0, 0),
]

BG_COLOR = (18, 18, 20)
GRID_COLOR = (40, 40, 45)
TEXT_COLOR = (240, 240, 240)


@dataclass
class Piece:
    shape: list
    color: tuple
    x: int
    y: int

    @property
    def width(self):
        return len(self.shape[0])

    @property
    def height(self):
        return len(self.shape)


class Tetris:
    def __init__(self):
        self.grid = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False

    def new_piece(self):
        index = random.randint(0, len(SHAPES) - 1)
        shape = SHAPES[index]
        color = SHAPE_COLORS[index]
        x = COLUMNS // 2 - len(shape[0]) // 2
        y = -len(shape)
        return Piece(shape, color, x, y)

    def rotate(self, piece):
        rotated = [list(row) for row in zip(*piece.shape[::-1])]
        return Piece(rotated, piece.color, piece.x, piece.y)

    def valid_position(self, piece, offset_x=0, offset_y=0):
        for row_index, row in enumerate(piece.shape):
            for col_index, cell in enumerate(row):
                if not cell:
                    continue
                x = piece.x + col_index + offset_x
                y = piece.y + row_index + offset_y
                if x < 0 or x >= COLUMNS or y >= ROWS:
                    return False
                if y >= 0 and self.grid[y][x]:
                    return False
        return True

    def lock_piece(self, piece):
        overflowed = False
        for row_index, row in enumerate(piece.shape):
            for col_index, cell in enumerate(row):
                if cell:
                    x = piece.x + col_index
                    y = piece.y + row_index
                    if y < 0:
                        overflowed = True
                        continue
                    self.grid[y][x] = piece.color
        self.clear_lines()
        if overflowed or any(self.grid[0][x] for x in range(COLUMNS)):
            self.game_over = True
            return
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if not self.valid_position(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = ROWS - len(new_grid)
        if cleared:
            for _ in range(cleared):
                new_grid.insert(0, [None for _ in range(COLUMNS)])
            self.grid = new_grid
            self.lines_cleared += cleared
            self.score += (100 * cleared) * cleared

    def hard_drop(self):
        while self.valid_position(self.current_piece, offset_y=1):
            self.current_piece.y += 1
        self.lock_piece(self.current_piece)


class Renderer:
    def __init__(self, screen, font, small_font):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.restart_button_rect = None
        self.restart_button_padding = (12, 8)

    def draw_grid(self, grid):
        for y in range(ROWS):
            for x in range(COLUMNS):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)
                if grid[y][x]:
                    pygame.draw.rect(self.screen, grid[y][x], rect.inflate(-2, -2))

    def draw_piece(self, piece):
        for row_index, row in enumerate(piece.shape):
            for col_index, cell in enumerate(row):
                if cell:
                    x = (piece.x + col_index) * CELL_SIZE
                    y = (piece.y + row_index) * CELL_SIZE
                    if y >= 0:
                        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(self.screen, piece.color, rect.inflate(-2, -2))

    def draw_panel(self, game):
        panel_x = PLAY_WIDTH
        panel_rect = pygame.Rect(panel_x, 0, SIDE_PANEL, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, (26, 26, 30), panel_rect)

        title = self.font.render("TETRIS", True, TEXT_COLOR)
        self.screen.blit(title, (panel_x + 20, 30))

        score_label = self.small_font.render("Score", True, TEXT_COLOR)
        score_value = self.small_font.render(str(game.score), True, TEXT_COLOR)
        self.screen.blit(score_label, (panel_x + 20, 90))
        self.screen.blit(score_value, (panel_x + 20, 115))

        line_label = self.small_font.render("Lines", True, TEXT_COLOR)
        line_value = self.small_font.render(str(game.lines_cleared), True, TEXT_COLOR)
        self.screen.blit(line_label, (panel_x + 20, 160))
        self.screen.blit(line_value, (panel_x + 20, 185))

        next_label = self.small_font.render("Next", True, TEXT_COLOR)
        self.screen.blit(next_label, (panel_x + 20, 235))
        self.draw_next_piece(game.next_piece, panel_x + 20, 270)

        if game.game_over:
            over_text = self.font.render("Game Over", True, (240, 80, 80))
            self.screen.blit(over_text, (panel_x + 20, 360))
            prompt = self.small_font.render("Restart?", True, TEXT_COLOR)
            self.screen.blit(prompt, (panel_x + 20, 395))
            self.restart_button_rect = self.draw_button(
                "Restart",
                panel_x + 20,
                425,
            )
        else:
            self.restart_button_rect = None

    def draw_next_piece(self, piece, start_x, start_y):
        for row_index, row in enumerate(piece.shape):
            for col_index, cell in enumerate(row):
                if cell:
                    x = start_x + col_index * CELL_SIZE
                    y = start_y + row_index * CELL_SIZE
                    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, piece.color, rect.inflate(-2, -2))

    def draw_button(self, label, x, y):
        text_surface = self.small_font.render(label, True, TEXT_COLOR)
        text_rect = text_surface.get_rect()
        padding_x, padding_y = self.restart_button_padding
        button_rect = pygame.Rect(
            x,
            y,
            text_rect.width + padding_x * 2,
            text_rect.height + padding_y * 2,
        )
        pygame.draw.rect(self.screen, (60, 60, 70), button_rect, border_radius=4)
        pygame.draw.rect(self.screen, (90, 90, 110), button_rect, 2, border_radius=4)
        text_pos = (
            x + padding_x,
            y + padding_y,
        )
        self.screen.blit(text_surface, text_pos)
        return button_rect


class InputHandler:
    def __init__(self):
        self.key_delay = 0
        self.key_repeat_ms = 80

    def handle_key_repeat(self, pressed, game, now):
        if now < self.key_delay:
            return
        moved = False
        if pressed[pygame.K_LEFT]:
            moved = self.try_move(game, -1, 0)
        if pressed[pygame.K_RIGHT]:
            moved = self.try_move(game, 1, 0) or moved
        if pressed[pygame.K_DOWN]:
            moved = self.try_move(game, 0, 1) or moved
        if moved:
            self.key_delay = now + self.key_repeat_ms

    def try_move(self, game, dx, dy):
        if game.valid_position(game.current_piece, offset_x=dx, offset_y=dy):
            game.current_piece.x += dx
            game.current_piece.y += dy
            return True
        if dy == 1:
            game.lock_piece(game.current_piece)
            return True
        return False


class TetrisGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tetris")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 32, bold=True)
        self.small_font = pygame.font.SysFont("arial", 20)
        self.game = Tetris()
        self.renderer = Renderer(self.screen, self.font, self.small_font)
        self.input_handler = InputHandler()
        self.drop_interval_ms = DROP_INTERVAL_MS
        self.next_speedup_ms = SPEEDUP_INTERVAL_MS
        pygame.time.set_timer(DROP_EVENT, self.drop_interval_ms)

    def reset(self):
        self.game = Tetris()
        self.drop_interval_ms = DROP_INTERVAL_MS
        self.next_speedup_ms = SPEEDUP_INTERVAL_MS
        pygame.time.set_timer(DROP_EVENT, self.drop_interval_ms)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == DROP_EVENT and not self.game.game_over:
                    if not self.game.valid_position(self.game.current_piece, offset_y=1):
                        self.game.lock_piece(self.game.current_piece)
                    else:
                        self.game.current_piece.y += 1
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and not self.game.game_over:
                        rotated = self.game.rotate(self.game.current_piece)
                        if self.game.valid_position(rotated):
                            self.game.current_piece = rotated
                    elif event.key == pygame.K_SPACE and not self.game.game_over:
                        self.game.hard_drop()
                    elif event.key == pygame.K_r and self.game.game_over:
                        self.reset()
                elif event.type == pygame.MOUSEBUTTONDOWN and self.game.game_over:
                    if event.button == 1 and self.renderer.restart_button_rect:
                        if self.renderer.restart_button_rect.collidepoint(event.pos):
                            self.reset()

            if not self.game.game_over:
                if now >= self.next_speedup_ms:
                    self.drop_interval_ms = max(
                        MIN_DROP_INTERVAL_MS,
                        int(self.drop_interval_ms * SPEEDUP_FACTOR),
                    )
                    pygame.time.set_timer(DROP_EVENT, self.drop_interval_ms)
                    self.next_speedup_ms += SPEEDUP_INTERVAL_MS
                pressed = pygame.key.get_pressed()
                self.input_handler.handle_key_repeat(pressed, self.game, now)

            self.screen.fill(BG_COLOR)
            self.renderer.draw_grid(self.game.grid)
            if not self.game.game_over:
                self.renderer.draw_piece(self.game.current_piece)
            self.renderer.draw_panel(self.game)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    TetrisGame().run()
