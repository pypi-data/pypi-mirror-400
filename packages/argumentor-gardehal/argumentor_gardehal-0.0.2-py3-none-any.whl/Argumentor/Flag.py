import re

class Flag():
    name: str
    alias: list[str]
    value: object
    defaultValue: object
    description: str

    def __init__(self, name: str, 
        alias: list[str],
        value: object,
        defaultValue: object = None,
        description: str = None):
        """
        Designates values input as a flag after commands. These are always optional and only return a static value.
        eg. update_external in 
        $ -dimensions height:100 --update_external

        Args:
            name (str): Name of argument, key for dictionary in Return.
            alias (list[str]): Alias of argument.
            value (object): The value to use if flag is present in input.
            defaultValue (object, optional): The value to use if flag is NOT present in input. Defaults to None.
            description (str, optional): Explaining what the argument is for. Defaults to None.
        """
        
        invalidCharactersRegex = r"\W"
        invalidNames = [e for e in alias + [name] if (re.search(invalidCharactersRegex, e))]
        if(invalidNames):
            raise AttributeError(f"Flag \"{name}\" name or alias ({invalidNames}) contain invalid characters, must be alphanumeric.")
        
        self.name = name
        self.alias = alias
        self.value = value
        self.defaultValue = defaultValue
        self.description = description
                
    def getFormattedDescription(self) -> str:
        """
        Get the description of flags with formatting.

        Returns:
            str: String description.
        """
        
        aliasDisplayString = f"alias: {", ".join(self.alias)}" if self.alias else ""
        return f"* Flag {self.name} ({aliasDisplayString}): \
            \n\t{self.description}"