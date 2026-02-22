import pygame

WIDTH, HEIGHT = 900, 250

pygame.init()

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

start_button_xLeft = 50
start_button_xRight = 250
start_button_yBottom = 25
start_button_yTop = 200

exit_button_xLeft = 300
exit_button_xRight = 500
exit_button_yBottom = 25
exit_button_yTop = 200

exit_menu = 0

screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill(WHITE)

button_font = pygame.font.SysFont('Comic Sans MS', 30)
title_font= pygame.font.SysFont('Comic Sans MS', 30)
credits_font = pygame.font.SysFont('Comic Sans MS', 20)
intern = pygame.font.SysFont('Comic Sans MS', 10)

start_button = button_font.render('Start Game', True, BLACK)
exit_button = button_font.render('Exit', True, BLACK)

credits_line_title = title_font.render('SUPER DUCKY RUN', True, BLACK)
credits_line0 = credits_font.render('----CREDITS-----', True, BLACK)
credits_line1 = credits_font.render('Nicholas Horner', True, BLACK)
credits_line2 = credits_font.render('Zac Calvert', True, BLACK)
credits_line3 = credits_font.render('Sam Palatnikov', True, BLACK)
credits_line4 = credits_font.render('Kaitlyn Dunphy', True, BLACK)
credits_line5 = intern.render('+ Intern', True, BLACK)


screen.blit(credits_line_title, (550, 25))
screen.blit(credits_line0, (600, 100))
screen.blit(credits_line1, (600, 125))
screen.blit(credits_line2, (600, 150))
screen.blit(credits_line3, (600, 175))
screen.blit(credits_line4, (600, 200))
screen.blit(credits_line5, (600, 225))


while exit_menu == 0:
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    pygame.draw.rect(screen, RED, (exit_button_xLeft, exit_button_yBottom, exit_button_xRight - exit_button_xLeft, exit_button_yTop - exit_button_yBottom))
    pygame.draw.rect(screen, GREEN, (start_button_xLeft, start_button_yBottom, start_button_xRight - start_button_xLeft, start_button_yTop - start_button_yBottom))

    if (start_button_xLeft < mouse_x < start_button_xRight) and (start_button_yBottom < mouse_y < start_button_yTop):
        pygame.draw.rect(screen, (0, 150, 0), (start_button_xLeft, start_button_yBottom, start_button_xRight - start_button_xLeft, start_button_yTop - start_button_yBottom))
        if pygame.mouse.get_pressed(3)[0] == True:
            print("Start Game")
            exit_menu = 1

    if (exit_button_xLeft < mouse_x < exit_button_xRight) and (exit_button_yBottom < mouse_y < exit_button_yTop):
        pygame.draw.rect(screen, (150, 0, 0), (exit_button_xLeft, exit_button_yBottom, exit_button_xRight - exit_button_xLeft, exit_button_yTop - exit_button_yBottom))
        if pygame.mouse.get_pressed(3)[0] == True:
            print("Exit")
            exit()

    screen.blit(start_button, (start_button_xLeft + 20, start_button_yBottom + 65)) 
    screen.blit(exit_button, (exit_button_xLeft + 70, exit_button_yBottom + 65))

    pygame.display.update()
