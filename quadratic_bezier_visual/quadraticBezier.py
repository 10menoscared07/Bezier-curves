import pygame, time, math, sys
import copy
from enum import Enum

import pygame.draw_py
pygame.init()

def clamp(val, mini, maxi):
    if val >= maxi:
        return maxi
    if val <= mini:
        return mini
    return val


vec2 = pygame.math.Vector2

class BasicWindow:
    def __init__(self, res=vec2(1280, 720), title="Quadratic beazier curve ;)"):
        self.resolution = res
        self.title = title

        self.window = pygame.Window(self.title, self.resolution)

    def get_window(self):
        return self.window.get_surface()

    def fill(self, color):
        self.get_window().fill(color)

    def update(self):
        self.window.flip()

class Variable:
    def __init__(self, value=None):
        self._currentValue = value
        self._prevValue = value
        self._changes = 0

    def getVal(self):
        return self._currentValue

    def setVal(self, value):
        del self._prevValue
        self._prevValue = copy.copy(self._currentValue)
        self._currentValue = value
        self._changes += 1
        
    def getPrev(self):
        return self._prevValue

    def getChanges(self):
        return self._changes

    val = property(getVal, setVal)
    prev = property(getPrev, None)
    changes = property(getChanges, None)

class ButtonStyle:
    def __init__(self):
        self.text = {"size":50,
                    "font":"font.ttf",
                    "fg":(200,200,200),
                    "bg":None,
                    "antialias":True,
                    "wraplength":700}

        self.button = {"padx":15,
                       "pady":15,
                       "bg":(10,10,10),
                       'outline':(200,20,100),
                       'outline-thick':1}
        self.hoverInAnim = {"color":(200,200,200),
                        "thickness":5,
                        "over":False,
                        "ongoing":False,
                        'startPos':None,
                        'endPos':None}


        self.hover = {"fg":(250,250,250),
                    "size":52,
                    'padx':1,
                    'pady':2,
                    "font":"font.ttf",
                    'bg':(30,30,30)}

        self.clickAnim = {'bg':(30,30,30), 'ongoing':False}
        self.clickTime = 0.1
        self.hoverTime  = 0.2

class Interpolate:
    @staticmethod
    def lerp(final, initial, time, duration):
        return initial + (final-initial)*clamp(time/duration, 0, 1)
    
    @staticmethod
    def lerpNorm(final, initial, time):
        return initial + (final-initial)*clamp(time, 0, 1)

    @staticmethod
    def easeInOutNorm(final, initial, time):
        # Ease-in-out function
        if time < 0.5:
            # Ease-in phase
            value = initial + (final - initial) * (2 * time * time)
        else:
            # Ease-out phase
            value = initial + (final - initial) * (1 - pow(-2 * time + 2, 2) / 2)
        
        return value

class LabelStyle:
    def __init__(self):
        self.text = {"font":"font.ttf",
                    "fg":(200,200,200),
                    "bg":None,
                    "size":18,
                    "antialias":True,
                    "wraplength":600}
        
class Label:
    def __init__(self, mgr, pos, text, style:LabelStyle):
        self.pos = pos
        self.mgr = mgr

        self.mgr.labels.append(self)
        
        self.text = {"text":text, 
                    "size":style.text['size'],
                    "font":style.text['font'],
                    "fg":style.text['fg'],
                    "bg":style.text['bg'],
                    "antialias":style.text['antialias'],
                    "wraplength":style.text['wraplength'],}

        self.font = pygame.font.Font(self.text['font'], self.text['size'])

        self.altered = True

    def change(self, prop, val):
        try:
            self.text[prop] = val
            self.altered = True
        except:
            print("Unknown property or invalid value")

    def manageSurfaces(self):
        if self.altered:
            self.altered = False

            self.textImage = self.font.render(self.text['text'], self.text['antialias'], self.text['fg'], self.text['bg'], self.text['wraplength'])
            self.textRect = self.textImage.get_rect(center=self.pos)

    def update(self, dt):
        self.manageSurfaces()

    def draw(self, window):
        window.blit(self.textImage, self.textRect)


