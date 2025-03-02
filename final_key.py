# Import stuff
from helper import *
from oracle import *
from custom_DES import des_decrypt
import random
import tqdm
import time

random.seed(42)

# Constants
CHAR_L = f"{0x00000400:032b}"
CHAR_R = f"{0x00000020:032b}"
CHAR = CHAR_L + CHAR_R
NUM_PAIRS = 85
NUM_FINAL = 5
S_BOX_INDICES = [0, 1, 2, 3, 4, 6, 7]

def max_clique(graph: list[list[int]], candidates: list[int], visited: int) -> int:
    """
    Function to determine the maximal clique in a graph. 
    graph:  List of plaintext-pairs satisfying characteristic with
            each element containing the keymasks for each of the
            known S-Boxes.
    candidates: Common keymasks amongst all visited nodes.
    visited: Bitmask representing the nodes visited so far.
    """

    # Check if the current mask is valid
    if 0 in candidates:
        return 0
    updated_visited = visited
    m = visited.bit_length() 
    # Consider nodes after the largest selected node
    for i in range(m, len(graph)):
        # Add new node
        current = graph[i]
        new_candidates = [candidates[j] & current[j] for j in range(len(candidates))]
        # Update maximal clique
        updated_visited = max(updated_visited, max_clique(graph, new_candidates, visited | (1 << i)), key=lambda x: x.bit_count())
    # Return maximal clique
    return updated_visited

# Compute suggested keys by random ciphertext pairs for the last round
# over the mentioned S_BOX_INDICES.
# These will serve as nodes for the later max-clique algorithm.

# Start time
start_time = time.time()

nodes = []
for i in range(NUM_PAIRS):
    # Generate a random 64-bit plaintext
    p1 = f"{random.getrandbits(64):064b}"
    p2 = xor(p1, CHAR)
    # Apply the inverse of the initial permutation to preserve p1, p2
    p1 = apply_matrix(FINAL_PERM, p1)
    p2 = apply_matrix(FINAL_PERM, p2)
    # Encrypt the plaintexts and peel off the final permutation
    c1 = apply_matrix(INIT_PERM, encrypt(p1))
    c2 = apply_matrix(INIT_PERM, encrypt(p2))
    # Print
    print(f"Pair {i+1}:")
    print(f"Plaintext: {get_hex(p1)}\t\tCiphertext: {get_hex(c1)}")
    print(f"Plaintext: {get_hex(p2)}\t\tCiphertext: {get_hex(c2)}")

    # Extract left half to get S-Box output
    c_left = get_left_half(xor(c1, c2))
    
    # Use the relation: F' = D' + c' + l' (assume D' = 0, c' = CHAR_R)
    # to get the output of final round
    f_prime = xor(c_left, CHAR_R)

    # Peel off the mixing permutation
    f_prime = apply_matrix(MIX_INV, f_prime)

    # Get right halves of c1, c2 and apply expansion
    c1_right = apply_matrix(EXP, get_right_half(c1))
    c2_right = apply_matrix(EXP, get_right_half(c2))

    # Print c1_right, c2_right, f_prime
    print(f"For S-Boxes")
    print(f"Input_1: {get_hex(c1_right)}\t\tInput_2: {get_hex(c2_right)}\t\tOutput_XOR: {get_hex(f_prime)}")
    print()

    # Now check for keys
    keymasks = []
    for i in S_BOX_INDICES:
        # To track which keys are possible
        keymask = 0

        # Assume a key
        for j in range(64):
            key = f"{j:06b}"

            s_box_input1 = xor(key, extract_input(i, c1_right))
            s_box_input2 = xor(key, extract_input(i, c2_right))

            # Check if the S-Box output XORed with the key is equal to f_prime
            if xor(s_box(i, s_box_input1), s_box(i, s_box_input2)) == extract_output(i, f_prime):
                keymask |= 1 << j
        keymasks.append(keymask)
    
    # Add nodes to the list
    nodes.append(keymasks)

# Run the max-clique algorithm
final_clique = max_clique(nodes, [(1<<64) - 1 for _ in S_BOX_INDICES], 0)
print(f"Final clique: {final_clique:085b}")
print()

# Get suggested keys by "AND"ing the masks of the nodes in the final clique
suggested_keys = [(1<<64) - 1 for _ in range(8)]
for i in range(len(S_BOX_INDICES)):
    for j in range(NUM_PAIRS):
        if final_clique & (1 << j):
            suggested_keys[S_BOX_INDICES[i]] &= nodes[j][i]

# Print the suggested keys
print("Suggested S-Box keys for k6:")
for i in range(8):
    print(f"S-Box {i}: {suggested_keys[i]:064b}")
print()

# Get key schedule for the last round
K_SCHED = key_schedule()
K6_SCHED = K_SCHED[5]

# Reconstruct K6
K6 = ''
known_bits = []
for i in range(8):
    if i in S_BOX_INDICES:
        K6 += f"{(suggested_keys[i].bit_length() - 1):06b}"
        known_bits += K6_SCHED[6*i:6*(i+1)]
    else:
        K6 += '000000'
print(f"Reconstructed K6: {K6}")
print()

# Main key
main_key = ''
for i in range(1, 65):
    if i in known_bits:
        main_key += K6[K6_SCHED.index(i)]
    else:
        main_key += '0'
print(f"Main key template: {main_key}")
print()

# More plaintext-ciphertext pairs for brute-force verification
pc_pairs = []
print("More plaintext-ciphertext pairs for verification:")
for i in range(NUM_FINAL):
    # Generate a random 64-bit plaintext
    p = f"{random.getrandbits(64):064b}"
    c = encrypt(p)
    # Print
    print(f"Plaintext: {get_hex(p)}\t\tCiphertext: {get_hex(c)}")
    pc_pairs.append((p, c))
print()

# Brute-forcing over 14 bits (tqdm for progress)
for i in tqdm.tqdm(range(1<<14)):
    # Construct unknown bits
    unknown_bits = 0
    for j in range(1, 65):
        if (j in known_bits) or (j%8==0):
            continue
        else:
            unknown_bits |= (i%2) << (64-j)
            i >>= 1
    unknown_bits = f"{unknown_bits:064b}"

    # XOR with known bits
    inter_key = xor(main_key, unknown_bits)

    # Compute parities
    parity = ''
    for j in range(8):
        curr_bit = 1 ^ get_parity(inter_key[8*j:8*(j+1)-1])
        parity += f"{curr_bit:08b}"

    # XOR again
    assumed_key = xor(inter_key, parity)

    # Decrypt over PC pairs
    success = True
    for p, c in pc_pairs:
        if des_decrypt(c, assumed_key) != p:
            success = False
            break
    if success:
        print(f"Found key: {assumed_key}")
        break

# End time
end_time = time.time()

# Print time taken
print(f"Time taken: {end_time - start_time:.2f} seconds")
