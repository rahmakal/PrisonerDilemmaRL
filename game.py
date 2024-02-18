import torch
import pygame
import sys
import random
from plotter import plot
from model import Linear_Qnet,Qtrainer
from collections import deque
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
class PrisonersDilemmaGameAI:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 400
        self.FPS = 60
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.BLACK = (0, 0, 0)
        self.font = pygame.font.Font(None, 36)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Prisoner's Dilemma Game")
        self.clock = pygame.time.Clock()
        self.p1_choices=[]
        self.p2_choices=[]
        self.p2_strategy=random.choice([0,1,2,3,4])
        self.p1_wins=0
        self.p2_wins=0
        self.ties=0
        self.model=Linear_Qnet(10,256,2)
        self.trainer=Qtrainer(self.model,0.001,0.9)
        self.memory = deque(maxlen=MAX_MEMORY)
        self.epsilon=0
        self.n_games=1
    def reset(self):
        self.n_games+=1
        self.p1_choices=[]
        self.p2_choices=[]
        self.p2_strategy=random.choice([0,1,2,3,4])
        self.screen.fill(self.BLACK)
        pygame.display.flip()
    def tit_for_tat(self):
        if self.p2_choices==[]:
            return 0
        else:
            return self.p1_choices[-1]
    def cooperator(self):
        return 0
    def defector(self):
        return 1
    def randomly(self):
        return random.choice([0,1])
    def sus_tit_for_tat(self):
        if self.p2_choices==[]:
            return 1
        else:
            return self.p1_choices[-1]
    def play_round(self,action):
        #action is either 0 or 1
        choices = ['cooperate', 'betray']
        player1_choice =choices[action]
        if(self.p2_strategy==0):
            ch=self.tit_for_tat()
        if(self.p2_strategy==1):
            ch=self.cooperator()
        if(self.p2_strategy==2):
            ch=self.defector()
        if(self.p2_strategy==3):
            ch=self.randomly()
        if(self.p2_strategy==4):
            ch=self.sus_tit_for_tat()
        player2_choice = choices[ch]
        self.p1_choices.append(action)
        self.p2_choices.append(ch)
        return player1_choice, player2_choice

    def calculate_score(self, player1_choice, player2_choice, player1_score, player2_score):
        if player1_choice == 'cooperate' and player2_choice == 'cooperate':
            player1_score += 2
            player2_score += 2
            reward=1
        elif player1_choice == 'cooperate' and player2_choice == 'betray':
            player1_score += 0
            player2_score += 3
            reward=-10
        elif player1_choice == 'betray' and player2_choice == 'cooperate':
            player1_score += 3
            player2_score += 0
            reward=10
        elif player1_choice == 'betray' and player2_choice == 'betray':
            player1_score += 1
            player2_score += 1
            reward=0
        return player1_score, player2_score,reward

    def display_text(self, text, x, y):
        text_surface = self.font.render(text, True, self.WHITE)
        self.screen.blit(text_surface, (x, y))

    def display_round(self, player1_choice, player2_choice, round_number):
        self.display_text("P1", 20, 50)
        self.display_text("P2", 20, 120)

        pygame.draw.rect(self.screen, self.BLUE if player1_choice == 'cooperate' else self.RED,
                         (50 + round_number * 70, 50, 50, 50))
        pygame.draw.rect(self.screen, self.BLUE if player2_choice == 'cooperate' else self.RED,
                         (50 + round_number * 70, 120, 50, 50))
        
        self.display_text("C" if player1_choice == 'cooperate' else "D", 50 + round_number * 70 + 17, 65)
        self.display_text("C" if player2_choice == 'cooperate' else "D", 50 + round_number * 70 + 17, 135)
    def get_action(self):
        self.epsilon = 200 - self.n_games
        if random.randint(0, 300) < self.epsilon:
            return random.choice([0,1])
        else:
            state=self.p2_choices.copy()
            while(len(state)<10):
                state.append(-1)
            state= torch.tensor(state, dtype=torch.float)
            prediction = self.model(state)
            action = torch.argmax(prediction).item()
            return action
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) 

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
    def run_game(self,action=1):
        
        self.reset()
        rounds = 10
        player1_score = 0
        player2_score = 0
        reward=0
        for round_number in range(rounds):
            old_state=self.p2_choices.copy()
            while(len(old_state)<10):
                old_state.append(-1)
            player1_choice, player2_choice = self.play_round(action)
            player1_score, player2_score ,reward= self.calculate_score(player1_choice, player2_choice,
                                                                 player1_score, player2_score)

            
            self.display_round(player1_choice, player2_choice,round_number)
            pygame.display.flip()
            pygame.time.wait(200)
            new_state=self.p2_choices.copy()
            while(len(new_state)<10):
                new_state.append(-1)
            self.train_short_memory(old_state,action,reward,new_state,round_number==9)
            self.remember(old_state,action,reward,new_state,round_number==9)
            action=self.get_action()

        
        pygame.time.wait(500)

        
        if player1_score > player2_score:
            winner_text = "Player 1 wins!"
            self.p1_wins+=1
            self.model.save()
        elif player2_score > player1_score:
            winner_text = "Player 2 wins!"
            self.p2_wins+=1
            
        else:
            winner_text = "It's a tie!"
            self.ties+=1

        
        self.display_text("Player 1 Score: {}".format(player1_score), 50, 180)
        self.display_text("Player 2 Score: {}".format(player2_score), 50, 200)
        self.display_text(winner_text, 50, 240)
        pygame.display.flip()
        self.train_long_memory()
       


if __name__ == "__main__":
    game= PrisonersDilemmaGameAI()
    
    waiting = True
    while waiting:
        game.run_game()
        pygame.time.wait(500)
        plot(game.p1_wins,game.p2_wins,game.ties)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
    print(game.p1_wins,game.p2_wins,game.ties,game.p1_choices,game.p2_choices)
    
    pygame.quit()
    sys.exit()
        
        
