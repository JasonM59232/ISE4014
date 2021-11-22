"""import the library source"""
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import cplex

"""library location"""
# from site import USER_BASE
# from site import USER_SITE
# USER_SITE = root + "\lib\site-packages"
# USER_BASE = root + "\lib\scripts"

"""create global variables"""
# Global variables
root = os.path.dirname(os.path.realpath(__file__))
Instancedir = root + "\Data"
Data1dir = Instancedir + "\Data1.csv"
Data2dir = Instancedir + "\Data2.csv"
DataHdir = Instancedir + "\DataHeavyTraffic.csv"
Distdir = Instancedir + "\Dist.csv"

# pandas parameters
# display the whole pandas dataframe
# if you want to view the full data, enable this function
pd.set_option("display.max_rows", None)
pd.set_option('display.max_columns', None)

# OR parameters
FlightData = []
DistData = []

RunwaySep_ArrArr = [[82, 131, 196], [69, 69, 157], [60, 60, 96]]
RunwaySep_ArrDep = [[75, 75, 75], [75, 75, 75], [75, 75, 75]]
RunwaySep_DepArr = [[60, 60, 60], [60, 60, 60], [60, 60, 60]]
RunwaySep_DepDep = [[60, 60, 120], [60, 60, 120], [60, 60, 90]]

MaxRange = 10e5
BigM = 10e10
# Cat-A, Cat-B, Cat-C = LSF
# Cat-D, Cat-E = MSF
# Cat-F = SSF

# cplex parameters




