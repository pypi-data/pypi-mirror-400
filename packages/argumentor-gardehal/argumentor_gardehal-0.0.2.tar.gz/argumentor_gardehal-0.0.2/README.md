# Argumentor

Command and argument parsing and documentation for Python CLI.

> [!WARNING]  
> This project is not really meant for widespread application and was mostly made for fun. Use at your own risk.

<sub><sup>Feel free to contribute if you find any issues though.</sup></sub>

## Install

[PyPi project](https://pypi.org/project/argumentor-gardehal/)

Install using pip
- $ `pip install argumentor-gardehal`

Install from files locally
- $ `cd [path to this folder]`
- $ `pip cache purge` (may help if old packages are cached)
- $ `pip install .`

## Example

#### Getting started

Creating a command to calculate volume for a given object we have stored somewhere with an ID.
[ExampleBasic.py](https://github.com/gardehal/argumentor/tests/ExampleBasic.py)
- $ `python .\tests\ExampleBasic.py -help`

#### A step further

Creating a command that takes multiple inputs, validating dimensions, and a optional argument with custom casting and validation from string to an enum.
[ExampleAdvanced.py](https://github.com/gardehal/argumentor/tests/ExampleAdvanced.py)
- $ `python .\tests\ExampleAdvanced.py -help`

##### Expected outcomes

The following list of examples explains some expected outcomes, or could be used to test Argumentor. Note: These are based on [ExampleAdvanced.py](https://github.com/gardehal/argumentor/tests/ExampleAdvanced.py).

    # Note, depending on CLI, these results may vary compared to validateString version as below, or as input into CLI (using ' or " would be a main reason as CLI reads it differently)

    inputA = "-dim 1 2 3" # Valid
    inputB = "-d a b c" # Invalid, a b c cannot be cast to ints unless you create a custom cast function
    inputC = "-d width:4 d:5 h:6" # Valid
    inputD = "-d w:7 8 d:9" # Valid, note the order: width, then unnamed argument which will be resolved to height because width and depth are named with an alias, then depth
    inputE = "-d w:10 11 12" # Valid
    inputF = "-d w:13 d:'-14' h:-15" # Invalid, validateInt function does not allow negative values (-14), and arguments (h:-15) starting with the command prefix (default "-") must be a named alias with quotation marks
    inputG = "-d w:16 d:':17' h::18" # Invalid, the default int casting (':17') will fail, and arguments with colon ":" (h::18) must be a named alias or in quotation marks
    inputH = "-test 19 20 21" # Invalid, command "test" does not exist and nothing will be returned from validate
    inputI = "-d 22 24 25 --updateexternal" # Valid, flag --updateexternal will return a static value
    inputJ = "-d 26 27 28 --nosuchflag" # Valid, but flag does not exist and reports this through Result.messages
    
    # Input as string
    argResults = argumentor.validateString(inputA)

## Recommendations

1. Use a more complete argument parser
1. See [ExampleBasic.py](https://github.com/gardehal/argumentor/tests/ExampleBasic.py) and [ExampleAdvanced.py](https://github.com/gardehal/argumentor/tests/ExampleAdvanced.py) for examples of usage.
1. Argumentor().validate() returns a list of Result with detected commands. Parse the result with this in mind:
    1. If the list is empty, no command-like input was detected.
    1. When populated, each Result will specify what command was hit by name and have a hitValue that was specified on init.
    1. If a command is detected but has errors, isValid will be false, and messages will details.
    1. Valid commands will have a dict of cast arguments ready to use.
1. Document your Commands, Arguments, and Flags using descriptions, provide a command (HELP/MAN) for users to see this. Access a printable description of commands through Argumentor().getFormattedDescription().
1. Arguments have fields for custom casting and validation functions (castFunc, validateFunc), the usage and limitations of these should be documented in descriptions.
1. Use arguments defaultValue and useDefaultValue to set a default or fallback in case casting or validating input from user fails. In some cases, a validation function is needed for applying default.
1. Static values can be set using a Flag, if the flag is present in input, the value set in Flag init will be in Result.arguments

## TODO

- guaranteed that multiple things can be improved in validate, both efficacy and readability