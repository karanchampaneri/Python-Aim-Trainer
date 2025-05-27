import math
import random
import time
import pygame
pygame.init()


WIDTH, HEIGHT = 800, 600  # Screen dimensions

WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Aim Trainer")

TARGET_INCREMENT = 400 # Time in milliseconds to add a new target
TARGET_EVENT = pygame.USEREVENT  # Custom event for adding targets

TARGET_PADDING = 30 # Padding around the screen

BG_COLOR = (0, 25, 40)  # Background color (black)
LIVES = 3
HUD_HEIGHT = 50  # Height of the HUD


LABEL_FONT = pygame.font.SysFont("comicsans", 24)  # Font for the HUD labels


class Target:
    MAX_SIZE = 30
    GROWTH_RATE = 0.2 #pixels per target per frame
    COLOR = "red"
    SECOND_COLOR = "white"

    def __init__(self, x, y): #constructor
        self.x = x
        self.y = y
        self.size = 0 #radius of the target increase until it reaches MAX_SIZE
        self.grow = True #boolean to check if the target is growing


    def update(self):
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False

        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE
        
    
    def draw(self, win):
        #draw a circle target
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.4)

    def collide(self, x, y):
        #check if the mouse position is within the target radius
        #center coordinates of mouse vs target, so take the straight line distance between the two 
        # points and see if the distance is less than the radius of the target if true then the mouse is within the target
        # distance to point formula 

        distance = math.sqrt(((self.x - x) ** 2) + ((self.y - y) ** 2))
        return distance <= self.size  # Return True if the mouse is within the target radius, False otherwise


def draw_main(win, targets):
    #frame by frame rendering of the game

    win.fill(BG_COLOR)

    for target in targets:
        target.draw(win)
    
    


def format_time(secs):
    milli = math.floor((int(secs * 1000) % 1000) / 100)  # Get milliseconds
    secs = int(round(secs%60, 1))  # Get whole seconds
    mins = int(secs//60)  # Get whole minutes
    return f"{mins:02d}:{secs:02d}.{milli}"  # Format as MM:SS.milliseconds


def draw_hud(win, elapsed_time, target_pressed, misses):
    
    pygame.draw.rect(win, "grey", (0,0, WIDTH, HUD_HEIGHT))  # Draw a black rectangle for the HUD background

    #render instance of font
    time_label = LABEL_FONT.render(
        f"Time: {format_time(elapsed_time)}", 1, "black")
    
    speed = round(target_pressed / elapsed_time, 1)

    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "black")
    hits_label = LABEL_FONT.render(f"Hits: {target_pressed}", 1, "black")
    lives_label = LABEL_FONT.render(f"Lives: {LIVES - misses}", 1, "black")


    win.blit(time_label, (5, 5))  # Draw the time label on the HUD blit displays additianl content to the window
    win.blit(speed_label, (200, 5)) 
    win.blit(hits_label, (450, 5)) 
    win.blit(lives_label, (650, 5)) 


def end_screen(win, elapsed_time, target_pressed, clicks):
    win.fill(BG_COLOR)

    time_label = LABEL_FONT.render(
        f"Time: {format_time(elapsed_time)}", 1, "white")
    
    speed = round(target_pressed / elapsed_time, 1)

    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "white")

    hits_label = LABEL_FONT.render(f"Hits: {target_pressed}", 1, "white")

    accuracy = round((target_pressed / clicks) * 100, 1)
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}%", 1, "white")
    
    win.blit(time_label, (get_middle(time_label), 100))  # Draw the time label on the HUD blit displays additianl content to the window
    win.blit(speed_label, (get_middle(speed_label), 200)) 
    win.blit(hits_label, (get_middle(hits_label), 300)) 
    win.blit(accuracy_label, (get_middle(accuracy_label), 400)) 

    pygame.display.update()  # Update the display to show the end screen

    run = True
    while run:  # Keep the end screen displayed until the user closes the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                quit()



    #find middle of the screen, draw from x/2 - width/2 (drew it out on paper)

def get_middle(surface):
    return WIDTH / 2 - surface.get_width() / 2


def main():
    run = True
    targets = []
    clock = pygame.time.Clock()

    target_pressed = 0
    clicks = 0
    misses = 0
    start_time = time.time() #track how much time has passed since the start of the game to get round duration


    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)  # trigger event every TARGET_INCREMENT milliseconds
     
    while run:
        clock.tick(60)  # Run the game at 60 frames per second
        click = False
        mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position
        elapsed_time = time.time() - start_time  # Calculate elapsed time since the start of the game

        # Event to quit Trigger, listen for target event to add new targets
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == TARGET_EVENT:
                #randomly generate a target position within the screen bounds
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING) #width - paddings makes sure the target is not too close to the edges
                y = random.randint(TARGET_PADDING + HUD_HEIGHT, HEIGHT - TARGET_PADDING)
                
                target = Target(x, y)  # create a new target
                targets.append(target) #add to target list
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1


        #update targets size an position
        for target in targets:
            target.update()

            # If the target is not growing and its size is less than or equal to 0, remove it from the list
            if target.size <= 0:
                targets.remove(target)
                misses += 1 #we didnt press the target in time, so we count it as a miss


            if click and target.collide(*mouse_pos):  # Check if the mouse clicked within the target. * breaks the tuple into separate arguments (x,y)
                targets.remove(target)  # Remove the target if clicked
                target_pressed += 1
            
            if misses >= LIVES:
                end_screen(WIN, elapsed_time, target_pressed, clicks) #end game

        draw_main(WIN, targets)  # draw the targets
        draw_hud(WIN, elapsed_time, target_pressed, misses)  # draw the HUD
        pygame.display.update() #updates everything preceeding this function

    pygame.quit()

if __name__ == "__main__":
    main()


          
