from __future__ import annotations
import json
from pathlib import Path
import pygame

ROOT = Path(__file__).resolve().parents[1]

class Assets:
    def __init__(self):
        manifest=json.loads((ROOT/'data/asset_manifest.json').read_text())['assets']
        self.items={(x['target'],x['kind'],x['name']):x for x in manifest}
        self.images={}; self.sounds={}
    def meta(self,target,name,kind='costume'): return self.items[(target,kind,name)]
    def image(self,target,name):
        key=(target,name)
        if key not in self.images:
            m=self.meta(target,name); self.images[key]=pygame.image.load(ROOT/m['path']).convert_alpha()
        return self.images[key]
    def sound(self,target,name):
        key=(target,name)
        if key not in self.sounds:
            try: self.sounds[key]=pygame.mixer.Sound(ROOT/self.meta(target,name,'sound')['path'])
            except pygame.error: self.sounds[key]=None
        return self.sounds[key]
    def draw(self,dst,target,name,x,y,size=100,direction=90,alpha=255,brightness=0):
        m=self.meta(target,name); img=self.image(target,name)
        scale=size/100/m.get('bitmap_resolution',1)
        nw=max(1,round(img.get_width()*scale)); nh=max(1,round(img.get_height()*scale))
        img=pygame.transform.scale(img,(nw,nh))
        if direction < 0: img=pygame.transform.flip(img,True,False)
        if alpha != 255: img=img.copy(); img.set_alpha(alpha)
        if brightness:
            img=img.copy(); img.fill((brightness,brightness,brightness,0),special_flags=pygame.BLEND_RGBA_ADD)
        left=round(240+x-m['rotation_center_x']*scale); top=round(180-y-m['rotation_center_y']*scale)
        dst.blit(img,(left,top)); return img, pygame.Rect(left,top,nw,nh)
    def stage_surface(self,target,name,size=350,alpha=255):
        s=pygame.Surface((480,360),pygame.SRCALPHA); self.draw(s,target,name,0,0,size,alpha=alpha); return s
