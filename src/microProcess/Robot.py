from rich.console import Console
from rich.table import Table
from rich import print
from datetime import datetime, timedelta
from Action import Action
from multiprocessing import Value


class Robot:
    def __init__(self, max_storage_per_slot=3):
        # self.storage = {1: [[], 0], 2: [[], 0], 3: [[], 0]}  # storage areas, initialized with empty lists and 0 points

        self.storage = ['', '', '']
        # simpler position management, and semaphores
        self._x, self._y, self._h, self.arm_x = Value('f'), Value('f'), Value('f'), 0

        # odometry variables
        # self.odometry = {'current_speed': 0, 'position': [0, 0], 'goal': None, 'current_action': None}
        self.max_storage_per_slot = max_storage_per_slot  # maximum number of objects in the inside storage compartment
        self.actions_emitted = []

    def move_cake(self, src, destination):
        cake = self.storage[src][-1]
        self.storage[src] = self.storage[src][:-1]
        self.storage[destination] += cake

    @property
    def x(self):
        return self._x.value

    @x.setter
    def x(self, value):
        self._x.value = value

    @property
    def y(self):
        return self._y.value

    @y.setter
    def y(self, value):
        self._y.value = value

    @property
    def h(self):
        return self._h.value

    @h.setter
    def h(self, value):
        self._h.value = value

    def incr(self, attr, value):
        attr = getattr(self, f'_{attr}')
        with attr.get_lock():
            attr.value += value

    def add_object(self, colors, slot_number):
        """Add objects to the specified storage slot and check for point-earning combinations."""

        if slot_number < 1 or slot_number > len(self.storage):
            raise ValueError("Invalid slot number.")
        
        for color in colors:
            if color not in ['B', 'Y', 'P']:
                raise ValueError("Invalid color.")
            
            if slot_number == 2 and len(self.storage[slot_number][0]) >= self.max_storage_per_slot:
                raise ValueError("Inside storage compartment is full.")
            
            if len(self.storage[slot_number][0]) >= self.max_storage_per_slot:
                raise ValueError("Storage compartment is full.")
            
            # Add the object to the storage area
            self.storage[slot_number][0].append(color)
            
        # Check for point-earning combinations
        self.count_points(slot_number)

        # Emit an action
        action = Action(
            name="Add Object",
            subject="Robot",
            description=f"Added {len(colors)} objects to storage slot {slot_number}.",
            receiver="Robot",
            emission_date=datetime.now(),
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=1)
        )
        self.actions_emitted.append(action)

    def get_storage(self):
        """Return the current objects in each storage area."""
        return self.storage

    # def update_odometry(self, current_speed=None, position=None, goal=None, current_action=None):
    #     if current_speed is not None:
    #         self.odometry['current_speed'] = current_speed
    #     if position is not None:
    #         self.odometry['position'] = position
    #     if goal is not None:
    #         self.odometry['goal'] = goal
    #     if current_action is not None:
    #         self.odometry['current_action'] = current_action

    # def get_current_position(self):
    #     """Return the current position of the robot."""
    #     return self.odometry['position']
    #
    # def get_current_speed(self):
    #     """Return the current speed of the robot."""
    #     return self.odometry['current_speed']
    #
    # def set_action(self, current_action):
    #     """Set the name of the current action of the robot."""
    #     self.odometry['current_action'] = current_action
    #
    # def get_current_action(self):
    #     """Return the current action of the robot."""
    #     return self.odometry['current_action']
    
    # def get_goal(self):
    #     """Return the current goal of the robot."""
    #     return self.odometry['goal']
    #
    # def set_goal(self, goal):
    #     """Set the goal of the robot."""
    #     self.odometry['goal'] = goal

    def get_total_points(self):
        """Return the total number of points the robot has earned."""
        return sum([self.storage[slot_number][1] for slot_number in self.storage])
    
    def get_available_storage(self, slot=None):
        """Return the number of available storage slots. If a slot number is entered, return the number of available storage slots in that slot."""
        if slot is None:
            return sum([1 for slot_number in self.storage if len(self.storage[slot_number][0]) < 3])
        else:
            return self.max_storage_per_slot - len(self.storage[slot][0])
        
    def clear_storage(self):
        """Clear all the storage areas."""
        self.storage = {1: ([], 0), 2: ([], 0), 3: ([], 0)}

    # def move_to_goal(self, goal):
    #     """
    #     Move the robot to the specified goal position and update its odometry.
    #     """
    #     current_position = self.odometry['position']
    #     # TODO: implement pathfinding algorithm to determine best route from current_position to goal
    #     # For now, assume the robot moves directly to the goal position in a straight line.
    #     distance = ((goal[0] - current_position[0])**2 + (goal[1] - current_position[1])**2)**0.5
    #     time = distance / self.odometry['current_speed']
    #     self.odometry['position'] = goal
    #     self.odometry['goal'] = None
    #     self.odometry['current_action'] = f"Moved to goal {goal} in {time} seconds."

    def count_points(self, slot_number=None):
        """Count the total points for a specific storage slot."""
        if slot_number is None: 
            test = sum([self.count_points(slot_number) for slot_number in self.storage])
            print("[bold red]Oui[bold red]", test)
            return sum([self.count_points(slot_number) for slot_number in self.storage])
        
        if slot_number < 1 or slot_number > len(self.storage):
            raise ValueError("Invalid slot number.")
        test = sum([1 for objects in self.storage[slot_number][0]])
        points = sum([1 for objects in self.storage[slot_number][0]])  # points for this slot only
        # Now let's check if [B, Y, P] is among the objects in this slot while keeping in mind that the size of the slot might vary according to self.max_storage_per_slot
        for i in range(len(self.storage[slot_number][0])):
            if self.storage[slot_number][0][i:i+3] == ['B', 'Y', 'P']:
                points += 4
            if i+3 >= len(self.storage[slot_number][0]):
                break
        
        # Now modify the storage area to reflect the points earned
        print(self.storage[slot_number])
        self.storage[slot_number][1] = points

    # def swap_objects(self, slot1, slot2):
    #     """ Swap the 2 top colors of the specified slots. """
    #     if slot1 < 1 or slot1 > len(self.storage) or slot2 < 1 or slot2 > len(self.storage):
    #         raise ValueError("Invalid slot number.")
    #
    #     if self.storage[slot1][0] == [] or self.storage[slot2][0] == []:
    #         raise ValueError("One of the slots is empty.")
    #
    #     self.storage[slot1][0][-1], self.storage[slot2][0][-1] = self.storage[slot2][0][-1], self.storage[slot1][0][-1]
    #
    #     # Let's re-count the points for both slots
    #     self.count_points(slot1)
    #     self.count_points(slot2)
    
    """def __str__(self):
        console = Console()
        table = Table(title="Robot Storage", show_header=True, header_style="bold magenta")
        table.add_column("Slot", style="cyan")
        table.add_column("Objects", style="green")
        table.add_column("Points", style="magenta")

        for i in range(1, len(self.storage)+1):
            slot = f"{i}"
            objects = ", ".join(self.storage[i][0])
            points = f"{self.storage[i][1]}"
            table.add_row(slot, objects, points)

        total_points = sum([self.storage[slot_number][1] for slot_number in self.storage])

        odometry_str = f"[bold magenta]Odometry:[/bold magenta] {self.odometry}"
        total_points_str = f"[bold magenta]Total points:[/bold magenta] {total_points}"
        console.print(table)
        console.print(odometry_str)
        console.print(total_points_str)
        return """""
    
    def __str__(self):
        console = Console()

        # Storage table
        table = Table(title="Robot Storage", show_header=True, header_style="bold magenta")
        table.add_column("Slot", style="cyan")
        table.add_column("Objects", style="green")
        table.add_column("Points", style="magenta")

        for i in range(1, len(self.storage)+1):
            slot = f"{i}"
            objects = ", ".join(self.storage[i][0])
            points = f"{self.storage[i][1]}"
            table.add_row(slot, objects, points)

        total_points = sum([self.storage[slot_number][1] for slot_number in self.storage])
        total_points_str = f"[bold magenta]Total points:[/bold magenta] {total_points}"

        # Actions table
        actions_table = Table(title="Robot Actions", show_header=True, header_style="bold magenta")
        actions_table.add_column("Name", style="cyan")
        actions_table.add_column("Subject", style="green")
        actions_table.add_column("Description", style="magenta")
        actions_table.add_column("Emission Date", style="magenta")
        actions_table.add_column("End Date", style="magenta")

        for action in self.actions_emitted:
            name = action.name
            subject = action.subject
            description = action.description
            emission_date = action.emission_date.strftime('%Y-%m-%d %H:%M:%S')
            end_time = action.end_time.strftime('%Y-%m-%d %H:%M:%S') if action.end_time is not None else ""
            actions_table.add_row(name, subject, description, emission_date, end_time)

        # Print tables and information
        console.print(table)
        console.print(total_points_str)
        console.print(actions_table)

        return ""


