import pygame
from .config import wrap_coordinate

class Player:
    def __init__(self, assets): self.a=assets; self.facing=90; self.reset(0,0,90)
    def reset(self,x,y,facing):
        self.x,self.y=float(x),float(y); self.sx=self.sy=0.; self.facing=facing; self.grounded=False; self.frame=0; self.costume='idle 1'
    def mask_at(self,x=None,y=None,costume='Hitbox'):
        m=self.a.meta('Player',costume); im=self.a.image('Player',costume); scale=3/m['bitmap_resolution']; im=pygame.transform.scale(im,(max(1,round(im.get_width()*scale)),max(1,round(im.get_height()*scale))))
        px=round(240+(self.x if x is None else x)-m['rotation_center_x']*scale); py=round(180-(self.y if y is None else y)-m['rotation_center_y']*scale)
        return pygame.mask.from_surface(im), (px,py)
    def overlaps(self, terrain, x=None,y=None):
        mask,pos=self.mask_at(x,y); return terrain.overlap(mask,pos) is not None
    def update(self,solid,left,right,jump):
        self.sy=max(-20,self.sy-1)
        if jump and self.grounded and self.sy>-2: self.sy=13; self.grounded=False; jumped=True
        else: jumped=False
        old=self.y; self.y+=self.sy
        if self.overlaps(solid):
            step=-1 if self.sy>0 else 1
            for _ in range(50):
                self.y+=step
                if not self.overlaps(solid): break
            self.grounded=self.sy<0; self.sy=0
        elif self.sy: self.grounded=False
        if self.y>182 or self.y<-182:
            self.y=wrap_coordinate(self.y,182);self.sy=0
        if right:self.sx+=1.2;self.facing=90
        if left:self.sx-=1.2;self.facing=-90
        self.sx*=.8; self.x+=self.sx
        if self.overlaps(solid):
            step=-1 if self.sx>0 else 1
            for _ in range(30):
                self.x+=step
                if not self.overlaps(solid): break
            self.sx=0
        if self.x>240 or self.x<-240:
            self.x=wrap_coordinate(self.x,240);self.sx=0
        if not self.grounded:self.costume='jump' if self.sy>0 else 'fall'
        elif abs(self.sx)>.2:self.costume=f"run {1+(self.frame//3)%8}"
        else:self.costume=f"idle {1+(self.frame//7)%4}"
        self.frame+=1
        return jumped
    def draw(self,s): return self.a.draw(s,'Player',self.costume,self.x,self.y,300,self.facing)
