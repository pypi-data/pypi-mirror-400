from math import *

class Rocket():
    # Rocket simulates a rocket ship for a game,
    #  or a physics simulation.
    
    def __init__(self, x=0, y=0):
        # Each rocket has an (x,y) position.
        self.x = x
        self.y = y
        
    def move_rocket(self, x_increment=0, y_increment=1):
        # Move the rocket according to the paremeters given.
        #  Default behavior is to move the rocket up one unit.
        self.x += x_increment
        self.y += y_increment
        
    def get_distance(self, other_rocket):
        # Calculates the distance from this rocket to another rocket,
        #  and returns that value.
        distance = sqrt((self.x-other_rocket.x)**2+(self.y-other_rocket.y)**2)
        return distance
    
    def __str__(self):
        return f"A Rocket positioned at ({self.x},{self.y})"

    def __repr__(self):
        return f"Rocket({self.x},{self.y})"
    def __eq__(self, other):
        print("the __eq__  is called ") 
        return (self.x == other.x) and (self.y == other.y)
    
class Shuttle(Rocket):
    # Shuttle simulates a space shuttle, which is really
    #  just a reusable rocket.
    
    def __init__(self, x=0, y=0, flights_completed=0):
        super().__init__(x, y)
        self.flights_completed = flights_completed

class circleRocket(Rocket):
     def __init__(self, x=0, y=0, r=0):
          super().__init__(x, y)
          self.radius = r  # Change variable name from 'r' to 'radius'
       
     def get_area(self):
         return pi * pow(self.radius, 2)  # Use self.radius
   
     def get_circumference(self):
         return 2 * pi * self.radius  # Use self.radius