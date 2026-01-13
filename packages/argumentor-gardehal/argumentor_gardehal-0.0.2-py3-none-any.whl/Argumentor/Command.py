import re

from .Argument import Argument
from .Flag import Flag

class Command():
    name: str
    hitValue: object
    alias: list[str]
    arguments: list[Argument]
    flags: list[Flag]
    description: str
    
    def __init__(self, name: str,
        alias: list[str],
        hitValue: object,
        arguments: list[Argument] = [],
        flags: list[Flag] = [],
        description: str = None):
        """
        Designates commands
        eg. dimensions in 
        $ -dimensions value:100

        Args:
            name (str): Name of command
            alias (list[str]): Alias of command.
            hitValue (object): Value to return in Result when this command is found in input
            arguments (list[Argument], optional): Arguments to be cast and validated, then returned in Result. Defaults to [].
            flags (list[Flag], optional): Flags which when present returns a static value. Defaults to [].
            description (str, optional): Explaining what the command does. Defaults to None.
        """

        invalidCharactersRegex = r"\W"
        invalidNames = [e for e in alias + [name] if (re.search(invalidCharactersRegex, e))]
        if(invalidNames):
            raise AttributeError(f"Command \"{name}\" name or alias ({invalidNames}) contain invalid characters, must be alphanumeric.")
        
        self.name = name
        self.alias = alias
        self.hitValue = hitValue
        self.arguments = arguments
        self.flags = flags
        self.description = description
        
    def getFormattedDescription(self) -> str:
        """
        Get the description of command and arguments combined with formatting.

        Returns:
            str: String description.
        """
        
        argumentDescriptions = "\n".join([e.getFormattedDescription() for e in self.arguments]) 
        argumentsDisplayString = f"\n{argumentDescriptions}" if self.arguments else ""
        flagDescriptions = "\n".join([e.getFormattedDescription() for e in self.flags]) 
        flagDisplayString = f"\n{flagDescriptions}" if self.flags else ""
        
        requiredArgumentsDisplayString = f"{len([e for e in self.arguments if not e.optional])} required arguments"
        aliasDisplayString = f", alias: {", ".join(self.alias)}" if self.alias else ""
        return f"\nCommand {self.name} ({requiredArgumentsDisplayString}{aliasDisplayString}) \
            \n\t{self.description} \
            {argumentsDisplayString} \
            {flagDisplayString}"
    
    