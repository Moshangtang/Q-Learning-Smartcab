import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here

        self.successes = []  # to store the the result of each trial
        self.trail_reward_list =[] # to store the total reward for each trial

        # set a new Q dictionary
        self.set_Q_Dic()


    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

        # save the destination
        self.destination = destination
        # reset the trial_reward for each trial
        self.trial_reward = 0


    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = {  "light":inputs["light"],
                        "oncoming":inputs["oncoming"],
                        "left": inputs["left"],
                        "direction": self.next_waypoint}

        # TODO: Select action according to your policy
        action = self.action_by_policy(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)
        self.trial_reward += reward # record the total reward

        # TODO: Learn policy based on state, action, reward

        self.update_Q_Dic(self.state, action, reward)


        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]

        # save the result for each trial in self.successes list
        location = self.env.agent_states[self]['location']
        if location == self.destination:
            self.successes.append(1)
            self.trail_reward_list.append(self.trial_reward)




    def action_by_policy(self, state):

        action_list = []
        state_key = (state['light'], state['oncoming'], state['left'], state['direction'])
        Q_item = self.Q_Dic[state_key]
        max_Q = max(Q_item.values()) # find the max Q value
        for key, value in Q_item.iteritems():
            if value == max_Q:
                action_list.append(key)
        action = random.choice(action_list)
        return action



    def update_Q_Dic(self, state, action, reward):

        learning_rate = 0.5
        gamma = 0.5
        # transform state to the Q dictionary key
        state_key = (state['light'], state['oncoming'], state['left'], state['direction'])
        inputs = self.env.sense(self)
        direction = self.planner.next_waypoint()
        next_state_key = (inputs['light'], inputs['oncoming'], inputs['left'], direction)
        max_Q = max(self.Q_Dic[next_state_key].values())
        # Q learning equation
        self.Q_Dic[state_key][action] = (1 - learning_rate) * self.Q_Dic[state_key][action] + learning_rate * (reward + gamma * max_Q)



    def set_Q_Dic(self):

        # initialize Q dictionary
        self.Q_Dic = {}
        valid_actions = [None, 'forward', 'left', 'right']
        for light in ['green','red']:
            for oncoming in valid_actions:
                for left in valid_actions:
                    for direction in valid_actions:
                        self.Q_Dic[(light, oncoming, left, direction)] = {'forward':0, 'left':0, 'right':0, None:0}



def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline = True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.05, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

    succeed_times = sum(a.successes)
    print "The success rate is :{}%".format(succeed_times) # the total trial is 100
    #print a.trail_reward_list

if __name__ == '__main__':
    run()
