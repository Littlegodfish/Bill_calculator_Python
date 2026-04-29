
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

def tax_tip_calculation(tax, tip, subtotal, money_list, people_list, evenly_split_tip, number_of_ppl):
    new_money_list = money_list.copy()
    details_list = []
    tax_percentage = (tax / subtotal)
    tip_percentage = (tip / subtotal)

    for i in range(len(money_list)):
        base_amount = money_list[i]
        tax_amount = base_amount * tax_percentage

        if evenly_split_tip:
            tip_amount = tip / number_of_ppl
        else:
            tip_amount = base_amount * tip_percentage

        final_amount = base_amount + tax_amount + tip_amount
        new_money_list[i] = final_amount

        details_list.append(
            {
                "name": people_list[i],
                "base": round(base_amount, 2),
                "tax": round(tax_amount, 2),
                "tip": round(tip_amount, 2),
                "final": round(final_amount, 2),
            }
        )

    return new_money_list, details_list

def print_out(new_money_list, people_list):
    total = 0 
    for i in range(len(people_list)):
        print(people_list[i], " pays:", round(new_money_list[i],2))
        total += new_money_list[i]
    print("Grand Total: " + str(round(total, 2)))


def print_details(details_list):
    print("Breakdown:")
    print(details_list)

def main():
    people_string, subtotal, tax, tip, evenly_split_tip = collect_input()
    money_list, people_list, number_of_ppl = make_list(people_string)
    subtotal_checker(subtotal, money_list)
    new_money_list, details_list = tax_tip_calculation(
        tax, tip, subtotal, money_list, people_list, evenly_split_tip, number_of_ppl
    )
    print_out(new_money_list, people_list)
    print_details(details_list)


if __name__ == "__main__":
    main()