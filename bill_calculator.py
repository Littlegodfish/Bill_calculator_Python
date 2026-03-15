# Required Input:
# 1) Number of ppl 2) Cost for each 3) Subtotal 4) Tax 5) Tip 6) Grand total 

# Calculation 
# 1) Tax/ Subtotal to get tax percetage 2) Tip/Subtotal w/o Tax to get Tip percentage 
# 3) Each person's cost + Tax and Tip percentage

# Output 
# 1) Each person's final cost 


def make_list(list_of_ppl):
    names_list = list_of_ppl.split()
    Money_list = []
    for name in names_list:
           Money_list.append(float(input("Initial Cost for " + name + " :")))
    return Money_list, names_list

def Tax_calculater(Subtotal, Tax):
    return (Tax/Subtotal)

def Tip_calculater(Tip, Subtotal):
     return (Tip/Subtotal)

def final_cost_calculator(Money_list, Tax_percentage, Tip_percentage, Evenly_split_tip, Even_Tip):
    New_money_list = Money_list.copy()
    for i in range(len(Money_list)):
        New_money_list[i] += Money_list[i] * Tax_percentage
    if Evenly_split_tip:
        for i in range(len(New_money_list)):
            New_money_list[i] += Even_Tip
    else:
        for i in range(len(New_money_list)):
            New_money_list[i] += Money_list[i] * Tip_percentage
    return New_money_list
def print_out(New_money_list, names_list):
    sum = 0 
    for i in range(len(names_list)):
        print(names_list[i], " pays:", round(New_money_list[i],2))
        sum += round(New_money_list[i],2)
    print("Grand Total: " + str(round(sum, 2)))
def main():
    string_of_ppl = str(input("Everyone's names separated by space: "))
    Money_list, names_list =  make_list(string_of_ppl)
    number_of_ppl = len(names_list)
    Subtotal = float(input("Subtotal before Tax and Tip: "))
    Tax = float(input("Tax Amount: "))
    Tax_percentage = Tax_calculater(Subtotal, Tax)
    choice = input("Split tip evenly? (y/n): ")
    Evenly_split_tip = choice.lower() == "y"
    Tip = float(input("Tip Amount: "))
    Even_Tip = Tip/number_of_ppl
    Tip_percentage = Tip_calculater(Tip, Subtotal)
    New_money_list = final_cost_calculator(Money_list, Tax_percentage, Tip_percentage, Evenly_split_tip, Even_Tip)
    print(print_out(New_money_list, names_list))


if __name__ == "__main__":
    main()