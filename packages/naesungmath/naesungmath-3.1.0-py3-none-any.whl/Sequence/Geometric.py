import math

class Geometric:
    """
    Geometric Progression Solver
    
    Provides methods to calculate the nth term, sum, and missing variables 
    of a geometric progression.
    """

    @staticmethod
    def nth_term(a: float, r: float, n: float) -> float:
        """
        Calculates the nth term of a geometric progression.
        Formula: an = a * r^(n - 1)
        """
        return a * math.pow(r, n - 1)

    @staticmethod
    def first_term(r: float, n: float, an: float) -> float:
        """
        Calculates the first term given r, n, an.
        Formula: a = an / r^(n - 1)
        """
        if r == 0:
            raise ValueError("Common ratio is 0; first term cannot be uniquely determined from nth term.")
        return an / math.pow(r, n - 1)

    @staticmethod
    def common_ratio(a: float, n: float, an: float) -> float:
        """
        Calculates the common ratio given a, n, an.
        Formula: r = (an / a)^(1 / (n - 1))
        """
        if a == 0:
            raise ValueError("First term is 0; common ratio is undefined/indeterminate.")
        if n == 1:
            raise ValueError("Cannot determine common ratio with only 1 term.")
        return math.pow(an / a, 1 / (n - 1))

    @staticmethod
    def number_of_terms(a: float, r: float, an: float) -> float:
        """
        Calculates the number of terms given a, r, an.
        Formula: n = log_r(an / a) + 1
        """
        if a == 0 or r <= 0 or r == 1:
            raise ValueError("Invalid inputs for logarithmic calculation of n.")
        return (math.log(an / a) / math.log(r)) + 1

    @staticmethod
    def sum(a: float, r: float, n: float) -> float:
        """
        Calculates the sum of a geometric progression.
        Formula: S = a(r^n - 1) / (r - 1) for r != 1
                 S = na for r = 1
        """
        if r == 1:
            return n * a
        return (a * (math.pow(r, n) - 1)) / (r - 1)
        
    @staticmethod
    def infinite_sum(a: float, r: float) -> float:
        """
        Calculates the sum of an infinite geometric progression.
        Formula: S = a / (1 - r) for |r| < 1
        """
        if abs(r) >= 1:
            raise ValueError("Infinite sum only exists for |r| < 1.")
        return a / (1 - r)

    @staticmethod
    def solve(a=None, r=None, n=None, an=None, s=None) -> dict:
        """
        Smart Solver: Analyzes the geometric progression and calculates missing variables.
        Input must have at least 3 distinct variables to solve for the others.
        
        :param a: First term
        :param r: Common ratio
        :param n: Number of terms
        :param an: Nth term
        :param s: Sum of terms
        :return: Dictionary containing all variables including calculated ones.
        """
        
        changed = True
        while changed:
            changed = False
            
            # 1. Relations involving a, r, n, an
            # an = a * r^(n-1)
            if an is None and a is not None and r is not None and n is not None:
                an = Geometric.nth_term(a, r, n)
                changed = True
            
            if a is None and an is not None and r is not None and n is not None and r != 0:
                a = Geometric.first_term(r, n, an)
                changed = True
                
            if r is None and a is not None and an is not None and n is not None and a != 0 and n != 1:
                r = Geometric.common_ratio(a, n, an)
                changed = True
                
            if n is None and a is not None and r is not None and an is not None and a != 0 and r > 0 and r != 1:
                n = Geometric.number_of_terms(a, r, an)
                changed = True

            # 2. Relations involving Sum
            # S = a(r^n - 1) / (r - 1)
            if s is None and a is not None and r is not None and n is not None:
                s = Geometric.sum(a, r, n)
                changed = True
            
            # Solve for a: a = S(r-1) / (r^n - 1)
            if a is None and s is not None and r is not None and n is not None:
                if r == 1:
                    a = s / n
                    changed = True
                else:
                    num = math.pow(r, n) - 1
                    if num != 0:
                        a = (s * (r - 1)) / num
                        changed = True

            # Solve for an using Sum: an = (S(r-1) + a) / r
            if an is None and s is not None and r is not None and a is not None and r != 0 and r != 1:
                an = (s * (r - 1) + a) / r
                changed = True

            # Check for completeness
            if None not in [a, r, n, an, s]:
                break
        
        if any(v is None for v in [a, r, n, an, s]):
            raise ValueError("Insufficient data to solve the geometric progression.")
            
        return {'a': a, 'r': r, 'n': n, 'an': an, 's': s}
