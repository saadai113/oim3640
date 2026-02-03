computer_price=float(input('Enter product price'))

def calc_tax(price):
    tax_rate=0.0625
    tax=price*tax_rate
    print(f'The tax for a product which costs $ {price} if ${tax}')
    return tax


calc_tax(computer_price)
ram_price= 6000
mass_rate=0.0625
tax_computer=calc_tax(computer_price, mass_rate)
tax_ram=calc_tax(ram_price, mass_rate)

total_tax=tax_computer+ tax_ram
print(f'Total tax: ${total_tax}')