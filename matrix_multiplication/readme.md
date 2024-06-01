# Assignment 1: Matrix multiplication

## What the code does

The overall idea is to implement matrix multiplication using python.
Here are a few relevant questions to address:
- how is a matrix represented in python
- what are the constraints on the inputs to ensure multiplication is possible
- how to implement the multiplication


## The code itself

```python

import numbers
from collections.abc import Iterable


def matmul(m1, m2):
    """multiplies 2 compatible matrices m1 and m2 and returns a product matrix, 
    raise an exception if multiplication not possible."""

    # check if the inputs are matrix qualifiers; 
    # for example, m1 should be an iterable within an iterable: nested lists, tuple of lists
    # DO NOT ASSUME THAT THE MATRIX IS A LIST OF LISTS; IT CAN BE ANY ITERABLE

    try:
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
```

## Noteworthy ideas involved

1. There is no inbuilt matrix construct in python. We generally treat  nested lists as a matrix; the rows of the matrix are lists themselves and these rows are all stored inside of another list, which we call a matrix. In general using a tuple in place of a list is not going to cause a problem, unless the matrix values are to be edited; *tuples are immutable* .
Also, dictionaries are less user-friendly objects to implement matrices because the values cannot be indexed using numbers but rather need keys.

2. I found a couple of libraries handy while writing this code.
    1.  check if an object is of numeric type
    ```python

    import numbers
    value = 5
    if isinstance(value, numbers.Number) == True:
        print("value is of numeric data type")
    else:
        print("value is not of numeric data type")
        
    ```

    2.   check if an entity is iterable
    ```python
    
    from collections.abc import Iterable
    obj = [1,2,3]
    if isinstance(obj, Iterable) == True:
        print("object is iterable")
    else:
        print("object is not iterable")
    
    ```

## Limitations and Fixes

Notice that we are relying on python to generate an `IndexError` when any of the nested lists(iterables) are not of the same length.

But consider a case such as this:
m1 has 5 rows, all rows have 3 columns, except for the 4th one that has 6 columns. Here the 4th, 5th and the 6th elements of the 4th row of m1 are never accessed and the multiplication is carried out, even though m1 does not qualify as a matrix in the first place.
We cannot rely on python to raise IndexError for such scenarios.
One way to tackle this would be to test whether all the rows of the matrix have the same number of columns,
although this adds to the overall time in testing whether an entity is a suitable matrix or not, and especially eliminates the idea of relying on `IndexError` to get the job done.
Here is the code that checks if all rows have the same length:


```python

row_length = m1[0]
for row in m1:
    if len(row) != row_length:
        raise TypeError("the rows of m1 do not all have the same length.")

```
Although, the code I wrote passed all the tests, it would be beneficial to include the following also, to ensure correctness every time.


## Scope for improvement

This function as it stands, is a barebones matrix multiplier. It is most probably going to be used as a part of a bigger project. It is imperative that the function suits the needs of that project too.
For example, this is not the most efficient way to multiply 2 matrices under all scenarios( I am not referring to numpy.)
There are ways to execute multiplication for spare matrices with much less time complexity, utilising the fact that most of the entries of a sparse matrix are zeroes.
Also if this function is to be used to handle sensitive data, then appropriate security fortifications are in order too.
Basically, depending on the use case, this code can be modified to suit the user's needs.


