from __future__ import annotations
import json, math
from pathlib import Path
import pygame
from .assets import Assets, ROOT
from .config import WIDTH,HEIGHT,FPS,TITLE
from .player import Player

IDLE_SECONDS = 10
IDLE_WARNING_SECONDS = 5
ENDING_RESTART_SECONDS = 7

class Game:
    def __init__(self):
        pygame.mixer.pre_init(48000,-16,2,1024); pygame.init()
        self.window=pygame.display.set_mode((960,720),pygame.RESIZABLE); pygame.display.set_caption(TITLE)
        self.canvas=pygame.Surface((WIDTH,HEIGHT)); self.clock=pygame.time.Clock(); self.a=Assets(); self.p=Player(self.a)
        self.levels=json.loads((ROOT/'data/levels.json').read_text())['levels']; self.dialogues=json.loads((ROOT/'data/dialogue.json').read_text())['sequences']
        self.level=1; self.state='playing'; self.timer=0; self.title_time=0; self.angle=0; self.voice=pygame.mixer.Channel(2); self.fx=pygame.mixer.Channel(3)
        self.loaded_levels=set(); self.idle_elapsed=0.; self.idle_warning=None
        self.tutorial_pending=True; self.tutorial=False; self.tutorial_clicks=0; self.tutorial_hold=0.; self.tutorial_pointer_down=False
        self.load_level(1); self.play_music('Hungarian Dance No')
    def restart_game(self):
        """Return to a fresh boot state after inactivity or the ending."""
        self.loaded_levels.clear(); self.title_time=0; self.idle_elapsed=0.; self.idle_warning=None
        self.tutorial_pending=True; self.tutorial=False; self.tutorial_clicks=0; self.tutorial_hold=0.; self.tutorial_pointer_down=False
        self.ceo=self.angry=self.launch=False
        self.load_level(1); self.play_music('Hungarian Dance No')
    def play_music(self,name):
        try: pygame.mixer.music.load(ROOT/self.a.meta('Stage',name,'sound')['path']); pygame.mixer.music.set_volume(.2); pygame.mixer.music.play(-1)
        except pygame.error: pass
    def sound(self,target,name,channel=None):
        s=self.a.sound(target,name)
        if s: (channel or self.fx).play(s); return s.get_length()
        return 0
    def load_level(self,n):
        first_load=n not in self.loaded_levels; self.loaded_levels.add(n)
        self.level=n; self.d=self.levels[n-1]
        facing=90 if self.d['spawn']['facing']=='right' else -90; self.p.reset(self.d['spawn']['x'],self.d['spawn']['y'],facing)
        self.ground=self.a.stage_surface('Ground',self.d['ground']); self.solid=pygame.mask.from_surface(self.ground)
        self.spike_surf=self.a.stage_surface('spikes',self.d['spikes']); self.spikes=pygame.mask.from_surface(self.spike_surf)
        self.invis_surf=self.a.stage_surface('Invisible platforms',self.d['invisible']); self.invis=pygame.mask.from_surface(self.invis_surf)
        self.dis_surf=self.a.stage_surface('disappearing platforms',self.d['disappearing']); self.dis=pygame.mask.from_surface(self.dis_surf)
        self.key_active='key' in self.d; self.platforms=False; self.saw_time=0
        if n==14: self.state='finale'; self.final_actions=None; self.timer=1.5
        elif 'assistant' in self.d and first_load: self.begin_dialogue(self.d['assistant']['sequence'])
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
        if self.idle_warning is not None:
            self.idle_warning-=dt
            if self.idle_warning<=0:self.restart_game()
            return
        if self.tutorial and (self.tutorial_pointer_down or pygame.mouse.get_pressed()[0]):
            self.tutorial_hold+=dt
            if self.tutorial_hold>=2:self.hide_tutorial()
        elif self.tutorial:self.tutorial_hold=0.
        # Only active play can become idle: dialogue level intros and every
        # phase of the ending therefore never accumulate idle time.
        if self.state=='playing':
            self.idle_elapsed+=dt
            if self.idle_elapsed>=IDLE_SECONDS:
                self.idle_warning=IDLE_WARNING_SECONDS
                return
        else:self.idle_elapsed=0.
        if self.state=='playing':
            k=pygame.key.get_pressed();mouse=pygame.mouse.get_pressed()[0]; mx,my=pygame.mouse.get_pos(); ww,wh=self.window.get_size()
            stage=self.window_to_stage(mx,my); zone=self.click_zone(*stage) if mouse and stage else None
            left=k[pygame.K_LEFT] or k[pygame.K_a] or zone in ('move_left','jump_left');right=k[pygame.K_RIGHT] or k[pygame.K_d] or zone in ('move_right','jump_right');jump=k[pygame.K_UP] or k[pygame.K_w] or zone in ('jump_left','jump_up','jump_right')
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
                else:self.state='complete';self.timer=ENDING_RESTART_SECONDS
        elif self.state=='complete':
            self.timer-=dt
            if self.timer<=0:self.restart_game()
    def window_to_stage(self,x,y):
        ww,wh=self.window.get_size();scale=min(ww/WIDTH,wh/HEIGHT);w,h=WIDTH*scale,HEIGHT*scale
        ox,oy=(ww-w)/2,(wh-h)/2
        if not (ox<=x<ox+w and oy<=y<oy+h):return None
        return (x-ox)/scale,(y-oy)/scale
    @staticmethod
    def click_zone(x,y):
        if y<HEIGHT/2:
            return ('jump_left','jump_up','jump_right')[min(2,int(x/(WIDTH/3)))]
        return 'move_left' if x<WIDTH/2 else 'move_right'
    def hide_tutorial(self):
        self.tutorial=False;self.tutorial_hold=0.;self.tutorial_pointer_down=False
    def note_input(self,event):
        """Reset inactivity and handle warning/tutorial input state."""
        self.idle_elapsed=0.
        if event.type in (pygame.MOUSEBUTTONUP,pygame.FINGERUP):self.tutorial_pointer_down=False
        if self.idle_warning is not None:
            self.idle_warning=None
            return
        pointer_down=event.type in (pygame.MOUSEBUTTONDOWN,pygame.FINGERDOWN)
        if pointer_down:self.tutorial_pointer_down=True
        if self.tutorial:
            if pointer_down:
                self.tutorial_clicks+=1;self.tutorial_hold=0.
                if self.tutorial_clicks>=2:self.hide_tutorial()
            return
        if self.tutorial_pending:
            self.tutorial_pending=False;self.tutorial=True
            self.tutorial_clicks=1 if pointer_down else 0
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
        if self.tutorial_pending:self.render_touch_to_start()
        if self.tutorial:self.render_tutorial()
        if self.idle_warning is not None:self.render_idle_warning()
        self.title_time+=1/FPS
    def render_touch_to_start(self):
        """Draw a softly pulsing kiosk call-to-action until first input."""
        alpha=round(190+55*(.5+.5*math.sin(self.saw_time*2)))
        text=self.a.text_surface('Touch to Start',22)
        panel=pygame.Surface((text.get_width()+36,text.get_height()+18),pygame.SRCALPHA)
        pygame.draw.rect(panel,(0,0,0,round(alpha*.55)),panel.get_rect(),border_radius=10)
        text.set_alpha(alpha);panel.blit(text,(18,9))
        self.canvas.blit(panel,panel.get_rect(center=(WIDTH//2,HEIGHT-38)))
    def render_tutorial(self):
        regions=[(pygame.Rect(0,0,160,180),(220,60,60),'Jump Left'),(pygame.Rect(160,0,160,180),(60,150,220),'Jump Up'),(pygame.Rect(320,0,160,180),(170,70,210),'Jump Right'),(pygame.Rect(0,180,240,180),(230,150,40),'Move Left'),(pygame.Rect(240,180,240,180),(50,180,100),'Move Right')]
        shade=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        for rect,color,label in regions:
            pygame.draw.rect(shade,(*color,105),rect);pygame.draw.rect(shade,(*color,230),rect,2)
            text=self.a.text_surface(label,16);shade.blit(text,text.get_rect(center=rect.center))
        self.canvas.blit(shade,(0,0))
    def render_idle_warning(self):
        veil=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA);veil.fill((0,0,0,175));self.canvas.blit(veil,(0,0))
        box=pygame.Rect(65,105,350,150);pygame.draw.rect(self.canvas,(28,31,42),box,border_radius=8);pygame.draw.rect(self.canvas,(235,235,240),box,2,border_radius=8)
        seconds=max(1,math.ceil(self.idle_warning))
        lines=('Game paused due to inactivity',f'Touch the screen within {seconds} seconds', 'or the game will restart')
        for i,line in enumerate(lines):
            text=self.a.text_surface(line,20 if i==1 else 16);self.canvas.blit(text,text.get_rect(center=(240,145+i*38)))
    def present(self):
        ww,wh=self.window.get_size();scale=min(ww/WIDTH,wh/HEIGHT);w,h=round(WIDTH*scale),round(HEIGHT*scale);frame=pygame.transform.scale(self.canvas,(w,h));self.window.fill((0,0,0));self.window.blit(frame,((ww-w)//2,(wh-h)//2));pygame.display.flip()
    def run(self):
        acc=0.;running=True
        while running:
            dt=min(.1,self.clock.tick(FPS)/1000);acc+=dt
            for e in pygame.event.get():
                if e.type in (pygame.KEYDOWN,pygame.KEYUP,pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP,pygame.MOUSEMOTION,pygame.FINGERDOWN,pygame.FINGERUP,pygame.FINGERMOTION,pygame.JOYBUTTONDOWN,pygame.JOYBUTTONUP,pygame.JOYAXISMOTION,pygame.JOYHATMOTION):self.note_input(e)
                if e.type==pygame.QUIT or e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:running=False
                elif e.type==pygame.KEYDOWN and e.key==pygame.K_F11:pygame.display.toggle_fullscreen()
                if e.type==pygame.KEYDOWN and e.key in (pygame.K_r,pygame.K_RETURN) and self.state=='complete':self.restart_game()
            while acc>=1/30:self.update(1/30);acc-=1/30
            self.render();self.present()
        pygame.quit()

def main(): Game().run()
