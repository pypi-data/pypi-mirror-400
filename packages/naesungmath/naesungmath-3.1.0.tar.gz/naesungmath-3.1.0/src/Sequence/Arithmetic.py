import math

class Arithmetic:
    """
    Arithmetic Progression Solver
    
    Provides methods to calculate the nth term, sum, and missing variables 
    of an arithmetic progression.
    """

    @staticmethod
    def nth_term(a: float, d: float, n: float) -> float:
        """
        Calculates the nth term of an arithmetic progression.
        Formula: an = a + (n - 1)d
        """
        return a + (n - 1) * d

    @staticmethod
    def first_term(d: float, n: float, an: float) -> float:
        """
        Calculates the first term given d, n, an.
        Formula: a = an - (n - 1)d
        """
        return an - (n - 1) * d

    @staticmethod
    def common_difference(a: float, n: float, an: float) -> float:
        """
        Calculates the common difference given a, n, an.
        Formula: d = (an - a) / (n - 1)
        """
        if n == 1:
            raise ValueError("Cannot determine common difference with only 1 term.")
        return (an - a) / (n - 1)

    @staticmethod
    def number_of_terms(a: float, d: float, an: float) -> float:
        """
        Calculates the number of terms given a, d, an.
        Formula: n = (an - a) / d + 1
        """
        if d == 0:
            raise ValueError("Common difference is 0; infinite terms or invalid input.")
        return (an - a) / d + 1

    @staticmethod
    def sum(a: float, an: float, n: float) -> float:
        """
        Calculates the sum of an arithmetic progression.
        Formula: S = n(a + an) / 2
        """
        return (n * (a + an)) / 2

    @staticmethod
    def solve(a=None, d=None, n=None, an=None, s=None) -> dict:
        """
        Smart Solver: Analyzes the arithmetic progression and calculates missing variables.
        Input must have at least 3 distinct variables to solve for the others.
        
        :param a: First term
        :param d: Common difference
        :param n: Number of terms
        :param an: Nth term
        :param s: Sum of terms
        :return: Dictionary containing all variables including calculated ones.
        """
        
        changed = True
        while changed:
            changed = False
            
            # 1. Relations involving a, d, n, an
            # an = a + (n-1)d
            if an is None and a is not None and n is not None and d is not None:
                an = Arithmetic.nth_term(a, d, n)
                changed = True
            
            if a is None and an is not None and n is not None and d is not None:
                a = Arithmetic.first_term(d, n, an)
                changed = True
                
            if d is None and a is not None and an is not None and n is not None and n != 1:
                d = Arithmetic.common_difference(a, n, an)
                changed = True
                
            if n is None and a is not None and an is not None and d is not None and d != 0:
                n = Arithmetic.number_of_terms(a, d, an)
                changed = True

            # 2. Relations involving Sum
            # s = n(a + an) / 2
            if s is None and n is not None and a is not None and an is not None:
                s = Arithmetic.sum(a, an, n)
                changed = True
                
            if n is None and s is not None and a is not None and an is not None and (a + an) != 0:
                n = (2 * s) / (a + an)
                changed = True
                
            if a is None and s is not None and n is not None and an is not None:
                a = (2 * s) / n - an
                changed = True
                
            if an is None and s is not None and n is not None and a is not None:
                an = (2 * s) / n - a
                changed = True

            # 3. Relations involving Sum and D (Derived variations)
            
            # S = n/2 * (2a + (n-1)d) -> Solve for a
            # a = S/n - (n-1)d/2
            if a is None and s is not None and n is not None and d is not None and n != 0:
                a = (s / n) - ((n - 1) * d) / 2
                changed = True

            # Solve for d: d = (2S/n - 2a) / (n-1)
            if d is None and s is not None and n is not None and a is not None and n != 0 and n != 1:
                d = ((2 * s) / n - 2 * a) / (n - 1)
                changed = True
            
            # Solve for n (Quadratic): dn^2 + (2a-d)n - 2S = 0
            if n is None and s is not None and a is not None and d is not None and d != 0:
                discriminant = math.pow(2 * a - d, 2) + 8 * d * s
                if discriminant >= 0:
                    root = (-(2 * a - d) + math.sqrt(discriminant)) / (2 * d)
                    if root > 0 and abs(root - round(root)) < 1e-9: # Check for integer close enough
                        n = round(root)
                        changed = True

            # S = n/2 * (2an - (n-1)d) -> Solve for an
            # an = S/n + (n-1)d/2
            if an is None and s is not None and n is not None and d is not None and n != 0:
                an = (s / n) + ((n - 1) * d) / 2
                changed = True

            # Check for completeness
            if None not in [a, d, n, an, s]:
                break
        
        if any(v is None for v in [a, d, n, an, s]):
            raise ValueError("Insufficient data to solve the arithmetic progression.")
            
        return {'a': a, 'd': d, 'n': n, 'an': an, 's': s}
