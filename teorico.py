import numpy as np
from scipy import stats

def bose(x, f):
 return (f**x)/((1+f)**(1+x))

#distribucion de poisson
def poisson(x, f):
    return stats.poisson.pmf(x, f)

#cuadratica
def cuadratica(x, m, b, c):
  return m * x**2 + b*x + c

#gaussiana
def gaussiana(x, a, mu, sigma) :
  return (a / (sigma * np.sqrt(2 * np.pi))) * np.exp(-((x - mu)**2) / (2 * sigma**2))

def expon(x, f):
    return stats.expon.pdf(x, scale = f)