class RunwaySchedulingSequencingProblem():
    """a class of gate assignment problem"""

    def InstanceRead(self, InstData):
        # read flight data and dist data
        FlightData = pd.read_csv(InstData)

        #########################################################################################################
        # --------------- Task here! Your input --------------
        # Refine/filter your dataset according to the question requirement.
        # Otherwise, full data will be loaded for analysis.

        #########################################################################################################

        # output the instance data
        print("Flight data")
        print("=" * 100)
        print(FlightData)
        print("=" * 100)
        print()

        os.system("pause")
        # return filtered data
        return FlightData

    def ASSPopt(self, FlightData):
        #########################################################################################################
        # --------------- Task here! Your input --------------
        # Please code your problem formulation here.

        # define length of set I
        NumFlight = len(FlightData)

        print("The number of flights: ", NumFlight)

        # extract the timestamp
        TimeStamp_i = [datetime.strptime(
            date, '%d/%m/%Y %H:%M') for date in FlightData["actual_runway_arrival"]]

        # round down to the nearest hour minus one hour for the first event
        TimeRoundDown = TimeStamp_i[0]
        TimeRoundDown = TimeRoundDown.replace(
            second=0, microsecond=0, minute=0) - timedelta(hours=1)
        print("The initial timestamp of the problem")
        print(TimeRoundDown)

        # target landing time in int/real number format
        T_i = [(x - TimeRoundDown).seconds for x in TimeStamp_i]

        # transfer recat to cat
        ReCat_i = FlightData["FlightSize"]
        Cat_i = ReCat_i.copy()
        for i in range(NumFlight):
            if ReCat_i[i] == "CAT-A" or ReCat_i[i] == "CAT-B" or ReCat_i[i] == "CAT-C":
                Cat_i[i] = "LSF"
            if ReCat_i[i] == "CAT-D" or ReCat_i[i] == "CAT-E":
                Cat_i[i] = "MSF"
            if ReCat_i[i] == "CAT-F":
                Cat_i[i] = "SSF"

      # define separation matrix
        S_ji = [["" for j in range(NumFlight)] for i in range(NumFlight)]
        for j in range(NumFlight):
            for i in range(NumFlight):
                if i == j:
                    S_ji[j][i] = BigM
                else:
                    if Cat_i[j] == "SSF" and Cat_i[i] == "SSF":
                        S_ji[j][i] = RunwaySep_ArrArr[0][0]
                    if Cat_i[j] == "SSF" and Cat_i[i] == "MSF":
                        S_ji[j][i] = RunwaySep_ArrArr[1][0]
                    if Cat_i[j] == "SSF" and Cat_i[i] == "LSF":
                        S_ji[j][i] = RunwaySep_ArrArr[2][0]
                    if Cat_i[j] == "MSF" and Cat_i[i] == "SSF":
                        S_ji[j][i] = RunwaySep_ArrArr[0][1]
                    if Cat_i[j] == "MSF" and Cat_i[i] == "MSF":
                        S_ji[j][i] = RunwaySep_ArrArr[1][1]
                    if Cat_i[j] == "MSF" and Cat_i[i] == "LSF":
                        S_ji[j][i] = RunwaySep_ArrArr[2][1]
                    if Cat_i[j] == "LSF" and Cat_i[i] == "SSF":
                        S_ji[j][i] = RunwaySep_ArrArr[0][2]
                    if Cat_i[j] == "LSF" and Cat_i[i] == "MSF":
                        S_ji[j][i] = RunwaySep_ArrArr[1][2]
                    if Cat_i[j] == "LSF" and Cat_i[i] == "LSF":
                        S_ji[j][i] = RunwaySep_ArrArr[2][2]

        print()
        print("The runway separation time")
        for j in range(NumFlight):
            print(S_ji[j])

        print()
        print("The target landing time")
        for i in range(NumFlight):
            print("Flight", i, ":", T_i[i])

        print()
        print("The flight size")
        for i in range(NumFlight):
            print("Flight", i, ":", Cat_i[i])

        print("//problem formulation start//")
        os.system("pause")

        # --------------- Task here! Your input --------------
        # initialise the datetime
        starttime = datetime.now()
        currtime = datetime.now()

        # initialise CPLEX environment
        cpx = cplex.Cplex()

        # set primal method only
        cpx.parameters.lpmethod.set(cpx.parameters.lpmethod.values.primal)

        # set CPU time (set as 5 mins for testing)
        # disable if you wish to get global optimum
        cpx.parameters.timelimit.set(300)

        # set optimality gap
        #cpx.parameters.mip.tolerances.mipgap.set(float(0.0137))

        # set objective function target
        # minimisation problem:                                                     cpx.objective.sense.minimize
        # maximiastion problem:                                                     cpx.objective.sense.maximize
        cpx.objective.set_sense(cpx.objective.sense.minimize)

        # set variables
        NumRun = 2
        x_ir = [["" for r in range(NumRun)] for i in range(NumFlight)]
        t_i = ["" for i in range(NumFlight)]
        alpha_i = ["" for i in range(NumFlight)]
        beta_i = ["" for i in range(NumFlight)]
        y_jir = [[["" for r in range(NumRun)] for i in range(NumFlight)] for j in range(NumFlight)]

        # define variables range and domain
        ###your input###
        for i in range(NumFlight):
            
            var_name = "t_" + str(i)
            t_i[i] = cpx.variables.get_num()
            cpx.variables.add(lb=[0.0],ub=[BigM], types=["C"], names=[var_name])

            var_name = "alpha_" + str(i)
            alpha_i[i] = cpx.variables.get_num()
            cpx.variables.add(obj=[1.0/NumFlight],lb=[0.0],ub=[BigM], types=["C"], names=[var_name])

            var_name = "beta_" + str(i)
            beta_i[i] = cpx.variables.get_num()
            cpx.variables.add(obj=[1.0/NumFlight],lb=[0.0],ub=[BigM], types=["C"], names=[var_name])
           
            
            for r in range(NumRun):
                var_name = "x_" + str(i)+str(r)
                x_ir[i][r] = cpx.variables.get_num()
                cpx.variables.add(lb=[0.0],ub=[1.0], types=["B"], names=[var_name])
                for j in range(NumFlight):
                    var_name = "Y_" + str(j) + str (i) + str(r)
                    y_jir[j][i][r] = cpx.variables.get_num()
                    cpx.variables.add(lb=[0.0],ub=[1.0], types=["B"], names=[var_name])


        # separation time constraints 
        ###your input###
        for r in range(NumRun):
            if r=r
            for i in range(NumFlight): 
                for j in range(NumFlight):#0,1,2
                    if (j != i) :  #0,1,2
                        C1_var = []
                        C1_coef = []
                        C1_var.append(t_i[i])
                        C1_coef.append(1)
                        C1_var.append(t_i[j])
                        C1_coef.append(-1)
                        C1_var.append(y_ji[j][i][r])
                        C1_coef.append(-1*BigM)
                        cpx.linear_constraints.add(
                        lin_expr=[cplex.SparsePair(C1_var,C1_coef)], senses="G", rhs=[S_ji[j][i]-1*BigM])

        # sequencing constraints
        ###your input###
        for i in range(NumFlight): 
            for j in range(NumFlight):
                if (j != i) :
                    C2_var = []
                    C2_coef = []
                    C2_var.append(y_jir[i][j][r])
                    C2_coef.append(1)
                    C2_var.append(y_jir[j][i][r])
                    C2_coef.append(1)
                    cpx.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(C2_var,C2_coef)], senses="L", rhs=[1])
       
        # earlier arrival penalty cost
        ###your input###
        for i in range(NumFlight): 
            C3_var = []
            C3_coef = []
            C3_var.append(alpha_i[i])
            C3_coef.append(1)
            C3_var.append(t_i[i])
            C3_coef.append(-1)
            cpx.linear_constraints.add(lin_expr=[cplex.SparsePair(C3_var,C3_coef)], senses="G", rhs=[-1*T_i[i]])

        
        # late arrival penalty cost
        ###your input###
        for i in range(NumFlight): 
            C4_var = []
            C4_coef = []
            C4_var.append(beta_i[i])
            C4_coef.append(1)
            C4_var.append(t_i[i])
            C4_coef.append(1)
            cpx.linear_constraints.add(
            lin_expr=[cplex.SparsePair(C4_var,C4_coef)], senses="G", rhs=[T_i[i]])

        #xir yij
        ###your input###


        # sequencing constraints
        ###your input###

    
        #runway assignment
        ###your input###


        # output formulation
        cpx.write(root + "\\Lab2Q3-1a_method_1_formulation.lp")

        # solve the model
        cpx.solve()
        solution = cpx.solution
        ObjVal = sys.maxsize

        currtime = datetime.now()
        lapsetime = datetime.now()
        Runtime = lapsetime - starttime

        print("The computation time: ", Runtime)
        # Solution status
        # if you want to check if the problem is in global optimal condition:       solution.status.MIP_optimal
        # if you want to check if the problem is feasible:                          solution.status.MIP_feasible
        # if you want to check if the problem is infeasible:                        solution.status.MIP_infeasible
        # if you want to check if the problem is unbounded:                         solution.status.unbounded

        if not (solution.get_status() == solution.status.unbounded or solution.get_status() == solution.status.MIP_infeasible):
            print("Global optimum reached.")
            ObjVal = solution.get_objective_value()
            print("Optimal value: ", ObjVal)  # show the objective value

            for i in range(NumFlight):
                for r in range(NumRun):
                    sol_x_ir = solution.get_values(x_ir[i][r])
                    if sol_x_ir > 1e-03:
                        print("Flight", str(i),"is assigned to land on runway",str(r))

            for i in range(NumFlight):
                sol_t = solution.get_values(t_i[i])
                if sol_t > 1e-03:
                    print("The assigned landing time of flight",str(i),"(",str(ReCat_i[i]),")", "is", round(sol_t))

                sol_alpha = solution.get_values(alpha_i[i])
                sol_beta = solution.get_values(beta_i[i])            
                if sol_alpha > 1e-03:
                    print("[Flight",
                        str(i), "arrive earlier with the time(cost) unit of", round(sol_alpha),"]")
                if sol_beta > 0:
                    print("[Flight",
                        str(i), "is delayed with the time(cost) unit of", round(sol_beta),"]")
                print()


        

        if solution.get_status() == solution.status.unbounded:
            print("The problem is unbounded.")

        if solution.get_status() == solution.status.MIP_infeasible:
            print("The problem is infeasible.")

        # clean memory
        # cpx.cleanup()

        #########################################################################################################


def main():


    """main def"""
    # create a new class for GAP
    ASSP = RunwaySchedulingSequencingProblem()

    # load the flight data1 and dist map
    Flt = ASSP.InstanceRead(DataHdir)

    # solve the problem with the filtered dataset
    ASSP.ASSPopt(Flt)


    os.system("pause")


# Example
if __name__ == '__main__':
    # call main function
    main()
