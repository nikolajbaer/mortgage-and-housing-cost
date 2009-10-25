"""Mortgage and Home Ownership calculations

This program is my attempt to understand and calculate the cost of owning a home. I skipped on the spreadsheets because i want to build it myself in the way that i usually comprehend things.. through code.

Author: Nikolaj Baer
License: MIT License

References;
http://www.hughchou.org/calc/formula.html
http://en.wikipedia.org/wiki/Amortization_calculator
http://en.wikipedia.org/wiki/Amortization_(business)
http://en.wikipedia.org/wiki/Tax_bracket#Tax_brackets_in_the_United_States
http://www.ftb.ca.gov/forms/2008_California_Tax_Rates_and_Exemptions.shtml
"""

FED_TAX_TABLE=(
    # rate, (single min,max),(joint min,max), (separate min,max), (head min,max)
    (10,(0,8,350),(0,16700   ),(0,8350),(0,11950)),
    (15,(8351,33950),(16701,67900),(8351,33950),(11951,45500)),
    (25,(33951,82250),(67901,137050),(33951,68525),(45501,117450)),
    (28,(82251,171550),(137051,208850),(68525,104425),(117451,190200)),
    (33,(171551,372950),(208851,372950),(104426,186475),(190201,372950)),
    (35,(372951,10**10),(372951,10**10),(186476,10**10),(372951,10**10)), # assuming no weimar republic
)

CA_TAX_TABLE=(
    # single
    (   (0.00,1.00,0.00,7168.00),
        (71.68,2.00,7168.00,16994.00),
        (268.20,4.00,16994.00,26821.00),
        (661.28,6.00,26821.00,37233.00),
        (1286.00,8.00,37233.00,47055.00),
        (2071.76,9.30,47055.00,1000000000.00), ),
    # joint
    (
        (0.00,1.00,0.00,14336.00),
        (143.36,2.00,14336.00,33988.00),
        (536.40,4.00,33988.00,53642.00),
        (1322.56,6.00,53642.00,74466.00),
        (2572.00,8.00,74466.00,94110.00),
        (4143.52,9.30,94110.00,1000000000.00), ),
    # separate (same as single in CA)
    (   (0.00,1.00,0.00,7168.00),
        (71.68,2.00,7168.00,16994.00),
        (268.20,4.00,16994.00,26821.00),
        (661.28,6.00,26821.00,37233.00),
        (1286.00,8.00,37233.00,47055.00),
        (2071.76,9.30,47055.00,1000000000.00), ),
    # head of household
    (
        (0.00,1.00,0.00,14345.00),
        (143.45,2.00,14345.00,33989.00),
        (536.33,4.00,33989.00,43814.00),
        (929.33,6.00,43814.00,54225.00),
        (1553.99,8.00,54225.00,64050.00),
        (2339.99,9.30,64050.00,1000000000.00), ),
)

FICA_RATE="7.65"
FICA_MAX="6621.60"

# average yearly inflation from BLS in USA from 1998-2009
USA_INFLATION_RATES=[3.85,2.85,3.24,3.39,2.68,2.27,1.59,2.83,3.38,2.19,1.55]
USA_INFLATION_RATE=sum(USA_INFLATION_RATES)/len(USA_INFLATION_RATES)

def calculate_monthly_cost(value,monthly_payment,prop_taxes,repair_cost,insurance,utilities):
    costs=monthly_payment
    costs+=value*prop_taxes/100/12.0
    costs+=(repair_cost/100.0*value)/12.0
    costs+=insurance
    costs+=utilities
    return costs

def amortize(balance,monthly_interest,monthly_payment):
    interest_paid=balance*monthly_interest  
    equity_earned=monthly_payment-interest_paid
    new_balance=balance-equity_earned
    return new_balance,interest_paid,equity_earned

def generate_pay_schedule(principal,interest,years):
    monthly_interest=interest/100.0/12
    monthly_payment=principal * monthly_interest/(1-(1+monthly_interest) ** (-years*12))
    balances,interest_paid,equity_earned=[],[],[]
    # smart people do this in formulas, but i kindof like 
    # the iterative one as it gives me more of a sense of how it compounds 
    b,i,q=principal,0.0,0.0
    for y in range(years*12):
        b,i,q=amortize(b,monthly_interest,monthly_payment) 
        balances.append(b)
        interest_paid.append(i)
        equity_earned.append(q)
    return balances,interest_paid,equity_earned,monthly_payment

def get_tax(i,fs):
    tr=0.0
    for r in FED_TAX_TABLE:
        if r[fs][0]<=i and r[fs][1] >= i:
            tr=r[0]
            break
    extra=0.0
    for r in CA_TAX_TABLE[fs-1]:
         if r[2]<=i and r[3] >= i:
            tr+=r[1]
            extra+=r[0]
    print "got tax rate of ",tr,"% plus extra ",extra
    return ((tr/100.0)*i) + extra
    
