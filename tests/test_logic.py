from ma_consumer import calculate_moving_average

def test_calculate_moving_average():
    prices = [100, 101, 99, 102, 98]
    assert calculate_moving_average(prices) == 100.0