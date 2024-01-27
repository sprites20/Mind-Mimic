# factorable_numbers.pyx

from libc.stdlib cimport malloc, free
from libc.string cimport memset

cdef struct CFactorArray:
    int size
    int* factorable_numbers
    int* quotients
    int* minbits
    int** bits
    int* freq

cdef list find_factorable_numbers(int n):
    cdef list factors = []
    cdef int i
    for i in range(1, 256):
        if i % n == 0:
            factors.append(i)
    return factors

cdef int calculate_minbits(int num):
    if num == 0:
        return 1  # Minimum bit representation of 0 is 1
    cdef int minbits = 0
    while num > 0:
        num >>= 1  # Right shift the number by 1 (equivalent to dividing by 2)
        minbits += 1
    return minbits

cdef class FactorArray:
    cdef CFactorArray* c_struct

    def __cinit__(self):
        self.c_struct = <CFactorArray*>malloc(sizeof(CFactorArray))

    def __dealloc__(self):
        free(self.c_struct.factorable_numbers)
        free(self.c_struct.quotients)
        free(self.c_struct.minbits)
        for i in range(8):
            free(self.c_struct.bits[i])
        free(self.c_struct.bits)
        free(self.c_struct.freq)

    property size:
        def __get__(self):
            return self.c_struct.size

    property factorable_numbers:
        def __get__(self):
            return [self.c_struct.factorable_numbers[i] for i in range(self.c_struct.size)]

    def create_factor_array(self, int n):
        cdef int i
        cdef list factors = find_factorable_numbers(n)
        self.c_struct.size = len(factors)
        self.c_struct.factorable_numbers = <int*>malloc(self.c_struct.size * sizeof(int))
        self.c_struct.quotients = <int*>malloc(self.c_struct.size * sizeof(int))
        self.c_struct.minbits = <int*>malloc(self.c_struct.size * sizeof(int))
        self.c_struct.freq = <int*>malloc(self.c_struct.size * sizeof(int))
        # Initialize memory with zeros
        memset(self.c_struct.factorable_numbers, 0, self.c_struct.size * sizeof(int))
        memset(self.c_struct.quotients, 0, self.c_struct.size * sizeof(int))
        memset(self.c_struct.minbits, 0, self.c_struct.size * sizeof(int))
        memset(self.c_struct.freq, 0, self.c_struct.size * sizeof(int))
        # Allocate memory for other arrays and fill them similarly
        for i in range(self.c_struct.size):
            self.c_struct.factorable_numbers[i] = factors[i]
            self.c_struct.quotients[i] = factors[i] // n - 1
            self.c_struct.minbits[i] = calculate_minbits(self.c_struct.quotients[i])
            self.c_struct.freq[i] = 0  # You can initialize freq to some default value if needed
        # Determine the maximum minbits value
        max_minbits = 0
        for i in range(self.c_struct.size):
            if self.c_struct.minbits[i] > max_minbits:
                max_minbits = self.c_struct.minbits[i]
        # Allocate memory for the bits array based on the maximum minbits value
        self.c_struct.bits = <int**>malloc((max_minbits + 1) * sizeof(int*))
        for i in range(max_minbits + 1):
            self.c_struct.bits[i] = <int*>malloc(self.c_struct.size * sizeof(int))
            # Initialize bits array with zeros
            memset(self.c_struct.bits[i], 0, self.c_struct.size * sizeof(int))
        # Fill the bits array
        for i in range(self.c_struct.size):
            minbit = self.c_struct.minbits[i]
            self.c_struct.bits[minbit][i] = self.c_struct.factorable_numbers[i]

    def get_factor_array_info(self):
        info = {
            "Size": self.c_struct.size,
            "Factorable Numbers": [self.c_struct.factorable_numbers[i] for i in range(self.c_struct.size)],
            "Minbits": [self.c_struct.minbits[i] for i in range(self.c_struct.size)],
            "Bits": {i: [self.c_struct.bits[i][j] for j in range(self.c_struct.size)] for i in range(8)}
        }
        return info

    def print_factor_array(self):
        print("Size:", self.c_struct.size)
        print("Factorable Numbers:", [self.c_struct.factorable_numbers[i] for i in range(self.c_struct.size)])
        #print("Quotients:", [self.c_struct.quotients[i] for i in range(self.c_struct.size)])
        print("Minbits:", [self.c_struct.minbits[i] for i in range(self.c_struct.size)])
        for i in range(8):
            print(f"Bits[{i}]:", [self.c_struct.bits[i][j] for j in range(self.c_struct.size)])
        # Print other fields similarly

    @staticmethod
    def print_array_of_factor_arrays(factor_arrays):
        for factor_array in factor_arrays:
            factor_array.print_factor_array()
            print()
