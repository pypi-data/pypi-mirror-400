
class Result():
    isValid: bool
    commandName: str
    commandHitValue: object
    commandIndex: int
    arguments: dict[str, object]
    messages: list[str]
    
    def __init__(self, isValid: bool, 
                 commandName: str, 
                 commandHitValue: object, 
                 commandIndex: int, 
                 arguments: dict[str, object], 
                 messages: list[str]):
        """
        Result of validate, with info of what command was hit, what values was added, where it was in the input string, what to parse next for the caller
        
        Args:
            isValid (bool): Command and arguments are valid
            commandName (str): Name of command
            commandHitValue (object): Hit value supplied in Command init
            commandIndex (int): Index of command in input
            arguments (dict[str, object]): Dict of arguments, key being the name supplied to Argument init, the value being cast and validated to typeT
            messages (list[str]): List of error messages, if any. Always populated when isValid = False, may contain messages when defaults are applied if casting and validating arguments failed
        """

        self.isValid = isValid
        self.commandName = commandName
        self.commandHitValue = commandHitValue
        self.commandIndex = commandIndex
        self.arguments = arguments
        self.messages = messages
        
    def toString(self) -> str:
        """
        Returns string with class properties.

        Returns: 
            str: String of class properties.
        """
        
        return f""" \
            isValid: {self.isValid},
            commandName: {self.commandName},
            commandHitValue: {self.commandHitValue},
            commandIndex: {self.commandIndex},
            arguments: {self.arguments},
            messages: {self.messages},
            """

    def getFormattedMessages(self) -> str:
        """
        Get detail messages formatted in a printable way.

        Returns: 
            str: String errors.
        """
        
        return "\n".join([f"* {e}" for e in self.messages])