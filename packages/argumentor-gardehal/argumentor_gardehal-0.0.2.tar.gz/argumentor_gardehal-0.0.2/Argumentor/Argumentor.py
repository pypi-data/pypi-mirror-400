from .Result import Result
from .Command import Command
from .ArgumentValidation import ArgumentValidation

import re

class Argumentor():
    commands: list[Command]
    commandPrefix: str
    namedArgDelim: str
    flagPrefix: str
    inputDelim: str
    
    def __init__(self, commands: list[Command],
        commandPrefix: str = "-",
        namedArgDelim: str = ":",
        flagPrefix: str = "--",
        inputDelim: str = " ",
        nameDuplicateCheck: bool = True):
        """
        Holder of all commands and arguments, base for validation of input.

        Args:
            commands (list[Command]): Commands to search for in input.
            commandPrefix (str, optional): Prefix expected to be in front of Commands only. Defaults to "-".
            namedArgDelim (str, optional): Deliminator for named arguments, e.g. "width:10". Defaults to ":".
            flagPrefix (str, optional): Prefix for flags, e.g. "--updateexternal". Defaults to "--".
            inputDelim (str, optional): Deliminator for input, only used for validateString. Defaults to " ".
            nameDuplicateCheck (bool, optional): Enable checks on command, argument, flag name/alias duplicates. Defaults to True.
        """

        self.commands = commands
        self.commandPrefix = commandPrefix
        self.namedArgDelim = namedArgDelim
        self.flagPrefix = flagPrefix
        self.inputDelim = inputDelim

        # Check for duplicates,
        # two different command cannot have the same names or alias,
        # a command cannot have two arguments with the same names or alias
        if(nameDuplicateCheck):
            argumentorList = [self.commandPrefix, self.namedArgDelim, self.flagPrefix, self.inputDelim]
            argumentorDuplicates = [e for e in argumentorList if argumentorList.count(e) > 1]
            if(argumentorDuplicates):
                raise AttributeError(f"Duplicate prefixes or delims ({argumentorDuplicates}) found in Argumentor")

            commandList = []
            for command in self.commands:
                argumentList = [e for f in command.arguments for e in (f.alias + [f.name])]
                argumentDuplicates = [e for e in argumentList if argumentList.count(e) > 1]
                if(argumentDuplicates):
                    raise AttributeError(f"Duplicate arguments ({argumentDuplicates}) found in {command.name}")
                
                flagList = [e for f in command.flags for e in (f.alias + [f.name])]
                flagDuplicates = [e for e in flagList if flagList.count(e) > 1]
                if(flagDuplicates):
                    raise AttributeError(f"Duplicate flags ({flagDuplicates}) found in {command.name}")

                commandList.append(command.name)
                commandList.extend(command.alias)

            commandDuplicates = [e for e in commandList if commandList.count(e) > 1]
            if(commandDuplicates):
                raise AttributeError(f"Duplicate commands ({commandDuplicates}) found")

    def getSyntaxDescription(self) -> str:
        """
        Get the description of syntax for calling commands.

        Returns:
            str: String description.
        """
        
        return f"""\
Commands must be prefixed with \"{self.commandPrefix}\"
Arguments can be either positional or prefixed with the argument name using \"{self.namedArgDelim}\"
Flags must be prefixed with \"{self.flagPrefix}\"
All input must be parted with \"{self.inputDelim}\"
Example: {self.commandPrefix}command{self.inputDelim}positionalArgument{self.inputDelim}argumentName{self.namedArgDelim}argumentValue{self.inputDelim}{self.flagPrefix}flag
            """

    def getFormattedDescription(self) -> str:
        """
        Get the description of commands and arguments combined with formatting.

        Returns:
            str: String description.
        """
        
        return "\n".join([e.getFormattedDescription() for e in self.commands])
    
    def validateString(self, input: str) -> list[Result]:
        """
        Validate input and return list of ArgResults found, with arguments, if any are found.
        Commands and related arguments not in commands list will not be parsed.

        Args:
            input (str): Input as a single string.

        Returns:
            list[Result]: List of results of commands hit, with corresponding cast and validated arguments.
        """
        
        return self.validate(input.split(self.inputDelim))
        
    def validate(self, input: list[str]) -> list[Result]:
        """
        Validate input and return list of ArgResults found, with arguments, if any are found.
        Commands and related arguments not in commands list will not be parsed.

        Args:
            input (list[str]): Input as list of string.

        Returns:
            list[Result]: List of results of commands hit, with corresponding cast and validated arguments.
        """
        
        if(len(input) == 0):
            return []
        
        result = []
        nextInputs = []
        for command in self.commands:
            prefixedCommandAlias = [f"{self.commandPrefix}{e}" for e in command.alias]
            for commandAlias in prefixedCommandAlias:
                if(commandAlias not in input):
                    continue
                
                commandIndex = input.index(commandAlias)
                potentialArgs = input[commandIndex + 1:]
                argsEndIndex = self.__getLastArgumentIndex(potentialArgs)
                nextInputs = potentialArgs[argsEndIndex:]
                
                args = potentialArgs[:argsEndIndex]
                validation = ArgumentValidation(args, command, self.namedArgDelim, self.flagPrefix)
                
                argResult = Result(validation.isValid, command.name, command.hitValue, commandIndex, validation.finalizedArguments, validation.messages)
                result.append(argResult)
        
        if(nextInputs):
            result.extend(self.validate(nextInputs))
    
        return result
    
    def __getLastArgumentIndex(self, potentialArgs: list[str]) -> int:
        commandRegex = fr"^{self.commandPrefix}\w"
        for potentialArg in potentialArgs:
            if(re.search(commandRegex, potentialArg)):
                return (potentialArgs.index(potentialArg))
            
        # None found, default to end of list
        return len(potentialArgs)
    