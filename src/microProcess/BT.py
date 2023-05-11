from abc import ABC, abstractmethod
from rich.console import Console
from rich.tree import Tree
from rich import print
from rich.text import Text
from rich.style import Style
from rich.logging import RichHandler
import logging
import datetime


class BehaviourTreeNode(ABC):

    FAILURE = "FAILURE"
    SUCCESS = "SUCCESS"
    RUNNING = "RUNNING"

    logger = logging.getLogger(__name__)
    logger.addHandler(RichHandler())

    def __init__(self, name, node_type):
        """
        Initializes a BehaviourTreeNode object.

        Args:
            name (str): The name of the node.
            node_type (str): The type of the node.
        """
        self.name = name
        self.node_type = node_type

    @abstractmethod
    def tick(self, prefix='', verbose=False) -> int:
        """
        Abstract method to be implemented by subclasses.
        Performs the tick operation on the node.

        Args:
            prefix (str): Prefix for log messages (default '').
            verbose (bool): Whether to enable verbose logging (default False).

        Returns:
            int: Result of the tick operation.
        """
        pass
    
    def log(self, message, level=logging.DEBUG,verbose=True):
        """
        Logs a message using the logger and prints it to the console.

        Args:
            message (str): The message to be logged.
            level (int): Log level (default logging.DEBUG).
            verbose (bool): Whether to enable verbose logging (default True).

        Returns:
            Logs in the terminal if enabled.
        """
        if verbose:
            console = Console()
            if self.node_type == "Action":
                log_msg = f"[bold magenta]{self.node_type}[/] {self.name} -> {message}"
            elif self.node_type == "Fallback":
                log_msg = f"[bold green]{self.node_type}[/] {self.name} -> {message}"
            elif self.node_type == "Condition":
                log_msg = f"[bold blue]{self.node_type}[/] {self.name} -> {message}"
            elif self.node_type == "Sequence":
                log_msg = f"[bold yellow]{self.node_type}[/] {self.name} -> {message}"
            else:
                log_msg = f"{self.node_type},{self.name} -> : {message}"
            self.logger.log(level, log_msg)
            console.log(log_msg)

    def __str__(self):
        """
        Returns a string representation of the BehaviourTreeNode.

        Args:
            None
        
        Returns:
            tree (rich.Tree): Tree representation of the BehaviourTreeNode.
        """
        tree = Tree()
        for child in self.children:
            tree.add(child.__str__())
        return tree


class SequenceNode(BehaviourTreeNode):

    def __init__(self, name, children: list):
        """
        Initializes a SequenceNode object.

        Args:
            name (str): The name of the node.
            children (list): List of child nodes.
        """
        super().__init__(name,"Sequence")
        self.children = children
        self.node_type = "Sequence"

    def tick(self, prefix='', verbose=False) -> str:
        """
        Performs the tick operation on the SequenceNode. 
        The node will tick each child in order (first to last) until one returns FAILURE or RUNNING.
        If all children return SUCCESS, the node returns SUCCESS.

        Args:
            prefix (str): Prefix for log messages (default '').
            verbose (bool): Whether to enable verbose logging (default False).

        Returns:
            int: Result of the tick operation.
            SUCCESS: If all children return SUCCESS.
            FAILURE: If any child returns FAILURE.
        """
        self.log(f"STARTED")
        for child in self.children:
            result = child.tick(prefix=f"{prefix}==", verbose=verbose)
            if result != BehaviourTreeNode.SUCCESS:
                self.log(f"FAILURE")
                return result
        self.log(f"SUCCESS")
        return BehaviourTreeNode.SUCCESS

    def __str__(self, prefix=''):
        """
        Returns a string representation of the SequenceNode.

        Args:
            prefix (str): Prefix for log messages (default '').

        Returns:
            tree (rich.Tree): Tree representation of the SequenceNode.
        """

        tree = Tree(f"{prefix}[bold yellow]Sequence [/]{self.name}", guide_style="bold blue")
        for child in self.children:
            tree.add(child.__str__())
        return tree


