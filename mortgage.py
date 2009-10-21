"""Mortgage and Home Ownership calculations

This program is my attempt to understand and calculate the cost of owning a home.

Author: Nikolaj Baer
License: MIT License
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

def calculate_monthly_cost(value,monthly_payment,prop_taxes,repair_cost,insurance,utilities):
    costs=monthly_payment
    costs+=value*prop_taxes/100/12.0
    costs+=(repair_cost/100.0*value)/12.0
    costs+=insurance
    costs+=utilities
    return costs

def calculate_payment(principal,interest,years):
    monthly_interest=interest/100.0/12
    return principal * monthly_interest/(1-(1+monthly_interest) ** (-years*12))

def calculate_tax_savings(agi,writeoffs,filing_status):
    def get_tax(i,fs):
        tr=0.0
        for r in FED_TAX_TABLE:
            if r[fs][0]<=i and r[fs][1] >= i:
                tr=r[0]
                break
        extra=0.0
        for r in CA_TAX_TABLE[filing_status-1]:
             if r[2]<=i and r[3] >= i:
                tr+=r[1]
                extra+=r[0]
        print "got tax rate of ",tr,"% plus extra ",extra
        return ((tr/100.0)*i) + extra
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
    parser.add_option("--repair-cost",dest="repair",help="Annual maintenace costs as percentage of home value per year",default="2")
    parser.add_option("--insurance",dest="insurance",help="Annual cost of homeowners insurance in dollars",default="2000")
    parser.add_option("-u","--utilites",dest="utilities",help="Monthly average cost of utilities",default="150")
    parser.add_option("--filing-status",dest="filing_status",help="Tax filing status. 1=single, 2=joint,3=separate,4=head of household.",default="2")
    return parser

def do_the_math(value,agi,options):
    # Start with monthly payment  
    down,rate,years=float(options.down),float(options.rate),float(options.years)
    principal=value*(1-down/100.0)
    vals={"principal":principal,"down payment":down/100.0*value,"rate":rate,"years":years}
    mp=calculate_payment(principal,rate,years)

    # Then monthly costs
    vals["monthly payment"]=mp
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
    vals["extra monthly income"]=calculate_tax_savings(agi,vals["total interest"]/years,int(options.filing_status))

    vals["monthly costs with new income"]=mc-vals["extra monthly income"] 
    # return the values we calculated
    return vals

if __name__=="__main__":
    parser=build_optparser()
    (options,args)=parser.parse_args()
    vals=do_the_math(float(args[0]),float(args[1]),options) 
    print "\n","*"*50
    for k,v in vals.items():
        print "%s: %0.2f"%(k,v)


