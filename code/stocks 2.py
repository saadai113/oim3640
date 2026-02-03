import random
import math
import numpy as np

def mc_european_call_antithetic(S0, K, r, sigma, T, N=100_000, seed=1):
    np.random.seed(seed)
    
    # Generate N/2 random numbers
    Z = np.random.standard_normal(N // 2)
    
    # Use both Z and -Z (antithetic pairs)
    drift = (r - 0.5 * sigma**2) * T
    diffusion = sigma * np.sqrt(T)
    
    ST_pos = S0 * np.exp(drift + diffusion * Z)
    ST_neg = S0 * np.exp(drift - diffusion * Z)  # Antithetic
    
    payoffs_pos = np.maximum(ST_pos - K, 0.0)
    payoffs_neg = np.maximum(ST_neg - K, 0.0)
    
    # Average the antithetic pairs first, then average all
    paired_payoffs = (payoffs_pos + payoffs_neg) / 2
    
    disc = np.exp(-r * T)
    price = disc * np.mean(paired_payoffs)
    se = disc * np.std(paired_payoffs, ddof=1) / np.sqrt(N // 2)
    
    ci_low = price - 1.96 * se
    ci_high = price + 1.96 * se
    
    return price, se, (ci_low, ci_high)
