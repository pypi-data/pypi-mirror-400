# Set of all valid commands/keywords in HWP Equation script

KEYWORDS = {
    # Structure
    'OVER', 'ATOP', 'SQRT', 'ROOT', 
    'LEFT', 'RIGHT',
    'MATRIX', 'PMATRIX', 'BMATRIX', 'DMATRIX', 'CASES',
    'PILE', 'LPILE', 'RPILE',
    
    # Scripts
    'SUP', 'SUB', # usually ^ and _
    'LSUP', 'LSUB',

    # Decorations
    'vec', 'dyad', 'acute', 'grave', 'dot', 'ddot', 'hat', 'check', 'arch', 'tilde', 'bar', 'under',

    # Big Operators
    'INT', 'OINT', 'DINT', 'TINT',
    'SUM', 'PROD', 'UNION', 'INTER', 
    'lim', 'Lim',

    # Operations
    'times', 'divide', 'plusminus', 'mp', 
    'bullet', 'circ', 
    
    # Relations
    'le', 'ge', 'ne', 'equiv', 'sim', 'approx', 'cong', 
    'subset', 'supset', 'in', 'ni', 
    'perp', 'parallel',
    'larrow', 'rarrow', 'lrarrow', 'Uparrow', 'Darrow', 
    
    # Logic
    'for', 'all', 'exist', 'and', 'or', 'xor', 'not', 
    
    # Functions (Auto Roman)
    'sin', 'cos', 'tan', 'cot', 'sec', 'csc',
    'sinh', 'cosh', 'tanh', 'coth',
    'log', 'ln', 'lg', 'exp', 
    'det', 'gcd', 'lcm', 'mod', 'dim', 'deg',

    # Special
    'inf', 'infinity', 'partial', 'nabla', 
    'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega',
    'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda', 'Mu', 'Nu', 'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma', 'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega',
    
    # Layout
    'rm', 'it', 'bold', 'scale', 'color', 
    '#', '&'
}

# Mapping specific synonyms or symbols if needed
SYMBOL_MAP = {
    'plusminus': '±',
    'times': '×',
    'divide': '÷',
    'alpha': 'α',
    'beta': 'β',
    # ... extensive mapping can be added here
}
