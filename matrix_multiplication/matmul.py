
import numbers
from collections.abc import Iterable


def matmul(m1, m2):
    """multiplies 2 compatible matrices m1 and m2 and returns a product matrix, 
    raise an exception if multiplication not possible."""

    # check if the inputs are matrix qualifiers; 
    # for example, m1 should be an iterable within an iterable: nested lists, list of tuples
    # DO NOT ASSUME THAT THE MATRIX IS A LIST OF LISTS; IT CAN BE ANY ITERABLE

    try:
        # test if the objects within m1 and m2 are iterable
        for ele in m1: # this statement will raise an error if m1 itself is not iterable.
            if isinstance(ele,Iterable) != True:
                raise TypeError("The entries inside the input object are not iterable")

        for ele in m2: # this statement will raise an error if m2 itself is not iterable.
            if isinstance(ele,Iterable) != True:
                raise TypeError("The entries inside the input object are not iterable")

        # test if the matrices are compatible
        # relying on indexerror to spot discrepancies in the row, column count of the matrices.
        if len(m1[0]) != len(m2):
            raise ValueError("matrices are not compatible for multiplication")
        
        # check if all the rows have the same length
        row_length = m1[0]
        for row in m1:
            if len(row) != row_length:
                raise TypeError("the rows of m1 do not all have the same length.")
        
        row_length = m2[0]
        for row in m2:
            if len(row) != row_length:
                raise TypeError("the rows of m2 do not all have the same length.")

        
        # check if all the elements in the matrices are numeric
        # first check m1:
        # there is a possibility for IndexError in the following lines
        for row in range(len(m1)):
            for col in range(len(m1[0])):
                if isinstance(m1[row][col],numbers.Number) != True:
                    raise TypeError("The entries in the first matrix are not numeric")
                
        # now check m2:
        for row in range(len(m2)):
            for col in range(len(m2[0])):
                if isinstance(m2[row][col],numbers.Number) != True:
                    raise TypeError("The entries in the second matrix are not numeric")
    except IndexError:
        raise IndexError("not all the columns are of the required length")
    
    # m1 is m x n and m2 is n x k
    #  now calculate the product
    m1_rows = len(m1)
    m1_cols = len(m2)
    m2_cols = len(m2[0]) # m2_rows = m1_cols

    # product matrix, with m rows and k columns, initially all 0 entries.
    prodm=[([0]*m2_cols) for i in range(m1_rows)] 

    # prodm(i,j) is the dot product of the ith row of m1 and the jth column of m2
    for row in range(m1_rows):
        for col in range(m2_cols):
            dot_prod = 0
            for m2_cols in range(m1_cols):
                dot_prod += m1[row][m2_cols] * m2[m2_cols][col]
            prodm[row][col] = dot_prod
    return prodm

""" consider an example such as this:
m1 has 5 rows, all rows have 3 columns, except for the 4th one that has 6 rows.
you cannot rely on python to raise IndexError for such scenarios.
one way to tackle this would be 
to test whether all the rows of the matrix have number of columns,
although this adds to the overall work 
to test whether an entity is a suitable matrix or not"""
