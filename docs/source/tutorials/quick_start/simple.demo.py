from potc import transobj

if __name__ == '__main__':
    print("transobj(1):", transobj(1))
    print("transobj([1, 2, 'sdkfj\u0123']):",
          transobj([1, 2, 'sdkfj\u0123']))

    print('empty set:', transobj(set()))
    print('1-lengthened tuple:', transobj((1,)))
