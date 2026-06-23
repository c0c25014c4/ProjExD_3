import os
import sys
import pygame as pg

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    font_lst = [f for f in pg.font.get_fonts() if f != ""]
    print(font_lst)

    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
        
        txt = font.render("こんにちは世界", True, (255, 255, 255))
        screen.fill((0, 0, 0))
        screen.blit(txt, [300, 200])
        pg.display.update()
        clock.tick(10)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()