class Button:
    class State(Enum):
        DEFAULT = 1
        HOVERED = 2
        LEFTCLICKED = 3
        RIGHTCLICKED = 4
        DISABLED = -1


    def __init__(self,mgr, pos, text, function, style:ButtonStyle):
        self.pos = pos ### center aligned
        self.mgr = mgr

        self.mgr.buttons.append(self)
        self.function = function
        self.style = style

        self.text = {"text":text, 
                    "size":self.style.text['size'],
                    "font":self.style.text['font'],
                    "fg":self.style.text['fg'],
                    "bg":self.style.text['bg'],
                    "antialias":self.style.text['antialias'],
                    "wraplength":self.style.text['wraplength'],}
        
        self.button = {"padx":self.style.button['padx'],
                       "pady":self.style.button['pady'],
                       "bg":self.style.button['bg'],
                       'outline':self.style.button['outline'],
                       'outline-thick':self.style.button['outline-thick'],}

        self.font = pygame.font.Font(self.text['font'], self.text['size'])



        self.state = Button.State.DEFAULT

        ### making animation for hover
        self.hoverInTimer = Timer(self.style.hoverTime)
        self.hoverInAnim = {"color":self.style.hoverInAnim['color'],
                        "thickness":self.style.hoverInAnim['thickness'],
                        "over":self.style.hoverInAnim['over'],
                        "ongoing":self.style.hoverInAnim['ongoing'],
                        'startPos':self.style.hoverInAnim['startPos'],
                        'endPos':self.style.hoverInAnim['endPos'],}


        self.hover = {"fg":self.style.hover['fg'],
                    "size":self.style.hover['size'],
                    'padx':self.style.hover['padx'],
                    'pady':self.style.hover['pady'],
                    "font":self.style.hover['font'],
                    'bg':self.style.hover['bg'],}

        self.clickAnim = {'bg':self.style.clickAnim['bg'],
                          'ongoing':False}
        self.clickTimer = Timer(self.style.clickTime)

        self.hoverFont = pygame.font.Font(self.hover['font'], self.hover['size'])

        self.altered = True


    def manageSurfaces(self):

        if self.altered:
            if self.state == Button.State.HOVERED:
                self.textImage = self.hoverFont.render(self.text['text'], self.text['antialias'], self.hover['fg'], None, self.text['wraplength'])
                self.textRect = self.textImage.get_rect(center=self.pos)

                    
                self.buttonRect = self.textRect.copy()
                self.buttonRect.width += 2*self.button['padx'] + 2*self.hover['padx']
                self.buttonRect.height += 2*self.button['pady'] + 2*self.hover['pady']
                self.buttonRect.center = self.textRect.center
            else:

                self.textImage = self.font.render(self.text['text'], self.text['antialias'], self.text['fg'], self.text['bg'], self.text['wraplength'])
                self.textRect = self.textImage.get_rect(center=self.pos)
                    
                self.buttonRect = self.textRect.copy()
                self.buttonRect.width += 2*self.button['padx']
                self.buttonRect.height += 2*self.button['pady']
                self.buttonRect.center = self.textRect.center

            self.altered = False


    def eventUpdate(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.state == Button.State.HOVERED:
                    self.state = Button.State.LEFTCLICKED
                    
                    self.function()
                    self.clickAnim['ongoing'] = True
                    
                    

    def update(self, dt):
        self.manageSurfaces()
        mousePos = pygame.mouse.get_pos()

        if self.buttonRect.collidepoint(*mousePos):
            self.state = Button.State.HOVERED
            if not self.hoverInAnim['ongoing']:
                self.hoverInAnim['ongoing'] = True
                self.hoverInAnim['over'] = False
                self.altered = True
        else:
            self.state = Button.State.DEFAULT

            if self.hoverInAnim['ongoing']:
                self.hoverInAnim['ongoing'] = False
                self.hoverInAnim['over'] = True
                self.hoverInAnim['endPos'] = None
                self.hoverInAnim['startPos'] = None
                self.hoverInTimer.reset()
                self.altered = True


        if self.hoverInAnim['ongoing']:
            self.hoverInTimer.update(dt)

            self.hoverInAnim['startPos'] = vec2(0,0)
            self.hoverInAnim['startPos'].x = self.buttonRect.midbottom[0] + Interpolate.easeInOutNorm(self.buttonRect.width//2, 0, self.hoverInTimer.getNormalized())
            self.hoverInAnim['startPos'].y  = self.buttonRect.midbottom[1]

            self.hoverInAnim['endPos'] = vec2(0,0)
            self.hoverInAnim['endPos'].x = self.buttonRect.midbottom[0] - Interpolate.easeInOutNorm(self.buttonRect.width//2, 0, self.hoverInTimer.getNormalized())
            self.hoverInAnim['endPos'].y  = self.buttonRect.midbottom[1]

            if self.hoverInTimer.isFinished():
                self.hoverInAnim['over'] = True


        if self.clickAnim['ongoing']:
            self.clickTimer.update(dt)
            if self.clickTimer.isFinished():
                self.clickAnim['ongoing'] = False
                self.clickTimer.reset()


    def draw(self, window):
        if self.state == Button.State.HOVERED or self.state == Button.State.LEFTCLICKED:

            if self.clickAnim['ongoing']:
                pygame.draw.rect(window, self.clickAnim['bg'], self.buttonRect, )
            else:
                pygame.draw.rect(window, self.button['bg'], self.buttonRect, )

            # pygame.draw.rect(window, self.button['outline'], self.buttonRect, width=self.button['outline-thick'])
            window.blit(self.textImage, self.textRect)

        else:
            pygame.draw.rect(window, self.button['bg'], self.buttonRect)
            window.blit(self.textImage, self.textRect)

        

        if self.hoverInAnim['ongoing']:
            pygame.draw.line(window, self.hoverInAnim['color'],self.hoverInAnim['startPos'], self.hoverInAnim['endPos'], self.hoverInAnim['thickness'])

class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.timer = 0
        self.finsied = False
    
    def update(self, deltaTime):
        self.timer += deltaTime
        if self.timer >= self.duration:
            self.finsied = True

    def getPercent(self):
        return clamp(self.timer/self.duration, 0, 1)*100

    def getNormalized(self):
        return clamp(self.timer/self.duration, 0, 1)

    def isFinished(self):
        return self.finsied
    
    def end(self):
        self.timer = 0
        self.finsied = True

    def reset(self):
        self.timer = 0
        self.finsied = False


class UIManager:
    def __init__(self):
        self.buttons = []
        self.labels = []

    def update(self, dt):
        for btn in self.buttons:
            btn.update(dt)

        for lbl in self.labels:
            lbl.update(dt)

    def draw(self, window):
        for btn in self.buttons:
            btn.draw(window)

        for lbl in self.labels:
            lbl.draw(window)

    def eventUpdate(self, event):
        for btn in self.buttons:
            btn.eventUpdate(event)


window = BasicWindow()

def lerp(v1, v2, t):
    return v1 + (v2-v1)*t

def hsl_to_rgb(h, s, l):
    """
    Convert HSL to RGB.

    Parameters:
        h (float): Hue (0-360 degrees)
        s (float): Saturation (0-1)
        l (float): Lightness (0-1)

    Returns:
        tuple: (R, G, B) values in the range 0-255
    """
    def hue_to_rgb(p, q, t):
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1/6:
            return p + (q - p) * 6 * t
        if t < 1/2:
            return q
        if t < 2/3:
            return p + (q - p) * (2/3 - t) * 6
        return p

    if s == 0:
        # Achromatic (gray)
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h / 360 + 1/3)
        g = hue_to_rgb(p, q, h / 360)
        b = hue_to_rgb(p, q, h / 360 - 1/3)

    # Convert to 0-255 range
    r = int(round(r * 255))
    g = int(round(g * 255))
    b = int(round(b * 255))

    return r, g, b

class Dot:
    def __init__(self, pos):
        self.pos =pos

        self.baseRadius = 8
        self.bufferRadius = 4
        self.radius = 8
        self.thickness = 2
        self.color = (200,200,200)
        self.hoverFill = [50]*3
        self.hoverOutline = [240]*3

        self.isHovered = False
        self.beingDragged = False


    def draw(self, window):
        if not self.isHovered:
            pygame.draw.circle(window, self.color, self.pos, self.radius, self.thickness)
        elif self.isHovered:
            pygame.draw.circle(window, self.hoverFill, self.pos, self.radius)
            pygame.draw.circle(window, self.hoverOutline, self.pos, self.radius, self.thickness)

    def isColliding(self, pos):
        if (self.pos-pos).length() <= self.radius:
            return True
        return False

    def update(self, dt):
        self.mousePos = vec2(*pygame.mouse.get_pos())

        if self.isColliding(self.mousePos):
            self.isHovered = True
        else:
            self.isHovered = False

        if self.beingDragged:
            self.pos = self.mousePos - self.offset
            self.isHovered = True


        if self.isHovered:
            self.radius = self.baseRadius + self.bufferRadius
        else:
            self.radius = self.baseRadius

        if pygame.mouse.get_pressed()[0] and self.isHovered:
            if not self.beingDragged:
                self.offset = self.mousePos - self.pos

            self.beingDragged = True
        else:
            self.beingDragged = False



    def drawUpdate(self, window, dt):
        self.update(dt)
        self.draw(window)


samples = 10
p1 = Dot(vec2(200,300))
p2 = Dot(vec2(600, 650))
p3 = Dot(vec2(1000, 150))

GRAY = (80, 80, 80)

viewStrings = True

def main(window, dt):

    p12 = Variable(p1.pos)
    p23 = Variable(p2.pos)
    p = Variable(p1.pos)

    for i in range(samples+1):
        t = i/samples

        p12.setVal(lerp(p1.pos, p2.pos, t))
        p23.setVal(lerp(p2.pos, p3.pos, t))



        if viewStrings:
            hue = t*360
            color = hsl_to_rgb(hue, 1, 0.5)
        
            pygame.draw.line(window, color, p12.getPrev(), p12.getVal(), 2)
            pygame.draw.line(window, color, p23.getPrev(), p23.getVal(), 2)
            pygame.draw.line(window, color, p12.getPrev(), p23.getVal(), 2)

        p.setVal(lerp(p12.getVal(), p23.getVal(), t))


        pygame.draw.line(window, (255,255,255), p.getPrev(), p.getVal(), 5)

    p1.drawUpdate(window, dt)
    p2.drawUpdate(window, dt)
    p3.drawUpdate(window, dt)
        
def click():
    global viewStrings
    viewStrings = not viewStrings

dt = 1/60
clock = pygame.time.Clock()



ui = UIManager()
bs = ButtonStyle()
bs.text['size'] = 30
bs.hover['size'] = 32
btn1 = Button(ui, vec2(1170, 680), "String Art N/Y", click, bs)

ls = LabelStyle()
ls.text['size'] = 20
lbl1 = Label(ui, vec2(80, 680), "Timer per frame: ", ls)

while 1:
    clock.tick(100000)
    fps = clock.get_fps()
    if fps <= 0: fps = 60
    dt = 1/fps

    lbl1.change("text", f"Time: {dt*1000:.2f} ms")

    mousePos = vec2(*pygame.mouse.get_pos())
    # p2 = mousePos
    

    
    # print(f"Time per frame: {dt*1000:.2f} ms")
    window.fill((30,30,30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        ui.eventUpdate(event)
    
    main(window.get_window(), dt)

    ui.update(dt)
    ui.draw(window.get_window())

    window.update()

            