from datetime import datetime
from datetime import timedelta
from rich.console import Console
from rich import print


class Action:
    def __init__(self, name, subject, description, receiver=None, emission_date=None, start_time=None, end_time=None):
        self.name = name
        self.subject = subject
        self.description = description
        self.receiver = receiver
        self.emission_date = emission_date if emission_date is not None else datetime.now()
        self.start_time = start_time or datetime.now()
        self.end_time = end_time

    def set_receiver(self, receiver):
        self.receiver = receiver

    def set_end_date(self, end_date):
        self.end_time = end_date

    def is_expired(self):
        if self.end_time is None:
            return False
        return datetime.now() > self.end_time

    def __str__(self):
        console = Console()
        start_time_str = self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else ""
        end_time_str = self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else ""
        console.print(f"[bold blue]{self.name}[/bold blue]\n"
                      f"Subject: [italic]{self.subject}[/italic]\n"
                      f"Description: {self.description}\n"
                      f"Receiver: {self.receiver}\n"
                      f"Start time: {start_time_str}\n"
                      f"End time: {end_time_str}")

        return ""


if '__main__' == __name__:

    # Create console 
    console = Console()
    # Create an action
    action = Action("Order Supplies", "Office Supplies", "Order more paper and pens.")

    # Set the receiver and end date
    action.set_receiver("John Smith")
    action.set_end_date(datetime.now() + timedelta(days=7))

    # Print the action
    print(action)

    # Test if the action is expired
    action.set_end_date(datetime.now())
    if action.is_expired():
        console.print(f"The action '{action.name}' has expired.")