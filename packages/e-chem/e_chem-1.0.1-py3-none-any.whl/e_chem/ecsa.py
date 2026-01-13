import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

def ecsa(cvsList, potentialDownward: float, potentialUpward: float, scanRates: list[int], startAtCorner=False, linFit=True, allFit=True, logPlot=False):

    fig, (ax1, ax2) = plt.subplots(1, 2, sharex=False, sharey=False)
    
    fig.set_size_inches(10, 5)

    ecsaResultValues = []

    for cvs in cvsList:
        # plot CVs
        plt.subplot(1,2,1)
        for i, cv in enumerate(cvs):
            plt.plot(cv.volts, cv.amps*1000, label="{} mV/s".format(scanRates[i]))

        # plt.legend(bbox_to_anchor=(0.5, -0.05), ncol=4)
        

        ax1.set_xlabel("Potential [V]")
        ax1.set_ylabel("Current density [mA/cm²]")
        plt.title("a")

        # plot ECSAs
        plt.subplot(1,2,2)
        cvCount = len(cvs)
        currentsUpward = np.empty(cvCount)
        currentsDownward = np.empty(cvCount)
        # scanRates = np.linspace(10, 50, cvCount)

        for i in range(cvCount):
            if startAtCorner:
                cvUpward = cvs[i].beforeRightVertex()
                currentsUpward[i] = cvUpward.getCurrentAt(potentialUpward)

                cvDownward = cvs[i].afterRightVertex()
                currentsDownward[i] = cvDownward.getCurrentAt(potentialDownward)

            else:
                cvUpward = cvs[i].afterRightVertex().afterLeftVertex()
                currentsUpward[i] = cvUpward.getCurrentAt(potentialUpward)

                cvDownward = cvs[i].afterRightVertex().beforeLeftVertex()
                currentsDownward[i] = cvDownward.getCurrentAt(potentialDownward)
            
        # raw data
        plt.scatter(scanRates, currentsDownward*1000, label="anodic (?) scan")
        plt.scatter(scanRates, currentsUpward*1000, label="cathodic (?) scan")

        # linear fit
        if linFit:
            fitCoef1 = np.polyfit(scanRates, currentsUpward, 1)
            fitFunction1 = np.poly1d(fitCoef1)
            plt.plot(scanRates, fitFunction1(scanRates)*1000, '--', label="linear: %.2f µF" % (fitCoef1[0] * 1e6))

            fitCoef2 = np.polyfit(scanRates, currentsDownward, 1)
            fitFunction2 = np.poly1d(fitCoef2)
            plt.plot(scanRates, fitFunction2(scanRates)*1000, '--', label="linear: %.2f µF" % (fitCoef2[0] * 1e6))

            # percentage of non-linearity
            deltaI = fitFunction1(scanRates) - currentsUpward
            deltaImax = np.max(deltaI)
            nlMax = np.abs(deltaImax) / np.abs(np.max(currentsUpward) - np.min(currentsUpward))*100
            print("nlMax %.2f" % nlMax)


        # allometric regression
        if allFit:
            def allometric(x, a, b):
                return b*pow(x,a)
            
            scanRatesRange = np.linspace(scanRates[0], scanRates[-1], 50)

            allometricParamUpward, allometricParamUpwardCov = curve_fit(allometric, scanRates, currentsUpward)
            aUp, bUp = allometricParamUpward
            plt.plot(scanRatesRange, allometric(scanRatesRange, aUp, bUp)*1000, '--', label="allometric: %.2f µF, a=%.2f" % (bUp * 1e6, aUp))

            allometricParamDownward, allometricParamDownwardCov = curve_fit(allometric, scanRates, currentsDownward)
            aDown, bDown = allometricParamDownward
            plt.plot(scanRatesRange, allometric(scanRatesRange, aDown, bDown)*1000, '--', label="allometric: %.2f µF, a=%.2f" % (bDown * 1e6, aDown))

            # if logPlot:
            #     plt.loglog(scanRates, fitFunction2(scanRates), '--', label="%.2f µF" % (fitCoef2[0] * 1e6))
            # else:
            #     plt.plot(scanRates, fitFunction2(scanRates), '--', label="linear: %.2f µF" % (fitCoef2[0] * 1e6))

        # ecsaResultValues.append(np.abs(fitCoef1[0]))
        # ecsaResultValues.append(np.abs(fitCoef2[0]))

    # ecsaMean = np.array(ecsaResultValues).mean()
    # ecsaStd = np.array(ecsaResultValues).std()

    ax2.set_xlabel("Scan rate [mV/s]")
    ax2.set_ylabel("Current density at constant potential [mA/cm²]")
    plt.legend()
    # plt.title("ECSA: %.2f ± %.2f µF" % (ecsaMean*1e6, ecsaStd*1e6))
    plt.title("b")

    plt.show()
