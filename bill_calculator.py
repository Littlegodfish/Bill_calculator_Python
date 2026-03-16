# Required Input:
# 1) Number of ppl 2) Cost for each 3) Subtotal 4) Tax 5) Tip 6) Grand total 

# Calculation 
# 1) Tax/ Subtotal to get Tax percentage 2) Tip/Subtotal w/o tax to get Tip percentage 
# 3) Each person's cost + Tax and Tip percentage

# Output 
# 1) Each person's final cost 


def make_list(list_of_ppl):
    names_list = list_of_ppl.split()
    money_list = []
    for name in names_list:
           money_list.append(float(input("Initial Cost for " + name + " :")))
    return money_list, names_list

def tax_calculator(subtotal, tax):
    return (tax/subtotal)

def tip_calculator(tip, subtotal):
     return (tip/subtotal)

def final_cost_calculator(money_list, tax_percentage, tip_percentage, evenly_split_tip, even_tip):
    new_money_list = money_list.copy()
    for i in range(len(money_list)):
        new_money_list[i] += money_list[i] * tax_percentage
    if evenly_split_tip:
        for i in range(len(new_money_list)):
            new_money_list[i] += even_tip
    else:
        for i in range(len(new_money_list)):
            new_money_list[i] += money_list[i] * tip_percentage
    return new_money_list
def print_out(new_money_list, names_list):
    total = 0 
    for i in range(len(names_list)):
        print(names_list[i], " pays:", round(new_money_list[i],2))
        total += new_money_list[i]
    print("Grand Total: " + str(round(total, 2)))
def main():
    string_of_ppl = input("Everyone's names separated by space: ")
    money_list, names_list = make_list(string_of_ppl)
    number_of_ppl = len(names_list)
    subtotal = float(input("Subtotal before Tax and Tip: "))
    if round(sum(money_list), 2) != round(subtotal, 2):
        print("Warning: individual costs do not match subtotal.")
    tax = float(input("Tax Amount: "))
    tax_percentage = tax_calculator(subtotal, tax)
    choice = input("Split Tip evenly? (y/n): ")
    evenly_split_tip = choice.lower() == "y"
    tip = float(input("Tip Amount: "))
    even_tip = tip/number_of_ppl
    tip_percentage = tip_calculator(tip, subtotal)
    new_money_list = final_cost_calculator(money_list, tax_percentage, tip_percentage, evenly_split_tip, even_tip)
    print_out(new_money_list, names_list)


if __name__ == "__main__":
    main()