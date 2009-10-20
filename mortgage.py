"""Mortgage calculations"""

PROPERTY_TAXES=1.5
TAX_RATE=0.33
REPAIR_COST=2
INSURANCE=1000
UTILITIES=100

def calculate_monthly_cost(value,monthly_payment):
    costs=monthly_payment
    costs+=value*PROPERTY_TAXES/100/12.0
    costs+=(REPAIR_COST/100.0*value)/12.0
    costs+=INSURANCE
    costs+=UTILITIES
    return costs

def calculate_payment(principal,interest,years):
    monthly_interest=interest/100.0/12
    return principal * monthly_interest/(1-(1+monthly_interest) ** (-years*12))

if __name__=="__main__":
    import sys
    if len(sys.argv)!=5:
        print "mortgage.py <value> <%down> <rate> <years>"
        sys.exit(1)
    value,down,rate,years=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4])
    principal=value*(1-down/100.0)
    vals={"principal":principal,"down payment":down/100.0*value,"rate":rate,"years":years}
    mp=calculate_payment(principal,rate,years)
    vals["monthly payment"]=mp
    vals["total interest"]=mp*years*12
    vals["total cost"]=mp*years*12+principal
    mc=calculate_monthly_cost(value,mp)
    vals["monthly costs"]=mc
    for k,v in vals.items():
        print "%s: %0.2f"%(k,v)