# Main program
methods_test_unit = True 
if '__main__' == __name__:


    # Create a new robot instance with a maximum inside storage compartment length of 2
    robot = Robot(max_storage_per_slot=3)

    console = Console()

    if methods_test_unit:
        # Add some objects and print the robot
        try:
            robot.add_object('B', 4)
        except ValueError as e:
            console.print(f"[bold red]{e}[/bold red]")
        console.print("After adding 'B' to slot 4:")
        console.print(robot)

        robot.add_object('B', 1)
        console.print("After adding 'B' to slot 1:")
        console.print(robot)

        robot.add_object('Y', 1)
        console.print("After adding 'Y' to slot 1:")
        console.print(robot)

        try:
            robot.add_object('B', 2)
        except ValueError as e:
            console.print(f"[bold red]{e}[/bold red]")
        console.print("After trying to add 'B' to slot 2:")
        console.print(robot)

        try:
            robot.add_object('P', 1)
        except ValueError as e:
            console.print(f"[bold red]{e}[/bold red]")
        console.print("After trying to add 'P' to slot 1:")
        console.print(robot)

        # Try to add more objects than allowed per storage compartment and print the robot
        try:
            robot.add_object('B', 1)
        except ValueError as e:
            console.print(f"[bold red]{e}[/bold red]")
        console.print("After trying to add 'B' to slot 1:")
        console.print(robot)

        # Try to swap objects in a slot that doesn't exist
        try:
            robot.swap_objects(1, 4)
        except ValueError as e:
            console.print(f"[bold red]{e}[/bold red]")

        # Test swapping objects in slots 1 and 2
        console.print("Test swapping objects in slots 1 and 2")
        console.print("Before swap:")
        console.print(robot)
        try:
            robot.swap_objects(1, 2)
        except ValueError as e:
            console.print(f"[bold red]{e}[/bold red]")
        console.print("After swap:")
        console.print(robot)

        # Test the get_available_storage method
        console.print("Test the get_available_storage method")
        console.print("Total available storage:", robot.get_available_storage())
        console.print("Available storage in slot 1:", robot.get_available_storage(1))
        console.print("Available storage in slot 2:", robot.get_available_storage(2))

        # Test the get_total_points method
        console.print("Test the get_total_points method")
        console.print("Total points:", robot.get_total_points())


        # Test the update_odometry method
        console.print("[bold green]Test the update_odometry method[/bold green]")
        print(robot)
        robot.update_odometry(current_speed=1, position=[1,2],current_action="move")
        print(robot)

        # Test the get_current_position method again
        console.print("[bold green]Test the get_current_position method again[/bold green]")
        console.print("Current position:", robot.get_current_position())






