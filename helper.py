# Helper functions for 6-Round DES Cryptanalysis
# Import matrices
from matrices import *

# Apply a matrix (a permutation)
def apply_matrix(matrix, input):
    # Apply the matrix to the input
    output = [input[i - 1] for i in matrix]
    return ''.join(output)

def apply_matrix_list(matrix, input):
    # Apply the matrix to the input
    output = [input[i - 1] for i in matrix]
    return output

# XOR function for two binary strings
def xor(a, b):
    # Compute the bitwise XOR of the two binary strings
    c = int(a, 2) ^ int(b, 2)
    # Convert the result back to a binary string
    c = bin(c)[2:].zfill(len(a))
    return c

# S-Box function
def s_box(i, input):
    # Assert that i is [0, 7]
    assert i >= 0 and i < 8, "Invalid S-Box index"
    assert len(input) == 6, "Invalid input length"

    # Get the row and column from the input
    row = int(input[0] + input[5], 2)
    col = int(input[1:5], 2)
    # Get the value from the S-Box
    value = WEAK_S_BOXES[i][row][col]
    # Convert the value to a binary string
    value = bin(value)[2:].zfill(4)
    return value

# Extract the input to the ith S-Box
def extract_input(i, input):
    # Assert that i is [0, 7]
    assert i >= 0 and i < 8, "Invalid S-Box index"
    assert len(input) == 48, "Invalid input length"

    # Get the input to the S-Box
    input = input[6 * i:6 * (i + 1)]
    return input

# Extract the output from the ith S-Box
def extract_output(i, output):
    # Assert that i is [0, 7]
    assert i >= 0 and i < 8, "Invalid S-Box index"
    assert len(output) == 32, "Invalid output length"

    # Get the output from the S-Box
    output = output[4 * i:4 * (i + 1)]
    return output

# Get left half
def get_left_half(input):
    # Assert that the input is of length 64
    assert len(input) == 64, "Invalid input length"
    return input[:32]

# Get right half
def get_right_half(input):
    # Assert that the input is of length 64
    assert len(input) == 64, "Invalid input length"
    return input[32:]

# Get a binary string as hexadecimal
def get_hex(input):
    # Convert the input to hexadecimal
    hex_output = hex(int(input, 2))[2:].zfill(16)
    return hex_output

# Get key schedule as a matrix of indices for 6 rounds
def key_schedule():
    main_key = [i for i in range(1, 65)]

    # Apply the PC-1 matrix
    key = apply_matrix_list(PC1, main_key)

    # Split the key into two halves
    left = key[:28]
    right = key[28:]

    # Subkeys
    subkeys = []
    for shift in SHIFTS:
        # Shift the halves
        left = left[shift:] + left[:shift]
        right = right[shift:] + right[:shift]
        # Merge the halves
        key = left + right
        # Apply the PC-2 matrix
        subkey = apply_matrix_list(PC2, key)
        subkeys.append(subkey)
    return subkeys

# Get parity of a binary string
def get_parity(input):
    parity = 0
    for i in input:
        parity ^= int(i)
    return parity
