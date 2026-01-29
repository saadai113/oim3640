import random
import math

def mc_european_call(S0, K, r, sigma, T, N=200_000, seed=1):
    random.seed(seed)
    disc = math.exp(-r * T)
    mu = (r - 0.5 * sigma * sigma) * T
    vol = sigma * math.sqrt(T)

    payoffs = []
    for _ in range(N):
        Z = random.gauss(0.0, 1.0)
        ST = S0 * math.exp(mu + vol * Z)
        payoff = max(ST - K, 0.0)
        payoffs.append(payoff)

    # Monte Carlo estimate
    mean_payoff = sum(payoffs) / N
    price = disc * mean_payoff

    # Standard error + 95% CI (normal approx)
    # sample variance
    m2 = sum((p - mean_payoff)**2 for p in payoffs) / (N - 1)
    se = disc * math.sqrt(m2 / N)
    ci_low = price - 1.96 * se
    ci_high = price + 1.96 * se
    return price, se, (ci_low, ci_high)

price, se, ci = mc_european_call(S0=100, K=100, r=0.05, sigma=0.2, T=1.0, N=200_000)
print("MC price:", price)
print("Std error:", se)
print("95% CI:", ci)
