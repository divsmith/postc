# PostC Language Reference

This document provides a comprehensive reference for the PostC programming language, including all data types, operators, functions, and syntax elements.

## Table of Contents

- [Data Types](#data-types)
- [Syntax Elements](#syntax-elements)
- [Operators](#operators)
- [Stack Manipulation](#stack-manipulation)
- [Variables and Functions](#variables-and-functions)
- [Control Structures](#control-structures)
- [Array Operations](#array-operations)
- [Dictionary Operations](#dictionary-operations)
- [String Operations](#string-operations)
- [File I/O Operations](#file-io-operations)
- [Standard Library](#standard-library)

## Data Types

PostC supports the following data types:

### Primitive Types

1. **Integers** - Signed whole numbers
   - Examples: `123`, `-456`, `0`
   - Range: Platform-dependent (typically 64-bit)

2. **Floats** - IEEE 754 double-precision floating-point numbers
   - Examples: `3.14`, `-2.5e10`, `1.23e-4`
   - Special values: Infinity, NaN

3. **Strings** - Sequences of characters enclosed in double quotes
   - Examples: `"hello"`, `"world"`, `""` (empty string)
   - Escape sequences: `\"` (quote), `\\` (backslash), `\n` (newline)

4. **Booleans** - Logical values
   - Values: `true`, `false`

### Composite Types

5. **Arrays** - Dynamic arrays that can store multiple values of any type
   - Created with: `size create_array`
   - Access with: `index load_array`, `value index store_array`
   - Get length with: `array_length`

6. **Dictionaries** - Key-value data structures for associative storage
   - Created with: `create_dict`
   - Access with: `key load_dict`, `key value store_dict`
   - Check membership: `key dict_has_key`
   - Get size with: `dict_length`

## Syntax Elements

### Literals

- **Integer literals**: `123`, `-456`
- **Float literals**: `3.14`, `-2.5e10`
- **String literals**: `"hello world"`
- **Boolean literals**: `true`, `false`

### Identifiers

- Variable and function names must start with a letter or underscore
- Can contain letters, digits, and underscores
- Case-sensitive

### Comments

- Single-line comments start with `#` and continue to end of line
- Example: `# This is a comment`

## Operators

### Arithmetic Operators

| Operator | Description | Example | Stack Effect |
|----------|-------------|---------|--------------|
| `+` | Addition | `3 4 +` | `(a b -- sum)` |
| `-` | Subtraction | `5 3 -` | `(a b -- diff)` |
| `*` | Multiplication | `6 7 *` | `(a b -- prod)` |
| `/` | Division | `15 3 /` | `(a b -- quot)` |

### Comparison Operators

| Operator | Description | Example | Stack Effect |
|----------|-------------|---------|--------------|
| `==` | Equality | `5 5 ==` | `(a b -- bool)` |
| `!=` | Inequality | `3 4 !=` | `(a b -- bool)` |
| `<` | Less than | `2 8 <` | `(a b -- bool)` |
| `>` | Greater than | `5 3 >` | `(a b -- bool)` |
| `<=` | Less or equal | `4 4 <=` | `(a b -- bool)` |
| `>=` | Greater or equal | `6 5 >=` | `(a b -- bool)` |

### Logical Operators

| Operator | Description | Example | Stack Effect |
|----------|-------------|---------|--------------|
| `and` | Logical AND | `true false and` | `(a b -- bool)` |
| `or` | Logical OR | `true false or` | `(a b -- bool)` |
| `not` | Logical NOT | `false not` | `(a -- bool)` |

## Stack Manipulation

PostC uses a stack-based execution model with explicit stack manipulation operators:

| Operator | Description | Stack Effect |
|----------|-------------|--------------|
| `dup` | Duplicate top element | `(a -- a a)` |
| `drop` | Remove top element | `(a -- )` |
| `swap` | Swap top two elements | `(a b -- b a)` |
| `over` | Copy second element to top | `(a b -- a b a)` |
| `rot` | Rotate top three elements | `(a b c -- b c a)` |

## Variables and Functions

### Variable Declarations

- **Immutable variables**: `let name value`
- **Mutable variables**: `var name value`

Example:
```
42 let answer
17 var counter
```

### Function Definitions

Functions are defined using RPN syntax:

```
:function_name param_count param
  # function body using RPN
;
```

Example:
```
:add 2 param
  +
;

:square 1 param
  dup *
;
```

### Function Calls

Functions are called by pushing arguments then invoking the function:

```
5 3 add    # Calls add function with arguments 5 and 3
10 square  # Calls square function with argument 10
```

## Control Structures

### Conditional Statements

```
condition if
  # true branch
else
  # false branch
;
```

Example:
```
x 0 > if
  "positive" print
else
  "non-positive" print
;
```

### Loops

#### While Loop
```
condition while
  # loop body
;
```

Example:
```
10 var i
i 0 > while
  i print
  i 1 - var i
;
```

#### For Loop (Countdown)
```
count for
  # loop body
;
```

Example:
```
5 for
  "countdown: " print
  dup print
;
```

## Array Operations

Arrays are dynamic data structures that can store multiple values:

### Creating Arrays
```
size create_array  # Creates array with given size
```

### Array Access
```
index load_array   # Load value at index
value index store_array  # Store value at index
```

### Array Information
```
array_length       # Get array length
```

### Example Usage
```
# Create array of size 3
3 create_array

# Store values
42 0 store_array
17 1 store_array
99 2 store_array

# Load and use values
0 load_array print  # Prints: 42
1 load_array print  # Prints: 17
2 load_array print  # Prints: 99

# Get length
array_length print  # Prints: 3
```

## Dictionary Operations

Dictionaries store key-value pairs and allow fast lookups by key:

### Creating Dictionaries
```
create_dict        # Creates empty dictionary
```

### Dictionary Operations
```
key value store_dict    # Store key-value pair
key load_dict          # Load value for key
key dict_has_key       # Check if key exists
dict_length           # Get dictionary size
```

### Example Usage
```
# Create dictionary
create_dict

# Store key-value pairs
"name" "PostC" store_dict
"version" "1.0" store_dict
"complete" "true" store_dict

# Load values
"name" load_dict print        # Prints: PostC
"version" load_dict print     # Prints: 1.0

# Check key existence
"turing_complete" dict_has_key print  # Prints: false
"name" dict_has_key print              # Prints: true

# Get size
dict_length print             # Prints: 3
```

## String Operations

PostC provides comprehensive string manipulation functions:

### String Creation
Strings are created using double quotes:
```
"hello world"
```

### String Functions
```
string1 string2 string_concat     # Concatenate strings
string string_length             # Get string length
string start length string_substring  # Extract substring
string substring string_indexof  # Find substring index
```

### Example Usage
```
# Concatenation
"Hello " "World!" string_concat print  # Prints: Hello World!

# Length
"Hello World!" string_length print     # Prints: 13

# Substring
"Hello World!" 6 5 string_substring print  # Prints: World

# Find index
"Hello World!" "World" string_indexof print  # Prints: 6
```

## File I/O Operations

PostC supports file input/output operations:

### Reading Files
```
filename read_file    # Read entire file contents
```

### Standard Input
```
read_stdin           # Read from standard input
```

### Example Usage
```
# Read file
"README.md" read_file print

# Read user input
"Enter your name: " print
read_stdin print
```

## Standard Library

The standard library provides commonly used functions organized by category:

### Arithmetic Functions
- `add`, `sub`, `mul`, `div` - Basic arithmetic
- `square`, `cube` - Power operations
- `abs` - Absolute value
- `max`, `min` - Comparison operations

### Comparison Functions
- `eq`, `ne`, `lt`, `gt`, `le`, `ge` - All comparison operations

### Stack Operations
- `dup`, `drop`, `swap`, `over`, `rot` - Stack manipulation

### Boolean Logic
- `not`, `and`, `or` - Logical operations

### Control Flow Helpers
- `if_else` - Conditional execution helper
- `while_do` - Loop helper

### Utility Functions
- `identity` - Return input unchanged
- `const` - Return constant value
- `apply` - Apply function to argument

### I/O Functions
- `print` - Output to stdout
- `read_file` - File input
- `read_stdin` - Standard input

## Error Handling

PostC provides basic error handling through stack underflow detection and type checking. More sophisticated error handling and reporting is planned for future versions.

## Examples

See the `examples/` directory for comprehensive example programs demonstrating all PostC features, including:
- Basic arithmetic and control flow
- Array and dictionary operations
- String manipulation
- File I/O operations
- Turing complete program examples