from __future__ import annotations
import json, math
from pathlib import Path
import pygame
from .assets import Assets, ROOT
from .config import WIDTH,HEIGHT,FPS,TITLE
from .player import Player

class Game:
    def __init__(self):
        pygame.mixer.pre_init(48000,-16,2,1024); pygame.init()
        self.window=pygame.display.set_mode((960,720),pygame.RESIZABLE); pygame.display.set_caption(TITLE)
        self.canvas=pygame.Surface((WIDTH,HEIGHT)); self.clock=pygame.time.Clock(); self.a=Assets(); self.p=Player(self.a)
        self.levels=json.loads((ROOT/'data/levels.json').read_text())['levels']; self.dialogues=json.loads((ROOT/'data/dialogue.json').read_text())['sequences']
        self.level=1; self.state='playing'; self.timer=0; self.title_time=0; self.angle=0; self.voice=pygame.mixer.Channel(2); self.fx=pygame.mixer.Channel(3)
        self.load_level(1); self.play_music('Hungarian Dance No')
    def play_music(self,name):
        try: pygame.mixer.music.load(ROOT/self.a.meta('Stage',name,'sound')['path']); pygame.mixer.music.set_volume(.2); pygame.mixer.music.play(-1)
        except pygame.error: pass
    def sound(self,target,name,channel=None):
        s=self.a.sound(target,name)
        if s: (channel or self.fx).play(s); return s.get_length()
        return 0
    def load_level(self,n):
        self.level=n; self.d=self.levels[n-1]
        facing=90 if self.d['spawn']['facing']=='right' else -90; self.p.reset(self.d['spawn']['x'],self.d['spawn']['y'],facing)
        self.ground=self.a.stage_surface('Ground',self.d['ground']); self.solid=pygame.mask.from_surface(self.ground)
        self.spike_surf=self.a.stage_surface('spikes',self.d['spikes']); self.spikes=pygame.mask.from_surface(self.spike_surf)
        self.invis_surf=self.a.stage_surface('Invisible platforms',self.d['invisible']); self.invis=pygame.mask.from_surface(self.invis_surf)
        self.dis_surf=self.a.stage_surface('disappearing platforms',self.d['disappearing']); self.dis=pygame.mask.from_surface(self.dis_surf)
        self.key_active='key' in self.d; self.platforms=False; self.saw_time=0
        if n==14: self.state='finale'; self.final_actions=None; self.timer=1.5
        elif 'assistant' in self.d: self.begin_dialogue(self.d['assistant']['sequence'])
        else:self.state='playing'
    def begin_dialogue(self,seq): self.state='dialogue';self.lines=self.dialogues[str(seq)];self.line=-1;self.timer=.35;self.card=None
    def next_line(self):
        self.line+=1
        if self.line>=len(self.lines): self.state='playing';self.card=None;return
        x=self.lines[self.line];self.card=x['card'];self.timer=self.sound('Text',x['sound'],self.voice)+x['after']
    def player_overlap(self,mask):
        pm,pos=self.p.mask_at(costume=self.p.costume); return mask.overlap(pm,pos) is not None
    def die(self):
        if self.state!='playing':return
        self.state='dying';self.timer=2.1;self.sound('Player','hitHurt (2)')
    def start_finale(self):
        self.play_music('PSP Persona OST Mad Hospital 10 Disc 1')
        names=['Im going to help you out','decrepid building','i cannot suport this org','deep voice 1','our visitor is right here','deep voice 2','no I wont','Vine Boom Sound Effect (Longer Verison For Real)','deep voice 3','i cant I wont','deep voice 4','no please!','manual override','my thrusters are controlled','receiving far worse']
        targets=['Text']*7+['the CEO']+['Text']*7
        self.final_actions=list(zip(targets,names));self.final_i=0;self.ceo=False;self.angry=False;self.launch=False;self.play_final_action()
    def play_final_action(self):
        if self.final_i>=len(self.final_actions): self.state='cards';self.card_i=0;self.card_phase='in';self.timer=.75;return
        target,name=self.final_actions[self.final_i]
        if name=='deep voice 1':self.ceo=True
        if name=='Vine Boom Sound Effect (Longer Verison For Real)':self.angry=True
        if name=='my thrusters are controlled':self.launch=True
        self.timer=self.sound(target,name,self.voice)+(.5 if name!='no please!' else 1);self.final_i+=1
    def update(self,dt):
        self.angle=(self.angle+2)%360;self.saw_time+=dt
        if self.state=='playing':
            k=pygame.key.get_pressed();mouse=pygame.mouse.get_pressed()[0]; mx,my=pygame.mouse.get_pos(); ww,wh=self.window.get_size()
            left=k[pygame.K_LEFT] or k[pygame.K_a] or (mouse and mx<ww/2);right=k[pygame.K_RIGHT] or k[pygame.K_d] or (mouse and mx>ww/2);jump=k[pygame.K_UP] or k[pygame.K_w] or (mouse and my<wh/2)
            solid=self.solid.copy()
            if self.platforms:solid.draw(self.invis,(0,0))
            if self.level==13 and not self.platforms:solid.draw(self.dis,(0,0))
            if self.p.update(solid,left,right,jump):self.sound('Player','jump (1)')
            if self.player_overlap(self.spikes):self.die()
            if self.key_active:
                keyrect=pygame.Rect(*[v-12 for v in (240+self.d['key']['x'],180-self.d['key']['y'])],24,24)
                if keyrect.collidepoint(240+self.p.x,180-self.p.y):self.key_active=False;self.platforms=True;self.sound('Key','pickupCoin (1)')
            for saw,rect in self.saws():
                if rect.collidepoint(240+self.p.x,180-self.p.y):self.die()
            if self.d['goal']:
                g=self.d['goal'];
                if (self.p.x-g['x'])**2+(self.p.y-g['y'])**2<25**2:self.state='transition';self.timer=1.25
        elif self.state=='dialogue':
            self.timer-=dt
            if self.timer<=0:self.next_line()
        elif self.state=='dying':
            self.timer-=dt
            if self.timer<=0:self.load_level(self.level)
        elif self.state=='transition':
            self.timer-=dt
            if self.timer<=0:self.load_level(self.level+1)
        elif self.state=='finale':
            self.timer-=dt
            if self.timer<=0:
                if self.final_actions is None:self.start_finale()
                else:self.play_final_action()
        elif self.state=='cards':
            self.timer-=dt
            if self.timer<=0:
                holds=[1,1,4,4,2,3,3]
                if self.card_phase=='in':self.card_phase='hold';self.timer=holds[self.card_i]
                elif self.card_phase=='hold':self.card_phase='out';self.timer=.75
                elif self.card_i<6:self.card_i+=1;self.card_phase='in';self.timer=1.25
                else:self.state='complete'
    def saws(self):
        out=[]
        for d in self.d.get('saws',[]):
            cycle=self.saw_time%2.667
            if cycle<.333:t=cycle/.333
            elif cycle<1.333:t=1
            elif cycle<1.666:t=1-(cycle-1.333)/.333
            else:t=0
            x=d['x']-d['movement_x']*t;y=d['y']-d['movement_y']*t
            im=self.a.image('saws','costume2');scale=d['size']/200;im=pygame.transform.scale(im,(round(im.get_width()*scale),round(im.get_height()*scale)));im=pygame.transform.rotate(im,-self.angle*3.5)
            out.append((im,im.get_rect(center=(round(240+x),round(180-y)))))
        return out
    def render(self):
        self.canvas.fill((4,5,10)); self.canvas.blit(self.a.stage_surface('background',self.d['background'],alpha=178),(0,0));self.canvas.blit(self.ground,(0,0))
        if self.level==13 and not self.platforms:self.canvas.blit(self.dis_surf,(0,0))
        if self.platforms:self.canvas.blit(self.invis_surf,(0,0))
        self.canvas.blit(self.spike_surf,(0,0))
        if self.key_active:
            self.a.draw(self.canvas,'Key','costume1',self.d['key']['x'],self.d['key']['y'],200,direction=80+math.sin(self.saw_time)*10)
        if self.d['goal']:
            g=self.d['goal']; im=self.a.image('Goal','costume1');im=pygame.transform.scale(im,(round(im.get_width()*1.75),round(im.get_height()*1.75)));im=pygame.transform.rotate(im,-self.angle);im.set_alpha(230);self.canvas.blit(im,im.get_rect(center=(240+g['x'],180-g['y'])))
        for im,r in self.saws():self.canvas.blit(im,r)
        if self.state!='dying' or int(self.timer*10)%2:self.p.draw(self.canvas)
        if self.state=='dialogue' or self.state=='finale':
            ast=self.d.get('assistant',{'x':15,'y':-120}); ay=ast['y']+math.sin(self.saw_time*2)*3
            if not getattr(self,'launch',False):self.a.draw(self.canvas,'assistant','costume1' if int(self.saw_time/.7)%2==0 else 'costume2',ast['x'],ay,300,-90 if self.p.x<ast['x'] else 90)
            if self.card:self.a.draw(self.canvas,'Text',self.card,ast['x'],ay+30)
        if getattr(self,'ceo',False):self.a.draw(self.canvas,'the CEO','angy' if self.angry else 'calm',0,0 if self.angry else 50,525 if self.angry else 400)
        if self.state=='transition':
            overlay=self.a.stage_surface('transist','costume1');overlay.set_alpha(min(255,round((1.25-self.timer)*400)));self.canvas.blit(overlay,(0,0))
        if self.state in ('cards','complete'):
            self.canvas.fill((0,0,0));idx=self.card_i if self.state=='cards' else 6;alpha=255
            if self.state=='cards' and self.card_phase=='in':alpha=round(255*(1-self.timer/.75))
            if self.state=='cards' and self.card_phase=='out':alpha=round(255*self.timer/.75)
            self.a.draw(self.canvas,'Text',f'Final {idx+1}',0,50,125,alpha=max(0,min(255,alpha)))
        if self.title_time<5:
            alpha=255 if self.title_time<4 else round(255*(5-self.title_time));self.a.draw(self.canvas,'Title ','tilted',0,0,alpha=max(0,alpha))
        self.title_time+=1/FPS
    def present(self):
        ww,wh=self.window.get_size();scale=min(ww/WIDTH,wh/HEIGHT);w,h=round(WIDTH*scale),round(HEIGHT*scale);frame=pygame.transform.scale(self.canvas,(w,h));self.window.fill((0,0,0));self.window.blit(frame,((ww-w)//2,(wh-h)//2));pygame.display.flip()
    def run(self):
        acc=0.;running=True
        while running:
            dt=min(.1,self.clock.tick(FPS)/1000);acc+=dt
            for e in pygame.event.get():
                if e.type==pygame.QUIT or e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:running=False
                elif e.type==pygame.KEYDOWN and e.key==pygame.K_F11:pygame.display.toggle_fullscreen()
                elif e.type==pygame.KEYDOWN and e.key in (pygame.K_r,pygame.K_RETURN) and self.state=='complete':self.load_level(1);self.play_music('Hungarian Dance No')
            while acc>=1/30:self.update(1/30);acc-=1/30
            self.render();self.present()
        pygame.quit()

def main(): Game().run()
