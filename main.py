from classes import *

def main():
    street_we = Street('w', 'e')
    street_ns = Street('n', 's')
    street_sn = Street('s', 'n')
    street_ew = Street('e', 'w')

    car = Car()
    street_we.add_car(car)


if __name__ == '__main__':
    main()