from __future__ import annotations
import json
from pathlib import Path
import xml.etree.ElementTree as ET
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
            m=self.meta(target,name)
            if target=='Text' and m['data_format']=='svg':
                self.images[key]=self._text_image(m)
            else:self.images[key]=pygame.image.load(ROOT/m['path']).convert_alpha()
        return self.images[key]
    def _text_image(self,m):
        """Rasterize Scratch text costumes without relying on SDL's SVG text support."""
        root=ET.parse(ROOT/m['path']).getroot()
        lines=[''.join(node.itertext()) for node in root.iter() if node.tag.endswith('tspan')]
        if not lines:
            lines=[''.join(node.itertext()) for node in root.iter() if node.tag.endswith('text')]
        width=max(1,round(float(root.attrib['width'])));height=max(1,round(float(root.attrib['height'])))
        surface=pygame.Surface((width,height),pygame.SRCALPHA)
        font_size=max(12,min(20,height//max(1,len(lines))))
        font=pygame.font.SysFont('serif',font_size)
        rendered=[font.render(line,True,(244,244,228)) for line in lines]
        total=sum(line.get_height() for line in rendered)
        y=max(0,(height-total)//2)
        for line in rendered:
            surface.blit(line,((width-line.get_width())//2,y));y+=line.get_height()
        return surface.convert_alpha()
    def text_surface(self,text,font_size=16,color=(255,255,255)):
        """Render UI copy with the same serif raster text used by intro cards."""
        font=pygame.font.SysFont('serif',font_size)
        return font.render(text,True,color).convert_alpha()
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
