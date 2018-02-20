import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import pickle
import skimage.transform
import cv2
import IPython
from random import shuffle

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent, TrafficLightAgent, RRTAgent
from gym_urbandriving.assets import Car, TrafficLight

import colorlover as cl



class VizRegristration():

    def __init__(self,cnfg):
        ''' 
        Initialize the VizRegristation Class

        Parameters
        ----------
        cnfig: Config
        configuration class for traffic intersection

        '''

        self.config = cnfg


    def load_frames(self):
        '''
        Load label images to be plotted 
        '''
        self.imgs = []
        for i in range(1,self.config.vz_time_horizon):
            img = cv2.imread(self.config.save_debug_img_path+'img_'+str(i)+'.png')
            self.imgs.append(img)

    def initalize_simulator(self):

        '''
        Initializes the simulator
        '''

        self.vis = uds.PyGameVisualizer((800, 800))

        # Create a simple-intersection state, with no agents
        self.init_state = uds.state.SimpleIntersectionState(ncars=0, nped=0, traffic_lights=True)

        # Create the world environment initialized to the starting state
        # Specify the max time the environment will run to 500
        # Randomize the environment when env._reset() is called
        # Specify what types of agents will control cars and traffic lights
        # Use ray for multiagent parallelism
        self.env = uds.UrbanDrivingEnv(init_state=self.init_state,
                                  visualizer=self.vis,
                                  max_time=500,
                                  randomize=False,
                                  agent_mappings={Car:NullAgent,
                                                  TrafficLight:TrafficLightAgent},
                                  use_ray=False
        )

        self.env._reset(new_state=self.init_state)


    def compute_color_template(self,num_trajectories):
        ''''
        Returns a spectrum of colors that intrepret between two different spectrums 
        The goal is to have unique color for each trajectories

        Parameter
        ------------
        num_trajectories: int
        Number of Trajectories to plot 
        '''

        color_r = np.linspace(255,0,num = num_trajectories)
        color_g = np.linspace(126,0,num = num_trajectories)
        color_b = np.linspace(0,255,num = num_trajectories)
        color_template = []

        for i in range(num_trajectories):

            c_r = int(color_r[i])
            c_g = int(color_g[i])
            c_b = int(color_b[i])

            color_template.append((c_r,c_g,c_b))
       
        shuffle(color_template)
        return color_template



    def visualize_trajectory_dots(self,trajectories,plot_traffic_images = False):
        '''
        Visualize the sperated trajecotries in the simulator and can also visualize the matching images

        Parameter
        ------------
        trajectories: list of Trajectory 
        A list of Trajectory Class

        plot_traffic_images: bool
        True if the images from the traffic cam should be shown alongside the simulator 
        '''
        self.initalize_simulator()
        if plot_traffic_images:
            self.load_frames()
        

        active_trajectories = []
        way_points = []

        color_template = self.compute_color_template(len(trajectories))

        color_index = 0
        for t in range(self.config.vz_time_horizon):

            for traj_index in range(len(trajectories)):

                traj = trajectories[traj_index]
                
                if t == traj.initial_time_step:
                    
                    color_match = [traj,color_template[color_index]]
                    active_trajectories.append(color_match)
                    color_index += 1
            
            
            for traj_index in range(len(active_trajectories)):

                traj = active_trajectories[traj_index][0]
                next_state,valid = traj.get_next_state()


                if valid:
                    w_p = [next_state,active_trajectories[traj_index][1]]
                    way_points.append(w_p)


            ###Render Images on Simulator and Traffic Camera 
            self.env._render(traffic_trajectories = way_points)
            
            if plot_traffic_images:
                cv2.imshow('img',self.imgs[t])
                cv2.waitKey(30)
                t+=1


        return

    def visualize_homography_points(self):
        ''' 
        Plot the correspnding homography ponts
        Assumes load_frames has been called
        '''

        self.initalize_simulator()
        img = self.imgs[0]

        for i in range(3):

            point = self.config.street_corners[i,:]

            img[point[1]-5:point[1]+5,point[0]-5:point[0]+5,:]=255

        waypoints = []

        for i in range(3):
            point = self.config.simulator_corners[i,:]
            waypoints.append(point)

        while True:
            self.env._render(waypoints = waypoints)     
            cv2.imshow('img',img)
            cv2.waitKey(30)