def calculate_tax_savings(agi,writeoffs,filing_status):
    taxes=get_tax(agi,filing_status)
    print "initial taxes ",taxes
    n_agi=(agi-writeoffs)
    adj_taxes=get_tax(n_agi,filing_status)
    print "adjusted taxes ",adj_taxes
    return (taxes-adj_taxes)/12

def build_optparser():
    # Build options
    from optparse import OptionParser
    parser=OptionParser(usage="usage: mortgage.py <homevalue> <gross income> [options]")
    parser.add_option("-d","--down",dest="down",help="Down Payment as percent of house value (e.g. 20 for 20%)",default="20")
    parser.add_option("-r","--rate",dest="rate",help="Interest rate of mortgage as percent (e.g. 5 for 5%)",default="5")
    parser.add_option("-y","--years",dest="years",help="Years of mortgage",default="30")
    parser.add_option("-p","--property-tax-rate",dest="prop_taxes",help="Property tax as percent of home value",default="1.5")
    parser.add_option("--repair-cost",dest="repair",help="Annual maintenace costs as percentage of home value (including equity growth) per year",default="2")
    parser.add_option("--insurance",dest="insurance",help="Annual cost of homeowners insurance in dollars",default="2000")
    parser.add_option("-u","--utilites",dest="utilities",help="Monthly average cost of utilities",default="150")
    parser.add_option("--filing-status",dest="filing_status",help="Tax filing status. 1=single, 2=joint,3=separate,4=head of household.",default="2")
    parser.add_option("--equity-growth",dest="equity_growth",help="Annual percentage increase in value of house",default="1")
    parser.add_option("--inflation-rate",dest="inflation_rate",help="Rate of inflation as it effects utilities and insurance",default="%0.2f"%USA_INFLATION_RATE)
    parser.add_option("--salary-growth",dest="salary_growth",help="Rate of salary growth in percent",default="3")
    parser.add_option("--medical-insurance",dest="med_insurance",help="monthly cost of medical insurance",default="150")

    return parser

def do_the_math(value,income,options):
    # Start with monthly payment, and payments over time
    down,rate,years=float(options.down),float(options.rate),float(options.years)
    principal=value*(1-down/100.0)
    vals={"principal":principal,"down payment":down/100.0*value,"rate":rate,"years":years}
    data={}
    # Here I calculate the equity growth over time, as well as the monthly payment
    balances,interest_paid,equity_earned,mp=generate_pay_schedule(principal,rate,years)
    # store these lists of numbers so i can graph stuff
    data["balances"]=balances
    data["interest paid"]=interest_paid
    data["equity earned"]=equity_earned
    data["monthly payment"]=[mp]*int(years)*12

    interest_writeoff=[]
    monthly_income=[]
    stated_income=[]
    income_over_time=income
    for y in range(years):
        income_over_time*=1.0+(float(options.salary_growth)/100.0)
        writeoff=sum(interest_paid[y*12:(y+1)*12])
        agi=income_over_time-writeoff
        income_tax=get_tax(agi,int(options.filing_status))
        monthly_income += [(income_over_time-income_tax)/12.0]*12
        stated_income +=[income_over_time/12.0]*12
        interest_writeoff=[writeoff/12.0]*12

    data["monthly_income"]=monthly_income
    data["interest_writeoff"]=interest_writeoff
    data["stated income"]=stated_income
    vals["monthly payment"]=mp

    # Then monthly costs
    vals["total cost"]=mp*years*12
    vals["total interest"]=(mp*years*12)-principal
    mc=calculate_monthly_cost(  value,
                                mp,
                                float(options.prop_taxes),
                                float(options.repair),
                                float(options.insurance),
                                float(options.utilities) )

    vals["monthly costs"]=mc

    # Figure out extra income from writeoffs
    vals["extra monthly income"]=calculate_tax_savings(income,vals["total interest"]/years,int(options.filing_status))

    vals["monthly costs with new income"]=mc-vals["extra monthly income"] 
    # return the values we calculated
    return vals,data

if __name__=="__main__":
    parser=build_optparser()
    (options,args)=parser.parse_args()
    vals,data=do_the_math(float(args[0]),float(args[1]),options) 
    print "\n","*"*50
    for k,v in vals.items():
        if type(v)==float:
            print "%s: %0.2f"%(k,v)
            
    print "*"*100,"\nPayment Schedule\n","*"*100 
    for k,v in data.items():
        print k
        print ",".join(["%.2f"%i for i in v[:5]]),"...",",".join(["%.2f"%i for i in v[-5:]])
 

