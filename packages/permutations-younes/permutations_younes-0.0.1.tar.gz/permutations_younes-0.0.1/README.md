# Permutations Generator

A Python utility to generate all permutations of a list of elements using Heap's algorithm.

## Overview

This script generates all possible permutations of a given list of elements. It uses Heap's algorithm, an efficient recursive approach that generates permutations by swapping elements in a systematic manner.

## Usage

Run the script from the command line with a list of elements to permute:

```bash
python permutations.py element1 element2 element3 ...
```

### Example

```bash
python permutations.py 1 2 3
```

Output:
```
['1', '2', '3']
---------------------------------------
1 2 3 
1 3 2 
2 1 3 
2 3 1 
3 1 2 
3 2 1 
```

## Requirements

- Python 3.6 or higher

## Notes

- Elements are treated as strings when passed via command line
- The total number of permutations for n elements is n! (factorial)
- For large input lists (n > 10), execution time and memory usage will increase significantly

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/procrastinator-101/permutations/blob/main/LICENSE) file for more details.