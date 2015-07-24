#!/usr/bin/env python3
# Requires QuantLib-SWIG with modified options.i

# <headingcell level=1>
# Data for barrier option

# <codecell>
from QuantLib import *
import matplotlib.pyplot as plt

barrier, barrierType, optionType, rebate = (80.0, Barrier.DownOut, Option.Call, 0.0)
underlying, strike, rf, sigma, maturity, divYield = (100, 105, 5e-2, 20e-2, 1.0, 0.0)
## maturity is in years and must correspond to an integral number of months
barrier_data = dict( (name,eval(name)) for name in [
    'barrier', 'barrierType', 'optionType', 'rebate', 'underlying', 'strike', 
    'rf', 'sigma', 'maturity', 'divYield'] )
barrier_data['barrierType'] = ['DownIn', 'UpIn', 'DownOut', 'UpOut'][barrier_data['barrierType']]
barrier_data['optionType'] = ['Put', '???', 'Call'][barrier_data['optionType']+1]
for k in barrier_data.keys():
    print("{} = {}".format(k, barrier_data[k]))

# <headingcell level=1>
# Compute price of barrier option using finite difference method for different grid sizes

# <codecell>
Grids = (5, 10, 25, 50, 100, 1000, 5000)
maxG = Grids[-1]

today = Settings.instance().evaluationDate
maturity_date = today + int(maturity * 12)
process = BlackScholesMertonProcess(
    QuoteHandle(SimpleQuote(underlying)),
    YieldTermStructureHandle(FlatForward(today, divYield, Thirty360())),
    YieldTermStructureHandle(FlatForward(today, rf, Thirty360())),
    BlackVolTermStructureHandle(BlackConstantVol(
        today, NullCalendar(), sigma, Thirty360())))
option = BarrierOption(barrierType, barrier, rebate, 
                       PlainVanillaPayoff(optionType, strike), 
                       EuropeanExercise(maturity_date))
option.setPricingEngine(AnalyticBarrierEngine(process))
trueValue = option.NPV()
uErrors = []
tErrors = []
for Grid in Grids:
    option.setPricingEngine(FdBlackScholesBarrierEngine (
        process, maxG, Grid))
    uErrors.append(abs(option.NPV()/trueValue-1))
    option.setPricingEngine(FdBlackScholesBarrierEngine (
        process, Grid, maxG))
    tErrors.append(abs(option.NPV()/trueValue-1))

# <headingcell level=1>
# Print pricing errors of finite difference method for different grid sizes

# <codecell>
print("True (Analytic) Value = {:.6f}".format(trueValue))
print("{:>12}{:>12}{:>12}".format("TimeGrid", "AssetGrid", "% Error"))
for T, A, E in zip([maxG for i in Grids], Grids, uErrors):
    print("{:12}{:12}{:12.4%}".format(T, A, E))
for T, A, E in zip(Grids, [maxG for i in Grids], tErrors):
    print("{:12}{:12}{:12.4%}".format(T, A, E))


# <headingcell level=1>
# Plot pricing errors of finite difference method for different grid sizes

# <codecell>
#%matplotlib inline
plt.loglog(Grids, uErrors, 'r-', Grids, tErrors, 'b--')
plt.xlabel('No of Grid Points (Log Scale)')
plt.ylabel('Relative Error (Log Scale)')
plt.legend(['Asset Grid Points', 'Time Grid Points'])
plt.title('Increasing Asset or Time Grid Keeping the Other Grid at ' + str(maxG))
plt.show()
