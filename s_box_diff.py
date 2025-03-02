# Generate S_Box table for DES encryption
from custom_DES import WEAK_S_BOXES, permute, P, E

# Generate table for ith S_Box
def generate_s_box_table(i, file_name=None):
    """
    This function generates a table for the ith S_Box.
    i:          The index of the S_Box (0 to 7)
    file_name:  The name of the file to write the table to
    """

    # Get S_BOX
    s_box = WEAK_S_BOXES[i]

    # Generate table of zeroes (64 rows, 16 columns)
    table = [[0 for x in range(16)] for y in range(64)]

    # Iterate from 0 to 63 twice:
    for i in range(64):
        for j in range(64):
            # Input XOR
            input_xor = i ^ j

            # Get row and column for i and j
            row_i = (i & 0b100000) >> 4 | (i & 0b1)
            col_i = (i & 0b011110) >> 1
            row_j = (j & 0b100000) >> 4 | (j & 0b1)
            col_j = (j & 0b011110) >> 1

            # Get output XOR
            output_xor = s_box[row_i][col_i] ^ s_box[row_j][col_j]

            # Increment table at row = input_xor, col = output_xor
            table[input_xor][output_xor] += 1

    # Write table to file
    if file_name:
        with open(file_name, 'w') as f:
            # Each cell has a fill of 5
            # Columns
            f.write(''.rjust(5))
            for i in range(16):
                f.write(str(i).rjust(5))
            f.write('\n')
            
            # Rows
            i = 0
            for row in table:
                f.write(str(i).rjust(5))
                for cell in row:
                    f.write(str(cell).rjust(5))
                f.write('\n')
                i += 1

    return table

# Generate all S_Box tables
def generate_all_s_box_tables():
    """
    This function generates all S_Box tables and returns them in a list.
    It also write the tables to ./tables/s_box_table_i.txt where i is 
    the S_Box number.
    """
    tables = []
    for i in range(8):
        table = generate_s_box_table(i, './tables/s_box_table_{}.txt'.format(i+1))
        tables.append(table)
    return tables

# Reconstruction of input from good differential
def reconstruct_input(input_xor_pos, s_box_num):
    """ 
    This function reconstructs the input from a good differential.
    input_xor_pos:  Position of the one-bit in the 
                    input XOR (starting from 0)
    s_box_num:      Index of the S_Box (starting from 0)
    """
    main_pos = (5 + 4*s_box_num) - input_xor_pos
    if main_pos < 0:
        main_pos += 32
    if main_pos >= 32:
        main_pos -= 32
    # Convert to 32-bit string
    main_str = format(1<<(32-main_pos), '032b')
    return main_str

# Reconstruction of output from good differential
def reconstruct_output(output_xor_pos, s_box_num):
    """
    This function reconstructs the output from a good differential.
    output_xor_pos: Position of the one-bit in the
                    output XOR (starting from 0)
    s_box_num:      Index of the S_Box (starting from 0)
    """
    # Final position (from left)
    final_pos = 4*s_box_num + (4-output_xor_pos)
    # Convert above number to a 32-bit string
    final_str = format(1<<(32-final_pos), '032b')
    print(final_str)
    # Permute
    final_str = permute(final_str, P)
    # Concatenate each entry in final_str
    final_str = ''.join(final_str)
    return final_str

# Main (Get good differentials)
if __name__ == '__main__':
    # Generate all S_Box tables
    tables = generate_all_s_box_tables()

    # Masks for inputs and output
    inputs = [1<<i for i in range(6)]
    outputs_1 = [1<<i for i in range(4)]
    outputs_2 = [0]
    outputs = outputs_1 + outputs_2

    # Threshold for good differentials
    thres = 16

    # Print info
    print("""The program computes the subtables for one-bit output differences and zero output differences from single-bit input differences for each S-Box. We only track differentials with greater than 0.25 probability.\n""") 

    # Iterate thru tables
    for i in range(8):
        # Extract subtable as per mask
        subtable = [[tables[i][j][k] for k in outputs] for j in inputs]
        subtable_1 = [[tables[i][j][k] for k in outputs_1] for j in inputs]
        subtable_2 = [[tables[i][j][k] for k in outputs_2] for j in inputs]

     

        # Print subtable with row and column headers
        print('S_Box {}:'.format(i+1))
        print(''.rjust(5), end='')
        for output in outputs:
            print(str(output).rjust(5), end='')
        print()
        for j in range(6):
            print(str(1<<j).rjust(5), end='')
            for k in range(5):
                print(str(subtable[j][k]).rjust(5), end='')
            print()

        # Analyze subtable
        print('--------------------------------- 1 -> 1 ---------------------------------')
        for j in range(6):
            for k in range(4):
                if subtable_1[j][k] >= thres:
                    print('Good differential: Input = {}, Output = {}, #Pairs = {}'.format(1<<j, 1<<k, subtable_1[j][k]))
                    print('Reconstructed input: ', reconstruct_input(j, i))
                    print('Reconstructed output: ', reconstruct_output(k, i))
                    print('Expanded input: ', ''.join(permute(reconstruct_input(j, i), E)))
                    print()

        # Analyze subtable (better)
        print('\n--------------------------------- 1 -> 0 ---------------------------------')
        for j in range(6):
            if subtable_2[j][0] >= thres:
                print('Good differential: Input = {}, Output = {}, #Pairs = {}'.format(1<<j, 0, subtable_2[j][0]))
                print('Reconstructed input: ', reconstruct_input(j, i))
                print('Expanded input: ', ''.join(permute(reconstruct_input(j, i), E)))
                print()

        print('--------------------------------------------------------------------------')
