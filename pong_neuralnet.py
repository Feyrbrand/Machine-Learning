# building simple pong
# learing through deep-q-learning
# version 0.0.1
# using pygame for game environment

import pygame
import random   # defines random direction of the ball

# define variables for the game
FPS = 60

# size of the window
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400

# size of the paddle of the player
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 60
PADDLE_BUFFER = 10

# size of the playing ball
BALL_WIDTH = 10
BALL_HEIGHT = 10

# speed of the playing ball & the paddle
# can be adjusted, by powerups
PADDLE_SPEED = 2
BALL_SPEED_X = 3
BALL_SPEED_Y = 2

# RGB colors for the paddle & ball
WHITE = ( 255, 255, 255)
BLACK = ( 0, 0, 0)

# screen initialization
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# draw the ball in the screen
def drawBall(ballPosX, ballPosY):
    ball = pygame.Rect(ballPosX, ballPosY, BALL_WIDTH, BALL_HEIGHT)
    pygame.draw.rect(screen, WHITE, ball)

# using the paddle_buffer for screen limitations
def drawPaddle1(paddle1PosY):
    paddle1 = pygame.Rect(PADDLE_BUFFER, paddle1PosY, PADDLE_WIDTH, PADDLE_HEIGHT)
    pygame.draw.rect(screen, WHITE, paddle1)

def drawPaddle2(paddle2PosY):
    paddle2 = pygame.Rect(WINDOW_WIDTH - PADDLE_BUFFER - PADDLE_WIDTH, paddle2PosY, PADDLE_WIDTH, PADDLE_HEIGHT)
    pygame.draw.rect(screen, WHITE, paddle2)

# function to update the position of the ball
# is depending on the current paddle pos
def updateBall(paddle1PosY, paddle2PosY, ballPosX, ballPosY, ballDirectionX, ballDirectionY):

    # update the x and y position of the ball
    ballPosX = ballPosX + ballDirectionX * BALL_SPEED_X
    ballPosY = ballPosY + ballDirectionY * BALL_SPEED_Y
    score = 0

    # collision check, switch dir of the ball, to get collisions
    # if the ball hits left side, switch direction
    if(ballPosX <= PADDLE_BUFFER + PADDLE_WIDTH 
        and ballPosY + BALL_HEIGHT >= paddle1PosY 
        and ballPosY - BALL_HEIGHT <= paddle1PosY + PADDLE_HEIGHT):
        # change direcions
        ballDirectionX = 1 
    
    # set score if ball is out of the window
    elif(ballPosX <= 0):
        ballDirectionX = 1
        score = -1
        return [score, paddle1PosY, paddle2PosY, ballPosX, ballPosY, ballDirectionX, ballDirectionY]
    
    # check if the ball hits the right side, switch directions
    if(ballPosX >= WINDOW_WIDTH - PADDLE_WIDTH - PADDLE_BUFFER 
        and ballPosY + BALL_HEIGHT >= paddle2PosY 
        and ballPosY - BALL_HEIGHT <= paddle2PosY + PADDLE_HEIGHT):
        # change directions
        ballDirectionX = -1

    # set score if ball is out of the window
    elif(ballPosX >= WINDOW_WIDTH - BALL_WIDTH):
        ballDirectionX = -1
        score = 1
        return [score, paddle1PosY, paddle2PosY, ballPosX, ballPosY, ballDirectionX, ballDirectionY]

    # if ball hits top , change directions
    if(ballPosY <= 0):
        ballPosY = 0
        ballDirectionY = 1
    
    # or bottom, change directions
    elif(ballPosY >= WINDOW_HEIGHT - BALL_HEIGHT):
        ballPosY = WINDOW_HEIGHT - BALL_HEIGHT
        ballDirectionY = -1
    
    return [score, paddle1PosY, paddle2PosY, ballPosX, ballPosY, ballDirectionX, ballDirectionY]


# update paddle1 position 
def updatePaddle1(action, paddle1PosY):
    
    # if paddle moves up
    if(action[1] == 1):
        paddle1PosY = paddle1PosY - PADDLE_SPEED    

    # if paddle moves down
    if(action[2] == 1):
        paddle1PosY = paddle1PosY + PADDLE_SPEED

    # implement screen boundaries
    if(paddle1PosY < 0):
        paddle1PosY = 0 
    if(paddle1PosY > WINDOW_HEIGHT - PADDLE_HEIGHT):
        paddle1PosY = WINDOW_HEIGHT - PADDLE_HEIGHT

    return paddle1PosY

