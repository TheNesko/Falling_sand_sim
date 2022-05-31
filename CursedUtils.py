import pygame
from pygame.locals import *

MOUSE_LEFT = "m_l"
MOUSE_RIGHT = "m_r"

events = []

def update():
    UI.is_over_ui = False
    for object in UI.Objects:
        object.Update()
    events.clear()

def draw(screen):
    for object in UI.Objects:
        object.Draw(screen)

class UI():
    Objects = []

    is_over_ui = False

    def __init__(self) -> None:
        UI.Objects.append(self)

    def Draw(Screen) -> None:
        for Object in UI.Objects:
            Object.Draw(Screen)

    def Update() -> None:
        UI.is_over_ui = False

        for Object in UI.Objects:
            Object.Update()

class Button(UI):
    def __init__(self,position,size,color=(255,255,255),text="",text_color=(255,255,255),font_size=20,font="didot.ttc",border=1,visible=True) -> None:
        super().__init__()
        self.rect = pygame.Rect(position[0],position[1],size[0],size[1])
        self.text = text
        self.text_color = text_color
        self.color = color
        self.font = font
        self.border = border
        self.border_rect = (self.rect.x-self.border,self.rect.y-self.border,self.rect.w+border*2,self.rect.h+self.border*2)
        self.visible = visible
        self.font1 = pygame.font.SysFont( self.font, font_size)
        self.is_pressed = False
    
    def Draw(self,Screen) -> None:
        if self.visible:
            pygame.draw.rect(Screen,self.color,self.rect)
            if self.border > 0:
                pygame.draw.rect(Screen,(0,0,0),self.border_rect,self.border)
            self.img = self.font1.render(self.text, True, self.text_color)
            img_rect = self.img.get_rect(center=self.rect.center)
            Screen.blit(self.img,img_rect)

    def Update(self) -> None:
        self.is_pressed = False
        if self.visible:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos[0],mouse_pos[1]):
                UI.is_over_ui = True
                if MOUSE_LEFT in events:
                    self.is_pressed = True

class Popup(UI):
    def __init__(self) -> None:
        super().__init__()