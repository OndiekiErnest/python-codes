import math

class Movements():
        
    def __init__(self):
        self.origin = [0,0]

    @property
    def distance(self):
        return math.sqrt((self.origin[0]**2)+(self.origin[1]**2))


    def move_up(self, units):
        self.origin[1] +=int(units)
        return self.origin
    
    def move_down(self, units):
        self.origin[1] -=int(units)
        return self.origin

    def move_right(self, units):
        self.origin[0] +=int(units)
        return self.origin

    def move_left(self, units):
        self.origin[0] -=int(units)
        return self.origin
    
if __name__ == "__main__":
    self = Movements()
    while True:
        user = input("\nEnter (up 5): ").upper().split()
        if not user or len(user) != 2:
            print(f"{self.distance:.2f}")
            break
        elif user[0] == "UP":
            print("\t:", self.move_up(user[1]))
        elif user[0] == "DOWN":
            print("\t:", self.move_down(user[1]))
        elif user[0] == "RIGHT":
            print("\t:", self.move_right(user[1]))
        elif user[0] == "LEFT":
            print("\t:", self.move_left(user[1]))