# update paddle2 position, knows ball position
def updatePaddle2(paddle2PosY, ballPosY):

    #move down if ball is in upper half
    if (paddle2PosY + PADDLE_HEIGHT/2 < ballPosY + BALL_HEIGHT/2):
        paddle2PosY = paddle2PosY + PADDLE_SPEED
    
    #move up if ball is in lower half
    if (paddle2PosY + PADDLE_HEIGHT/2 > ballPosY + BALL_HEIGHT/2):
        paddle2PosY = paddle2PosY - PADDLE_SPEED
    
    #don't let it hit top
    if (paddle2PosY < 0):
        paddle2PosY = 0
    
    #dont let it hit bottom
    if (paddle2PosY > WINDOW_HEIGHT - PADDLE_HEIGHT):
        paddle2PosY = WINDOW_HEIGHT - PADDLE_HEIGHT
    
    return paddle2PosY

# init the Pong Game
class PongGame:
    def __init__(self):

        # random number for init direction of the ball, fairness
        num = random.randint(0, 9)

        # keep the score
        self.tally = 0

        # init position of our paddle (1)
        # starting in the middle of the screen
        self.paddle1PosY = WINDOW_HEIGHT /2 - PADDLE_HEIGHT /2
        self.paddle2PosY = WINDOW_HEIGHT /2 - PADDLE_HEIGHT /2

        # define ball direction
        self.ballDirectionX = 1
        self.ballDirectionY = 1

        # starting pos of the ball
        self.ballPosX = WINDOW_WIDTH /2 - BALL_WIDTH /2

        # randomly decide where the ball will move 
        if(0 < num < 3):
            self.ballDirectionX = 1
            self.ballDirectionY = 1
        if (3 <= num < 5):
            self.ballDirectionX = -1
            self.ballDirectionY = 1
        if (5 <= num < 8):
            self.ballDirectionX = 1
            self.ballDirectionY = -1
        if (8 <= num < 10):
            self.ballDirectionX = -1
            self.ballDirectionY = -1
        
        # new random number
        num = random.randint(0,9)

        # where it will start, y part
        self.ballPosY = num*(WINDOW_HEIGHT - BALL_HEIGHT)/9

    # need framedata for the q learning algorithm
    # gives a score for try and error learning
    def getPresentFrame(self):

        # for each frame, call the event queue
        pygame.event.pump()

        # setting the background to black
        screen.fill(BLACK)

        # draw the paddles
        drawPaddle1(self.paddle1PosY)
        drawPaddle2(self.paddle2PosY)

        # draw the ball
        drawBall(self.ballPosX, self.ballPosY)

        # get the pixels of the hole game, in one state
        image_data = pygame.surfarray.array3d(pygame.display.get_surface())

        # update the window
        pygame.display.flip()

        # return the screen data, from the current state
        return image_data

    # get the data of the next Frame state
    def getNextFrame(self, action):
        pygame.event.pump()
        score = 0
        screen.fill(BLACK)

        # update both paddle at the same time
        self.paddle1PosY = updatePaddle1(action, self.paddle1PosY)
        drawPaddle1(self.paddle1PosY)
        self.paddle2PosY = updatePaddle2(self.paddle2PosY, self.ballPosY)
        drawPaddle2(self.paddle2PosY)

        # updating all variables, by updateing the ball position
        [score, self.paddle1PosY, self.paddle2PosY, self.ballPosX, self.ballPosY, self.ballDirectionX, self.ballDirectionY] = updateBall(self.paddle1PosY, self.paddle2PosY, self.ballPosX, self.ballPosY, self.ballDirectionX, self.ballDirectionY)

        # draw the state of the ball
        drawBall(self.ballPosX, self.ballPosY)

        image_data = pygame.surfarray.array3d(pygame.display.get_surface())

        # refresh display state
        pygame.display.flip()

        # update score
        self.tally = self.tally + score
        print ("Tally is " + str(self.tally))

        # those values are returned to the learning algorithm
        return [score, image_data]









