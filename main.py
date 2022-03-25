from classes import *

def main():
    street_we = Road('w', 'e')
    street_ns = Road('n', 's')
    street_sn = Road('s', 'n')
    street_ew = Road('e', 'w')

    car = Car()
    street_we.add_car(car)


if __name__ == '__main__':
    main()