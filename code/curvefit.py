# This file should be run on your own computer in order to get 
# five parameters for a curve fit. You need to have numpy,
# scipy, and matplotlib installed. 

# One easy way to do that is to transfer this file and the
# requirements.txt file to your computer and run
# `pip install -r requirements.txt`
# in the directory with requirements.txt

# Then you need to fill in the values for two arrays below
# T and R. Then run this script. It will spit out a list that
# you can copy into the settings.json file in the t1Params or
# the t2Params. It will also show you a plot of the fit.

# Th

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as poly

# Fill these temperatures in with the values you measured.
T = [-21.72, 13.84, 25.44, 37.05, 48.85, 72.66, 82.34, 93.92, 106.34]
T = [-21.43, 10.13, 34.21, 44.56, 54.95, 66.13, 77.89, 89.45, 99.36]
# T = [-21.43, 10.13, 34.21, 44,56, 54.95, 66.13, 77.89, 89.45]/
# Fill in the matching resistances.
#R =  [96064.9, 16412.8, 9719.2, 5613.4, 3266.2, 1467.5, 1080.3, 748.2,  536.0]
#R = [96176.4, 16406.6, 9756.3, 6671.7, 4600.1, 1991.5, 1533.2, 1074.8, 757.8]

R = [100815.77, 19644.46, 6808.194, 4742.921, 3277.293, 2244.594, 1520.885, 1066.824545, 824.5571]

# R = [100444.49, 19720.07, 6733.9,  4547.141, 3096.442, 2134.607, 1451.03, 1018.236364, 770.1482]

T = np.array(T)

R = np.array(R)

invSqrtLnR = 1/(np.sqrt(np.log(R)))

coef, cov = poly.polyfit(invSqrtLnR, T, 4,full=True)

x = np.linspace(invSqrtLnR.min(), invSqrtLnR.max(), 2000)
y = poly.Polynomial(coef)

fig = plt.figure(figsize=(8,5))
# ax = fig.add_axes([0,0,1,1])
ax = fig.add_subplot(111)
ax.plot(invSqrtLnR, T, "r.")
ax.plot(x, y(x), 'b-', linewidth=1)

print(f"\r\nPARAMS: [{coef[0]}, {coef[1]}, {coef[2]}, {coef[3]}, {coef[4]}] \r\n")
print(y)

plt.show()
