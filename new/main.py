"""
Notes:

Convert thing to pandas table.

struct a: A structure array of factors from 0-255. Contains array of numbers they are factorable towards. Minimum bit representation of quotients, and null frequencies. An array from 1-8 of minimum bit representation containing null frequencies. And a cumulative frequency.

struct b: For speed purposes, we have a structure of numbers, containing an array of their factors.

We fill struct b and then struct a. With an algorithm.
Here:

struct c: A struct array from 0-n factors with a non-zero cumulative frequency. The factor and the cumulative frequency. With a null dynamic array of best sequence generated. And dynamic array of subsequences from 1-8 bits.

We generate struct c and then sort based on cumulative frequency.

For each element of struct c. We fill best sequence array in parallel. Using algorithm.
Here:

1. From the highest frequency factor, and from highest bit representation. 

2.  We generate every possible factors and sort them based on bit reduction. 
bit reduction = freq*8 - min_bit*freq + sum([freq[0:fac]])

From the most bit reduction, Iterate in their numbers, check if number exist and has same minimum bit representation in any other factors after it, remove them if true. And then update bit reduction.

3. Generate the next sequence in lower bit representation. Merge the 2 tables, sort then do 2. Until min_bit 1.

4. If conflicting factors with different bit representations still occur. If former has higher min_bit, merge if higher bit reduction. Then store on best sequence found with corresponding bit representations and numbers.

5. Merge in between struct c s.

Everything has a minus 1 unless factor = 1.

7, 9, 14, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 25, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28 = 544 bits

List least prime factors:
This case:
7, 5, 3, 2

Greatest frequency of greatest factor mask
7: 10111111111111111110111111111111111111111111111111111111111111111111 = 68 bits
5: 01 = 2 bits
3: 1 = 1 bits

Get bits of max(groupby(arr, 7))
Then represent each number/7 - 1 in arr in those bits
0001010101010101010101010101010101010111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111 = (68-2)2 = 132 bits
Remove those numbers from arr

Get bits of max(groupby(arr, 5))
Then represent each number/5 - 1 in arr in those bits
0 = 1 bit
Remove those numbers from arr

Get bits of max(groupby(arr, 3))
Then represent each number/5 - 1 in arr in those bits
0 = 1 bit
Remove from arr

Head: byte size = 32 bits
Head: max(Header (factor)) = 8 bits
Head: bit count of factors = minbit(max(factor)) = 4 bits
Head: factor count = 8 bits
Factors: 7, 5, 3 = value(bit count of factors) value(factor count) = 9 bits

Factor Mask and Count:
 expect byte size/8
 7: 10111111111111111110111111111111111111111111111111111111111111111111 = 66 bits = byte size/8
 expect 0s count
 5: 01 = 2 bits
 expect 0s count
 3: 1 = 1 bits

Header (factors): minbit(Header (factor bits)[]) = 4 bits
Header (factor bits): minbit(max(groupby(arr, 7))/7) = 3 bits
expect value(Factor Mask Count) * value(Header (factor bits)) = (66-2) * 2 = 134 bits

Header (factor bits): minbit(max(groupby(arr, 5))/5) = 3 bits
expect value(Factor Mask Count) * value(Header (factor bits)) = 1 bit

Header (factor bits): minbit(max(groupby(arr, 3))/3) = 3 bits
expect value(Factor mask Count) * value(Header (factor bits)) = 1 bit

32 + 8 + 4 + 8 + 9 + 66 + 2 + 1 + 4 + 3 + 128 + 3 + 1 + 3 + 1 = 273 vs 544

50% Compression

If we try to transpose the matrix and finding consecutive n-bit representation in that direction it might be possible but it has to not collide with the x representation. Since their locations are predictable due to location of ending 1s
If we try to group n-bits in x axis,
1001010101111011110000111
10. 0. 0. 0. 0. 0000
0. 0. 0. 0. 0. 0001
0. 0. 0. 1. 0. 001
1. 0. 0. 1. 01
1. 1. 1
There's a pattern that consecutive 0s are ended with a 1. Which we can kinda derive an algorithm towards to get the original x representation.
From behind, 1110010001... etc.
From front, 101000011000001... etc.


1010000110000011000001100011111000011110000010000100010011110100001100000110000011000111110000111100000100001000100111
Partitioned 0s? 1
Now:
01101000011000000110100001100000 (Ignore)
Partitioned 0s? 1 (Happens twice)
Now: 001100000110
Partitioned 0s? 0
Partitioned 1s? 0

Now:
10101100110011000111110111001010001001111010110011001100011111011100101000100111
Partitioned 1s? 1
Now: 000000001000000000000000001000000000 (Ignore)
Partitioned 0s? 1
Now: 0000000000
Partitioned 0s? 1
Now: 1111011110
Partitioned 0s? 0
Partitioned 1s? 1
Now: 1010

Final: 10101100110011000111110111001010001001111010110011001100011111011100101000100111
Mask 0? 1
Conditions mask for 0s:
110
L1:
01101011000110101100
L2:
0011000110

Mask 1? 0
(Ignore)
Conditions Mask for 1s:
1110111101
L1:
001000001000
L2:
1010
L3:
11

<114 vs 118 aww... I guess it works for other examples though
Sent
Write to

"""

