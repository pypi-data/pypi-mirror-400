################################################################################
# iRating calculator
#

import math

LN_2 = 0.693147180559945309417232121458176568
BR = 1600 / LN_2 # 2308.31206542

def chance(a, b, factor=BR):
    ea = math.exp(-a / factor)
    eb = math.exp(-b / factor)
    Q_a = (1 - ea) * eb
    Q_b = (1 - eb) * ea
    return Q_a / (Q_b + Q_a)

class IRatingResult():
    def __init__(self, name, iRating, started):
        self.name = name
        self.started = started
        self.initialIR = iRating
        self.calculatedIr = None

    def __str__(self):
        return "{} [{}] -> {:.0f} ({:+.0f})".format(self.name, self.initialIR, self.calculatedIr, self.calculatedIr-self.initialIR)
    
    def __repr__(self):
        return self.__str__()

class IRatingCalculator:

    def calculate(self, raceResults):
        nTotal = len(raceResults)
        nStarters = len([result for result in raceResults if result.started])
        nNonStarters = nTotal - nStarters

        expecteds = []
        sumExpectedStarted = 0
        sumExpectedNonStarted = 0
        for i in range(nTotal):
            c = -0.5
            for j in range(nTotal):
                c += chance(raceResults[i].initialIR, raceResults[j].initialIR)
            if raceResults[i].started:
                sumExpectedStarted += c
            else:
                sumExpectedNonStarted += c
            expecteds.append(c)

        changesStarters = []
        for i in range(nTotal):
            if not raceResults[i].started:
                changesStarters.append(0)
            else:
                pos = i+1
                factor = ((nTotal - nNonStarters / 2) / 2 - pos) / 100.
                changesStarters.append((nTotal - pos - expecteds[i] \
                        - factor) * 200. / nStarters)
        
        for i in range(nTotal):
            if raceResults[i].started:
                raceResults[i].calculatedIr = raceResults[i].initialIR + changesStarters[i]
            else:
                raceResults[i].calculatedIr = raceResults[i].initialIR + (-sum(changesStarters) / nNonStarters * expecteds[i] \
                    / (sumExpectedNonStarted / nNonStarters))
        return [i.calculatedIr for i in raceResults]
