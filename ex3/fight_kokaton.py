import math  # 追加：ビームの回転計算用
import os
import pygame as pg
import random
import sys
import time


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5  # 爆弾の数
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy
        self.dire = (+5, 0)  

    def change_img(self, num: int, screen: pg.Surface):
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
            self.dire = tuple(sum_mv)  
            
        screen.blit(self.img, self.rct)


class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird: "Bird"):
        self.vx, self.vy = bird.dire
        theta = math.atan2(-self.vy, self.vx)  
        angle = math.degrees(theta)  
        img_orig = pg.image.load("fig/beam.png")
        self.img = pg.transform.rotozoom(img_orig, angle, 1.0)
        
        self.rct = self.img.get_rect()
        self.rct.centerx = bird.rct.centerx + (bird.rct.width * self.vx / 5)
        self.rct.centery = bird.rct.centery + (bird.rct.height * self.vy / 5)

    def update(self, screen: pg.Surface):
        if check_bound(self.rct) == (True, True):
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct)    


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Score:
    """
    打ち落とした爆弾の数を表示するスコアに関するクラス
    """
    def __init__(self):
        self.fonto = pg.font.Font(None, 50) 
        self.color = (0, 0, 255)  
        self.score = 0
        self.img = self.fonto.render(f"SCORE: {self.score}", 0, self.color)
        self.rct = self.img.get_rect()
        self.rct.center = (100, HEIGHT - 50)  

    def update(self, screen: pg.Surface):
        self.img = self.fonto.render(f"SCORE: {self.score}", 0, self.color)
        screen.blit(self.img, self.rct)


class Explosion:
    """
    爆弾が爆発したときのエフェクトに関するクラス
    """
    def __init__(self, bomb: "Bomb"):
        img_orig = pg.image.load("fig/explosion.gif")
        img_flip = pg.transform.flip(img_orig, True, True)  
        self.imgs = [img_orig, img_flip]
        self.rct = img_orig.get_rect()
        self.rct.center = bomb.rct.center
        self.life = 40  

    def update(self, screen: pg.Surface):
        self.life -= 1
        if self.life > 0:
            img_idx = (self.life // 10) % 2
            screen.blit(self.imgs[img_idx], self.rct)


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    score = Score()  
    beams = []  
    explosions = []  

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.append(Beam(bird))            
        
        screen.blit(bg_img, [0, 0])
        
        # 復活部分：爆弾とこうかとんが衝突した時の処理
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                bird.change_img(8, screen) # 泣いてる画像
                
                # 練習4の「Game Over」文字表示をここに復活！
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH // 2 - 150, HEIGHT // 2])
                
                pg.display.update()
                time.sleep(1)
                return
        
        for j, beam in enumerate(beams):
            if beam is not None:
                for i, bomb in enumerate(bombs):
                    if bomb is not None:
                        if beam.rct.colliderect(bomb.rct):  
                            bird.change_img(6, screen)
                            explosions.append(Explosion(bomb))
                            beams[j] = None  
                            bombs[i] = None  
                            score.score += 1  
        
        bombs = [bomb for bomb in bombs if bomb is not None]
        beams = [beam for beam in beams if beam is not None and check_bound(beam.rct) == (True, True)]
        explosions = [exp for exp in explosions if exp.life > 0]

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        
        for beam in beams:
            beam.update(screen)   
            
        for bomb in bombs:
            bomb.update(screen)
            
        for exp in explosions:
            exp.update(screen)
            
        score.update(screen)
        
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()