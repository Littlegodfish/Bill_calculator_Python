
def collect_input():
    people_string = input("Everyone's names separated by space: ")
    subtotal = float(input("Subtotal before Tax and Tip: "))
    tax = float(input("Tax Amount: "))
    tip = float(input("Tip Amount: "))
    choice = input("Split Tip evenly? (y/n): ")
    evenly_split_tip = choice.lower() == "y" 
    return people_string, subtotal, tax, tip, evenly_split_tip

def make_list(people_string):
    people_list = people_string.split()
    money_list = []
    for name in people_list:
           money_list.append(float(input("Initial Cost for " + name + " :")))
    return money_list, people_list, len(people_list)

def subtotal_checker(subtotal, money_list):
    if round(sum(money_list), 2) != round(subtotal, 2):
        print(round(sum(money_list), 2))
        print("Warning: Sum of each person's cost does not match the subtotal")

def tax_tip_calculation(tax, tip, subtotal, money_list, evenly_split_tip, number_of_ppl):
    new_money_list = money_list.copy()
    tax_percentage = (tax/subtotal)
    tip_percentage = (tip/subtotal)
    for i in range(len(money_list)):
        new_money_list[i] += money_list[i] * tax_percentage

    if evenly_split_tip:
        even_tip = (tip / number_of_ppl)
        for i in range(len(money_list)):
            new_money_list[i] += even_tip
    else: 
        for i in range(len(money_list)):
            new_money_list[i] += money_list[i] * tip_percentage
    return new_money_list

def print_out(new_money_list, people_list):
    total = 0 
    for i in range(len(people_list)):
        print(people_list[i], " pays:", round(new_money_list[i],2))
        total += new_money_list[i]
    print("Grand Total: " + str(round(total, 2)))

def main():
    people_string, subtotal, tax, tip, evenly_split_tip = collect_input()
    money_list, people_list, number_of_ppl = make_list(people_string)
    subtotal_checker(subtotal, money_list)
    new_money_list = tax_tip_calculation(tax, tip, subtotal, money_list, evenly_split_tip, number_of_ppl)
    print_out(new_money_list, people_list)


if __name__ == "__main__":
    main()