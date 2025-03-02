### Breaking 6-Round Weak DES
### Topics In Cryptanalysis (Spring 2025)
### Rishit D
### CS21BTECH11053

#### Code Structure Overview
This repository contains the following files:
1. `custom_des.py` - Contains the implementation of the DES algorithm.
2. `s_box_diff.py` - Contains the code to analyze differentials.
3. `oracle.py` - Contains the oracle implementation as per given URL.
4. `matrices.py` - Contains the matrices used for DES.
5. `helpers.py` - Contains helper functions for permutations and S-Box instructions in `str` format.
6. `Report` - Folder containing the report for the project (along with the `LaTeX` source code).
7. `tables` - Folder containing the differential tables for each S-Box. Default location for output of `s_box_diff.py`.
8. `requirements.txt` - Contains `python` library requirements.

#### Analyzing differentials
To analyze the differentials, we first generate differential tables for each S-Box. We then look at high probability instances with single-input differences resulting in single-output differences or no out differences. We then provide reconstructed input and output to verify if the exapnsion might affect other S-Boxes. To obtain these results, run the following code.
```python3 s_box_diff.py```

#### Extracting final key
To retrieve final key, we run the clique counting scheme and brute force remaining keybits. To obtain final key, run the following code.
```python3 final_key.py```

