
class ArithmeticProgression:
    @staticmethod
    def solve(*, a=None, d=None, n=None, an=None, s=None):
        """
        Solves for missing Arithmetic Progression variables.
        Strictly enforces keyword arguments.
        """
        changed = True
        loop_count = 0
        
        def is_def(v): return v is not None

        while changed and loop_count < 5:
            changed = False
            
            # 1. an = a + (n-1)d
            if not is_def(an) and is_def(a) and is_def(n) and is_def(d):
                an = a + (n - 1) * d
                changed = True
            
            # 2. s = n(a + an)/2
            if not is_def(s) and is_def(n) and is_def(a) and is_def(an):
                s = n * (a + an) / 2
                changed = True
            
            # 3. s = n(2a + (n-1)d)/2
            if not is_def(s) and is_def(n) and is_def(a) and is_def(d):
                s = n * (2 * a + (n - 1) * d) / 2
                changed = True

            # Inverses
            # a from an, n, d
            if not is_def(a) and is_def(an) and is_def(n) and is_def(d):
                a = an - (n - 1) * d
                changed = True
                
            loop_count += 1
            
        return {
            "a": a,
            "d": d,
            "n": n,
            "an": an,
            "sum": s,
            "s": s 
        }