import random
import math
import pandas as pd
from itertools import groupby
factor_array_list = []

def generate_random_array(n):
    return [random.randint(1, 255) for _ in range(n)]

def calculate_frequencies(arr):
    frequencies = [0] * 256  # Initialize frequencies for numbers 0 to 255 with 0
    for num in arr:
        frequencies[num] += 1  # Increment frequency for the number
    return frequencies

class FactorArray:
    def __init__(self, n):
        self.n = n
        self.minbit = calculate_minbits(n)
        self.factorable_numbers = []
        self.quotients = []
        self.minbits = []
        self.bits = [[] for _ in range(8)]  # Ensure bits has 8 sublists
        self.freq = []
        self.bit_reduction = []
        
    
    def get_bit_reduction(self):
    #self.bit_reduction = []  # Initialize bit_reduction as an empty list
        print("Sizes")
        print(len(self.factorable_numbers), len(self.minbits), len(self.freq))
        for i in range(len(self.factorable_numbers)):
            # Calculate the bit reduction value using the formula and append it to bit_reduction
            reduction_value = (8 - self.minbits[i]) * self.freq[i] - self.freq[i]
            self.bit_reduction.append(reduction_value)
                
    def create_factor_array(self):
        factors = find_factorable_numbers(self.n)
        self.factorable_numbers = factors
        self.quotients = [i // self.n - 1 for i in factors]
        self.minbits = [calculate_minbits(q) for q in self.quotients]

        for i in range(len(self.factorable_numbers)):
            minbit = min(self.minbits[i], 7)  # Ensure minbit is in range [0, 7]
            self.bits[minbit].append(self.factorable_numbers[i])

        self.freq = [0] * len(self.factorable_numbers)
    
    def sort_properties(self):
        data = {
            "bit_reduction" : self.bit_reduction,
            "freq": self.freq,
            "multiplier": [1] * len(self.factorable_numbers),
            "minbits": self.minbits,
            "factorable_numbers": self.factorable_numbers,
            "factors": [self.n] * len(self.factorable_numbers),
        }
        # Example dictionary representing columns
        # Check if all required keys exist in the data dictionary

       # Check if all required keys exist in the data dictionary
        required_keys = ['bit_reduction', 'freq', 'multiplier', 'minbits', 'factorable_numbers']
        sorted_data = {}
        if all(key in data for key in required_keys):
            # Create a dictionary from the zipped key-value pairs
            sorted_data = dict(sorted(zip(data['factorable_numbers'], zip(data['bit_reduction'], data['freq'], data["multiplier"], data['minbits'], data['factors'])), key=lambda x: x[1][1], reverse=True))
            # Sort the dictionary by the 'freq' value

            print()
            # Print the sorted dictionary
            print(sorted_data)
        else:
            print("One or more required keys are missing in the data dictionary.")
        
        somesum = 0
        for i in sorted_data.values():
            somesum += i[0]
        print(somesum)
        
        self.increase_bit_reduction(sorted_data)
        
    def increase_bit_reduction(self, data):
        # Create an iterator for the dictionary items
        iterator = iter(data.items())
        # Skip the first item
        #next(iterator, None)
        # Iterate over the remaining items
        print("Reducing Values")
        for k, v in iterator:
            #print(f"Key: {k}, Value: {v}")
            facts = factor_array_list[k-1].factorable_numbers
            #print(facts)
            iterator2 = iter(facts)
            #next(iterator2, None)
            
            for i in iterator2:
                #print(i, data[i], factor_array_list[int(i/k)-1].minbit)
                #reduction_value = (8 - self.minbits[i]) * self.freq[i]
                try:
                    minbit = calculate_minbits(i//k-1)
                    #print(factor_array_list[int(i/k)-1].minbit)
                    freq = data[i][1]
                    temp = ((8 - minbit) * freq + freq, freq, data[i][2], minbit, k)
                    if data[i][0] < temp[0]:
                        data[i] = temp
                    #print(i, data[i])
                except Exception as e:
                    print(e, "Not found")
                    pass
        # Assuming you have already created the sorted_data dictionary as shown in your code

        # Group the data by the 'factors' value
        grouped_data = {}
        for key, value in data.items():
            factor = value[-1]  # Assuming the factor is the last element of the tuple
            if factor not in grouped_data:
                grouped_data[factor] = []
            grouped_data[factor].append((key, value))

        # Sort within each group based on the 'freq' value
        for factor, group in grouped_data.items():
            grouped_data[factor] = dict(sorted(group, key=lambda x: x[1][1], reverse=True))

        # Sort the groups based on the sum of the 'freq' values
        sorted_groups = sorted(grouped_data.items(), key=lambda x: sum(v[1] for _, v in x[1].items()), reverse=True)

        # Print the sorted groups
        i = 0
        new_data = {}
        for factor, sorted_group in sorted_groups:
            i += 1
            for key, value in sorted_group.items():
                #print(sorted_group[key])
                minbit = calculate_minbits(key//factor-1)
                #print(factor_array_list[int(i/k)-1].minbit)
                freq = value[1]
                #print(freq)
                #print(minbit)
                temp = ((8 - minbit) * freq - freq * i, freq, i, minbit, factor)
                #print(i)
                sorted_group[key] = temp
                #print(sorted_group[key])
                new_data[key] = sorted_group[key]
                print(f"\tKey: {key}, Value: {sorted_group[key]}")
            somesum = sum(new_data[key][0] for _, v in sorted_group.items())
            print(f"{i}, Factor: {factor}, Sum of freq: {somesum}")
        
        self.reduce_2(new_data)
        
    def reduce_2(self, data):
        new_data = {}
        last_factor = 420
        current_minbit = 4
        mult = 1
        total_somesum = 0  # Initialize total somesum

        for k, v in data.items():
            facts = factor_array_list[v[-1] - 1].factorable_numbers
            if v[-1] == last_factor:
                mult += 1
                continue
            last_factor = v[-1]

            for i in facts:
                try:
                    minbit = calculate_minbits(i // last_factor - 1)
                    if minbit > current_minbit:
                        break
                    freq = data[i][1]
                    temp = ((8 - minbit) * freq - freq ** (1 / (4 * math.log(mult, 4)))), freq, mult, data[i][2], minbit, last_factor

                    if data[i][0] < temp[0]:
                        data[i] = temp
                        new_data[i] = temp
                except Exception as e:
                    print(f"Error: {e}")
                    pass

        grouped_data = {}
        for key, value in data.items():
            factor = value[-1]
            if factor not in grouped_data:
                grouped_data[factor] = []
            grouped_data[factor].append((key, value))

        for factor, group in grouped_data.items():
            grouped_data[factor] = dict(sorted(group, key=lambda x: x[1][1], reverse=True))

        sorted_groups = sorted(grouped_data.items(), key=lambda x: sum(v[1] for _, v in x[1].items()), reverse=True)

        for i, (factor, sorted_group) in enumerate(sorted_groups, start=1):
            sorted_group = dict(sorted(sorted_group.items(), key=lambda x: x[1][1], reverse=True))  # Sort within each group by freq
            for key, value in sorted_group.items():
                minbit = calculate_minbits(key // factor - 1)
                freq = value[1]
                temp = ((8 - minbit) * freq - freq ** (1 / (4 * math.log(mult, 4)))), freq, i, minbit, factor
                sorted_group[key] = temp
                new_data[key] = temp

                # Accumulate somesum in total_somesum
                total_somesum += new_data[key][0]

                print(f"\tKey: {key}, Value: {sorted_group[key]}")

            print(f"{i}, Factor: {factor}, Sum of freq: {sum(v[1] for _, v in sorted_group.items())}")

        print(f"Total somesum: {total_somesum}")  # Print total somesum
            
            
    def get_factor_array_info(self):
        info = {
            "Size": len(self.factorable_numbers),
            "Factorable Numbers": self.factorable_numbers,
            "Minbits": self.minbits,
            "Frequency": self.freq,
            "Bits": {i: self.bits[i] for i in range(8)},
            "Bit Reduction:" : self.bit_reduction
        }
        return info

    def print_factor_array(self):
        print("Size:", len(self.factorable_numbers))
        print("Factorable Numbers:", self.factorable_numbers)
        print("Frequency:", self.freq)
        print("Minbits:", self.minbits)
        for i in range(8):
            print(f"Bits[{i}]:", self.bits[i])

def find_factorable_numbers(n):
    factors = []
    for i in range(1, 256):
        if i % n == 0:
            factors.append(i)
    return factors

def calculate_minbits(num):
    if num == 0:
        return 1  # Minimum bit representation of 0 is 1
    minbits = 0
    while num > 0:
        num >>= 1  # Right shift the number by 1 (equivalent to dividing by 2)
        minbits += 1
    return minbits

def fill_frequency(factor_array_list, sorted_frequencies):
    for i in range(2, 256):
        print("i", i)
        print(factor_array_list[i-2].factorable_numbers)
        for j in factor_array_list[i-2].factorable_numbers:
            for k, frequency in sorted_frequencies:
                if k == j:
                    print("i", i, "j", j, k, frequency)
                    factor_array_list[i-2].freq[int(j/(i - 1))-1] = frequency
                    print(factor_array_list[i-2].factorable_numbers[int(j/(i - 1))-1], factor_array_list[i-2].freq[int(j/(i - 1))-1])
        #print(factor_array_list[i].freq)
        #factor_array.freq = frequencies

def calculate_factor_frequencies(random_array):
    frequencies = {}
    for number in random_array:
        factors = calculate_factors(number)
        for factor in factors:
            if factor in frequencies:
                frequencies[factor] += 1
            else:
                frequencies[factor] = 1
    return frequencies

def calculate_factors(number):
    factors = set()
    for i in range(1, int(math.sqrt(number)) + 1):
        if number % i == 0:
            factors.add(i)
            factors.add(number // i)
    return factors
    
def main():
    # Usage
    for n in range(1, 256):
        factor_array = FactorArray(n)
        factor_array.create_factor_array()
        factor_array_list.append(factor_array)

    n = 1000  # Example size of the random array
    random_array = generate_random_array(n)
    with open('main.py', 'rb') as file:
        random_array = file.read()
    frequencies = calculate_frequencies(random_array)

    # Create a list of tuples (number, frequency) and sort it based on frequency in descending order
    sorted_frequencies = sorted(enumerate(frequencies), key=lambda x: x[1], reverse=True)

    fill_frequency(factor_array_list, sorted_frequencies)

    # Print the frequencies in the factor arrays
    for factor_array in factor_array_list:
        print()
        print(factor_array.factorable_numbers)
        print(factor_array.freq)
    print(sorted_frequencies)
    
    factor_frequencies = calculate_factor_frequencies(random_array)

    # Sort the factor frequencies dictionary by value (frequency) in descending order
    sorted_factor_frequencies = sorted(factor_frequencies.items(), key=lambda x: x[1], reverse=True)
    """
        # Print the sorted factor frequency table
    for factor, frequency in sorted_factor_frequencies:
        print(f"Factor {factor}: {frequency} times")
    """
    print(sorted_factor_frequencies)
    
    for factor_array in factor_array_list:
        factor_array.get_bit_reduction()
    print("Bit Reduced!")
    print(factor_array_list[1].get_factor_array_info())
    sorted_factor_array_list = []
    some_i = 100
    for factor, frequency in sorted_factor_frequencies:
        try:
            #print(factor)
            sorted_factor_array_list.append(factor_array_list[factor])
            print(factor_array_list[factor].n)
        except:
            pass
    print(sorted_factor_array_list[1].get_factor_array_info())
    factor_array_list[0].sort_properties()
    
if __name__ == "__main__":
    main()