class FallbackNode(BehaviourTreeNode):

    def __init__(self, name, children: list):
        """
        Initializes a FallbackNode object.

        Args:
            name (str): The name of the node.
            children (list): List of child nodes.
        """
        super().__init__(name,"Fallback")
        self.children = children
        self.node_type = "Fallback"
        self.logger = logging.getLogger(name)
    
    def tick(self, prefix='', verbose=False) -> int:
        """
        Performs the tick operation on the FallbackNode. 
        The node will tick each child in order (first to last) until one returns SUCCESS or RUNNING.

        Args:
            prefix (str): Prefix for log messages (default '').
            verbose (bool): Whether to enable verbose logging (default False).

        Returns:
            int: Result of the tick operation.
        """
        self.log(f"STARTED")
        for child in self.children:
            result = child.tick(prefix=f"{prefix}==", verbose=verbose)
            if result == BehaviourTreeNode.SUCCESS:
                self.log(f"SUCCESS")
                return result
            elif result == BehaviourTreeNode.RUNNING:
                self.log(f"RUNNING")
                return result
        self.log(f"FAILURE")
        return BehaviourTreeNode.FAILURE
    
    def __str__(self, prefix=''):
        """
        Returns a string representation of the FallbackNode.

        Args:
            prefix (str): Prefix for log messages (default '').
        
        Returns:
            tree (rich.Tree): Tree representation of the FallbackNode.
        """
        tree = Tree(f"{prefix}[bold green]Fallback [/]{self.name}", guide_style="bold blue")
        child_prefix = prefix
        for child in self.children:
            tree.add(child.__str__(child_prefix))
        return tree


class ActionNode(BehaviourTreeNode):

    def __init__(self, name, callback):
        """
        Initializes an ActionNode object.

        Args:
            name (str): The name of the node.
            callback (function): The callback function to be executed.
        """
        super().__init__(name,"Action")
        self.callback = callback

    def tick(self, prefix='', verbose=False) -> int:
        """
        Performs the tick operation on the ActionNode by running the defined callback function.
        The node will return SUCCESS if the callback function returns True,
        and FAILURE if it returns False.

        Args:
            prefix (str): Prefix for log messages (default '').
            verbose (bool): Whether to enable verbose logging (default False).

        Returns:
            int: Result of the tick operation.
            SUCCESS: If the callback function returns True.
            FAILURE: If the callback function returns False.
        """
        self.log(f"STARTED")
        success = self.callback()
        if success:
            self.log(f"SUCCESS")
            return BehaviourTreeNode.SUCCESS
        else:
            self.log(f"FAILURE")
            return BehaviourTreeNode.FAILURE
    
    def __str__(self, prefix=''):
        """
        Returns a tree representation of the ActionNode.

        Args:
            prefix (str): Prefix for log messages (default '').

        Returns:
            tree (rich.Tree): Tree representation of the ActionNode.
        """
        return Tree(f"{prefix}[bold purple]Action [/]{self.name}", guide_style="bold blue")


class ConditionNode(BehaviourTreeNode):

    def __init__(self, name, callback):
        """
        Initializes a ConditionNode object.

        Args:
            name (str): The name of the node.
            callback (function): The callback function to be executed.
        """
        super().__init__(name,"Condition")
        self.callback = callback
        self.node_type = "Condition"

    def tick(self, prefix='', verbose=False) -> int:
        """
        Performs the tick operation on the ConditionNode by running the defined callback function.
        The node will return SUCCESS if the callback function returns True,
        and FAILURE if it returns False.

        Args:
            prefix (str): Prefix for log messages (default '').
            verbose (bool): Whether to enable verbose logging (default False).

        Returns:
            int: Result of the tick operation.
            SUCCESS: If the callback function returns True.
            FAILURE: If the callback function returns False.
        """
        self.log(f"STARTED")
        success = self.callback()
        if success:
            self.log(f"SUCCESS")
            return BehaviourTreeNode.SUCCESS
        else:
            self.log(f"FAILURE")
            return BehaviourTreeNode.FAILURE

    def __str__(self, prefix=''):
        """
        Returns a tree representation of the ConditionNode.

        Args:
            prefix (str): Prefix for log messages (default '').
            verbose (bool): Whether to enable verbose logging (default False).

        Returns:
            tree (rich.Tree): Tree representation of the ConditionNode.
        """
        return Tree(f"{prefix}[bold blue]Condition [/]{self.name}", guide_style="bold blue")


if __name__ == '__main__':
    action1 = ActionNode("Action1", lambda: True)
    action2 = ActionNode("Action2", lambda: False)
    action3 = ActionNode("Action3", lambda: True)
    condition1 = ConditionNode("Condition1", lambda: True)
    condition2 = ConditionNode("Condition2", lambda: False)

    seq1 = SequenceNode("Seq1", [action1, action2])
    seq2 = SequenceNode("Seq2", [condition1, action3])
    root = FallbackNode("Root", [seq1, seq2])

    print(root.__str__())
