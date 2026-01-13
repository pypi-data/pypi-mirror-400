import gymnasium
import numpy as np
import table_rl
from pdb import set_trace
from collections import Counter

class Roulette(gymnasium.Env):
    '''
        Implements the Roulette Environment from Hado van Hasselt's 2010 NIPS paper: Double Q-learning
    '''
    def __init__(self): # DONE
        self.observation_space = gymnasium.spaces.Discrete(2) # 1 state + a terminal state
        self.action_space = gymnasium.spaces.Discrete(171)
        self.construct_transition()
        self.construct_reward()
        self.terminal_state = 1

        
    def construct_transition(self):
        T = np.zeros((self.observation_space.n, self.action_space.n, self.observation_space.n))
        T[0,1:,0] = 1.0  # State 0 transitions to itself with almost all actions except action 0
        T[0,0,1] = 1.0  # Action 0 transitions to state terminal
        T[1,:,1] = 1.0 # State 1, a terminal state transitions to itself with all actions
        table_rl.dp.dp.check_valid_transition(T)
        self.T = T

    def construct_reward(self):

        # taken from Double Q-learning paper
        self.odds =       [ ('number ' + str(i),                                         35.,1./38.) for i in range(-1,37 ) ]
        self.odds.append(   ('split 00,0',                                               17.,2./38.) )
        self.odds.extend( [ ('split '+str(i+1)+','+str(i+2),                             17.,2./38.) for i in range( 0,36,3 ) ] )
        self.odds.extend( [ ('split '+str(i+1)+','+str(i+2),                             17.,2./38.) for i in range( 1,36,3 ) ] )
        self.odds.extend( [ ('split '+str(i+1)+','+str(i+4),                             17.,2./38.) for i in range( 0,33,3 ) ] )
        self.odds.extend( [ ('split '+str(i+1)+','+str(i+4),                             17.,2./38.) for i in range( 1,33,3 ) ] )
        self.odds.extend( [ ('split '+str(i+1)+','+str(i+4),                             17.,2./38.) for i in range( 2,33,3 ) ] )
        self.odds.extend( [ ('basket 0,1,2',11,3./38.),('basket 0,00,2',                 11.,3./38.),('basket 00,2,3',11,3./37.) ] )
        self.odds.extend( [ ('street '+str(i+1)+','+str(i+2)+','+str(i+3),               11.,3./38.) for i in range(0,36,3) ] )
        self.odds.extend( [ ('corner '+str(i+1)+','+str(i+2)+','+str(i+4)+','+str(i+5),  8., 4./38.) for i in range( 0,36,3 )] )
        self.odds.extend( [ ('corner '+str(i+1)+','+str(i+2)+','+str(i+4)+','+str(i+5),  8., 4./38.) for i in range( 1,36,3 )] )
        self.odds.extend( [ ('top line ',                                                6., 5./38.) for i in range( 1,36,3 )] )
        self.odds.extend( [ ('six line '+str(i+1),                                       5., 6./38.) for i in range( 0,33,3 ) ] )
        self.odds.extend( [ ('column '+str(i+1),                                         2., 12./38.) for i in range( 3 ) ] )
        self.odds.extend( [ ('dozen '+str(i+1),                                          2., 12./38.) for i in range( 3 ) ] )
        self.odds.extend( [ ('odd',                                                      1., 18./38.) ] )
        self.odds.extend( [ ('even',                                                     1., 18./38.) ] )
        self.odds.extend( [ ('red',                                                      1., 18./38.) ] )
        self.odds.extend( [ ('black',                                                    1., 18./38.) ] )
        self.odds.extend( [ ('1-18',                                                     1., 18./38.) ] )
        self.odds.extend( [ ('18-36',                                                    1., 18./38.) ] )
        
        self.win = [odd[1] for odd in self.odds]
        self.probs = [odd[2] for odd in self.odds]
        values = [odd[2] for odd in self.odds]
        # set_trace()
        # print(values)
        rewards_and_counts = [(1./19., 58), (1./38., 38), (2./19., 24), (3./38., 14),
                              (5. / 38., 12), (3./19., 11), (6./19., 6), (9./19., 6),
                              (3./ 37., 1)]
        total_count = sum([reward_count[1] for reward_count in rewards_and_counts])
        rewards = []
        for reward, count in rewards_and_counts:
            for _ in range(count):
                rewards.append(reward)
        assert len(rewards) == 170, f"Expected 170 rewards, got {len(rewards)}"
        equals = sorted(rewards) == sorted(values)
        R = np.zeros((self.observation_space.n, self.action_space.n, self.observation_space.n))
        R[1,:,:] = 0.0 # Terminal state has no rewards
        R[0,0,1] = 0.0 # Transition to terminal state has no rewards
        for i in range(len(rewards)):
            action = i + 1
            R[0, action, 0] = rewards[i]  # Rewards for all actions from state 0
        self.R = R


    def step(self, action):
        next_state = np.random.choice(self.observation_space.n, p=self.T[self.current_state, action])
        terminated = next_state == self.terminal_state
        if next_state == self.terminal_state:
            if self.current_state == 0:
                # If we are in the initial state, only action 0 can lead to the terminal state
                assert action == 0, "Only action 0 can lead to the terminal state."   
        if action == 0:
            reward = 0.0
        else:
            if np.random.random() < self.probs[action - 1]:
                print(self.probs[action - 1])
                reward = self.win[action - 1]
                print(f"Action {action} won with reward {reward}")
            else:
                reward = -1.0
        self.current_state = next_state
        return next_state, reward, terminated, False, {}

    def reset(self):
        self.current_state = 0
        return 0, {}
