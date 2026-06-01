from legacy import fizzbuzz

def test_fizzbuzz():
    assert fizzbuzz(15) == "FizzBuzz"

def test_plain():
    assert fizzbuzz(7) == "7"

def test_fizz_six():
    assert fizzbuzz(6) == "Fizz"
