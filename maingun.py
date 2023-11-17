import math
from random import choice
import pygame as pg


FPS = 30

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
GAME_COLORS = [BLUE, YELLOW, GREEN, MAGENTA, CYAN]

WIDTH = 800
HEIGHT = 600

K = 0.07 #coefficient of aerodynamic drag


class Ball:
    def __init__(self, screen: pg.Surface, x=30, y=500):
        """
        Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.mass = 5
        self.x = x
        self.y = y
        self.r = 10
        self.vx = 0
        self.vy = 0
        self.color = choice(GAME_COLORS)
        self.live = 30

    def move(self):
        """
        Перемещает снаряд при каждой прорисовке с учетом скоростей vx, vy , гравитации и сопротивления среды.
        """

        self.live -= 0.1 #уменьшает оставшееся время жизни снаряда

        self.x += self.vx
        self.y -= self.vy

        #гравитация:
        self.vy -= 0.2
        if self.y<=0 or self.y>=600:
            self.vy *= -1
        self.vy -= 0.2

        #сопротивление
        v = (self.vy ** 2 + self.vx ** 2) ** 0.5
        self.vy -= self.vy/v * K * v ** 2 / self.mass / FPS
        self.vx -= self.vx/v * K * v ** 2 / self.mass / FPS

    def draw(self):
        pg.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def hit(self, obj):
        """
        Проверяет, произошло ли столкновение снаряда с объектом, переданным в аргументах.
        """
        if (self.x - obj.x) ** 2 + (self.y - obj.y) ** 2 < (self.r + obj.r) ** 2:
            return True
        return False


class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.x = 30
        self.y = 500
        self.width = 30
        self.height =30
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = BLACK

    def fire_start(self, event):
        self.f2_on = 1

    def fire_end(self, event):
        """
        Выстрел снаряда.
        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls
        new_ball = Ball(self.screen)
        new_ball.r += 5
        self.an = math.atan2((event.pos[1] - new_ball.y), (event.pos[0] - new_ball.x))
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = - self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 10

    def draw(self):
        """
        Прорисовка пушки каждый кадр с учетом её наклона (определяемого положением мыши относительно снаряда an)
        и текущей длины (зависящей от накопленного заряда f.power).
         """

        cos = math.cos(self.an)
        sin = math.sin(self.an)
        d1 = [self.x - self.height / 2 * sin, self.y + self.height / 2 * cos]
        d4 = [self.x + self.height / 2 * sin, self.y - self.height / 2 * cos]
        d2 = [self.width * cos + d1[0], self.width * sin + d1[1]]
        d3 = [self.width * cos + d4[0], self.width * sin + d4[1]]
        pg.draw.polygon(self.screen, self.color, [d1, d2, d3, d4])

    def targetting(self, event):
        """Прицеливание по положению мыши."""

        if event:
            self.an = math.atan((event.pos[1]-450) / (event.pos[0]-20))
        if self.f2_on:
            self.color = RED
        else:
            self.color = BLACK


    def power_up(self):
        """
        Накопление заряда пушкой, пока нажата кнопка мыши.
        При этом пропорциональна увеличивается ее длина и изменяется цвет
        """

        if self.f2_on:
            self.width = 30 + self.f2_power
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = RED
        else:
            self.color = BLACK
            self.width = 30



class Target:
    def __init__(self, screen, live):
        self.screen = screen
        self.live = 1
        self.new_target()

    def new_target(self):
        """ Инициализация новой цели. """
        self.x = choice(range(600, 780))
        self.y = choice(range(200, 550))
        self.r = choice(range(4, 50))
        self.vx= choice(range(1,5))/4
        self.vy= choice(range(5,15))/5
        self.live = 1
        self.color = RED


    def move(self):
        """
        Передвигат мишени каждый кадр.
        Т.е. обновляет значения self.x и self.y
        с учетом скоростей self.vx и self.vy и возможных соударений с краями окна.
        """
        self.x += self.vx
        if self.y<=0 or self.y>=600:
            self.vy *= -1
        if self.x<=0 or self.x>=800:
            self.vx *= -1
        self.y -= self.vy

    def draw(self):
        pg.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )


pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
balls = []

clock = pg.time.Clock()
gun = Gun(screen)
target1 = Target(screen,0)
target2 = Target(screen,0)
finished = False

while not finished:
    screen.fill(WHITE)
    gun.draw()
    target1.draw()
    target2.draw()
    for b in balls:
        b.draw()
    pg.display.update()

    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            finished = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            gun.fire_start(event)
        elif event.type == pg.MOUSEBUTTONUP:
            gun.fire_end(event)
        elif event.type == pg.MOUSEMOTION:
            gun.targetting(event)

    for b in range(len(balls)):
        balls[b].move()
        dead_balls = []
        if balls[b].hit(target1) and target1.live:
            target1.live = 0
            target1.new_target()
        if balls[b].hit(target2) and target2.live:
            target2.live = 0
            target2.new_target()
        if balls[b].live <=0:
            del balls[b]
            break

    target1.move()
    target2.move()
    gun.power_up()

pg.quit()