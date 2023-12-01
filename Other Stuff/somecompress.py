from collections import Counter
import secrets

#n_now = min_bit * frequency
def generate_random_bytes(length):
    random_bytes = secrets.token_bytes(length)
    return random_bytes

def find_factors(n):
    factors = set()
    for i in range(1, n + 1):
        if n % i == 0:
            factors.add(i)
    return factors

def generate_byte_frequency_table(byte_sequence, n_then):
    byte_frequency = Counter(byte_sequence)
    
    # Create a dictionary to store factors and their corresponding frequencies
    factor_frequency = {}
    
    # Find factors for each byte value and update factor_frequency
    for byte, frequency in byte_frequency.items():
        factors = find_factors(byte)
        for factor in factors:
            if factor not in factor_frequency:
                factor_frequency[factor] = frequency
            else:
                factor_frequency[factor] += frequency
    
    # Sort the factors based on frequency in descending order
    sorted_factors = sorted(factor_frequency.items(), key=lambda x: x[1], reverse=True)
    
    # Create a dictionary for each factor with minimum bits, byte sequence, and frequency
    result_dict = {}
    n_now = False
    for factor, _ in sorted_factors:
        # Find the quotients of the numbers divisible by the factor
        quotient_frequency = Counter()
        for byte, frequency in byte_frequency.items():
            if byte % factor == 0:
                quotient = byte // factor
                quotient_frequency[quotient] += frequency
        
        # Sort the quotients based on frequency in descending order
        sorted_quotients = sorted(quotient_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Create a dictionary for each factor with minimum bits, byte sequence, and frequency
        factor_dict = {}
        for quotient, frequency in sorted_quotients:
            min_bit = len(bin(quotient)) - 2  # Calculate the minimum bit representation
            if min_bit not in factor_dict:
                factor_dict[min_bit] = {'byte_sequence': set([factor*byte for byte, _ in sorted_quotients if len(bin(byte)) - 2 == min_bit]),
                                        'frequency': frequency}
            else:
                factor_dict[min_bit]['byte_sequence'].update([factor*byte for byte, _ in sorted_quotients if len(bin(byte)) - 2 == min_bit])
                factor_dict[min_bit]['frequency'] += frequency
            factor_dict[min_bit]["n_then"] = n_then
            n_now = factor_dict[min_bit]['frequency'] * min_bit
            factor_dict[min_bit]["n_now"] = n_now
            #Do Recursion here
            if not n_then == n_now
            factor_dict[min_bit]['tail'] = {}
        # Add the factor dictionary to the result dictionary
        result_dict[factor] = factor_dict
    """
    # Create a dictionary to store the final result
    final_result_dict = {}
    
    # Iterate through factors in descending order of frequency
    for factor, factor_dict in sorted(result_dict.items(), key=lambda x: max(x[1].keys()), reverse=True):
        factor_info = {'min_bits': {}}
        
        # Iterate through minimum bits in descending order
        for min_bit, min_bit_info in sorted(factor_dict.items(), key=lambda x: x[0], reverse=True):
            original_byte_sequences = [byte for byte in min_bit_info['byte_sequence']]
            factor_info['min_bits'][min_bit] = {
                'byte_sequence': original_byte_sequences,
                'frequency': min_bit_info['frequency'],
                'n_now' : min_bit_info["n_now"],
                'tail': {}
            }
            
            # Generate the byte frequency table for the tail
            tail_byte_frequency_table = generate_byte_frequency_table_for_tail(original_byte_sequences, min_bit_info["n_now"])
            factor_info['min_bits'][min_bit]['tail'] = tail_byte_frequency_table
        
        final_result_dict[factor] = factor_info
    """
    return result_dict

# Function to generate byte frequency table for the tail
def generate_byte_frequency_table_for_tail(tail_byte_sequence, n):
    return generate_byte_frequency_table(tail_byte_sequence, n)

# Example usage:
random_byte_length = 20
random_bytes = generate_random_bytes(random_byte_length)

print(f"Random Bytes: {random_bytes}")
result_dict = generate_byte_frequency_table(random_bytes, random_byte_length*8)

# Create a dictionary to store the final result
final_result_dict = {}

# Iterate through factors in descending order of frequency
for factor, factor_dict in sorted(result_dict.items(), key=lambda x: max(x[1].keys()), reverse=True):
    factor_info = {'min_bits': {}}
    
    # Iterate through minimum bits in descending order
    for min_bit, min_bit_info in sorted(factor_dict.items(), key=lambda x: x[0], reverse=True):
        original_byte_sequences = [byte for byte in min_bit_info['byte_sequence']]
        factor_info['min_bits'][min_bit] = {
            'byte_sequence': original_byte_sequences,
            'frequency': min_bit_info['frequency'],
            'n_then' : min_bit_info["n_then"],
            'n_now' : min_bit_info["n_now"],
            'tail': {}
        }
        
        # Generate the byte frequency table for the tail
        tail_byte_frequency_table = generate_byte_frequency_table_for_tail(original_byte_sequences, min_bit_info["n_now"])
        factor_info['min_bits'][min_bit]['tail'] = tail_byte_frequency_table
    
    final_result_dict[factor] = factor_info

# Print the final result dictionary
for factor, factor_info in final_result_dict.items():
    print(f"\nFactor {factor}:")
    
    for min_bit, min_bit_info in factor_info['min_bits'].items():
        print(f"\tMinimum Bit {min_bit}:")
        print(f"\tByte Sequence: {min_bit_info['byte_sequence']}")
        print(f"\tFrequency: {min_bit_info['frequency']}")
        print(f"\tn_then: {min_bit_info['n_then']}")
        print(f"\tn_now: {min_bit_info['n_now']}")
        # Print the byte frequency table for the tail
        print(f"\tTail Byte Frequency Table: {min_bit_info['tail']}")
        
        print()
