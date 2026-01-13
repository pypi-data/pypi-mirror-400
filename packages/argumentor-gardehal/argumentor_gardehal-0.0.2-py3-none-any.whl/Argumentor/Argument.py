import re

from typing import TypeVar, Type, Callable

T = TypeVar("T")

class Argument():
    name: str
    alias: list[str]
    typeT: Type[T]
    optional: bool
    castFunc: Callable[[str], T]
    validateFunc: Callable[[T], bool]
    useDefaultValue: bool
    defaultValue: T
    description: str
    
    def __init__(self, name: str, 
        alias: list[str],
        typeT: Type[T], 
        optional: bool = False, 
        castFunc: Callable[[str], T] = None, 
        validateFunc: Callable[[T], bool] = None, 
        useDefaultValue: bool = False, 
        defaultValue: T = None, 
        description: str = None):
        """
        Designates values input as arguments after commands 
        eg. height in 
        $ -dimensions height:100

        Args:
            name (str): Name of argument, key for dictionary in Return
            alias (list[str]): Alias of argument.
            typeT (Type[T]): Type of argument, str, int, bool, enum, etc.
            optional (bool, optional): Argument is optional/nullable (from input). Defaults to False. Note that this implies the argument can be None in result, unless useDefaultValue and defaultValue are both set.
            castFunc (Callable[[str], T], optional): Optional function for custom casting of input to typeT. Must take in 1 argument: str and return typeT. Defaults to None.
            validateFunc (Callable[[T], bool], optional): Optional function for custom validation. Must take in 1 argument: typeT and return bool. Defaults to None.
            useDefaultValue (bool, optional): Use a default value if casting and validation fails. Defaults to False.
            defaultValue (T, optional): The default value to use if casting and validation fails, and useDefaultValue is True. Must be typeT. Defaults to None.
            description (str, optional): Explaining what the argument is for. Defaults to None.
        """
        
        invalidCharactersRegex = r"\W"
        invalidNames = [e for e in alias + [name] if (re.search(invalidCharactersRegex, e))]
        if(invalidNames):
            raise AttributeError(f"Argument \"{name}\" name or alias ({invalidNames}) contain invalid characters, must be alphanumeric.")
        
        self.name = name
        self.alias = alias
        self.typeT = typeT
        self.optional = optional
        self.castFunc = castFunc
        self.validateFunc = validateFunc
        self.useDefaultValue = useDefaultValue
        self.defaultValue = defaultValue
        self.description = description
                
    def getFormattedDescription(self) -> str:
        """
        Get the description of arguments with formatting.

        Returns:
            str: String description.
        """
        
        optionalDisplayString = "optional" if self.optional else "required"
        typeDisplayString = f", type: {self.typeT.__name__}"
        aliasDisplayString = f", alias: {", ".join(self.alias)}" if self.alias else ""
        defaultDisplayString = f", default: {str(self.defaultValue)}" if self.useDefaultValue else ""
        return f"* Argument {self.name} ({optionalDisplayString}{typeDisplayString}{defaultDisplayString}{aliasDisplayString}): \
            \n\t{self.description}"