from date_fuzz import find_dates


def test_find():
    text = "A thing happened on Jan 1st 2012 and the next morning at 09:15 and also jan 15th at 12am in 2018."
    found_dates = find_dates(text)
    expected_out = [("2012-01-01", 4), ("2012-01-02 09:15", 9), ("2018-01-15 12:00", 15)]
    print("\nText :", text)
    print("Found:", found_dates)
    print("Expct:", expected_out)

    assert found_dates == expected_out

    text = "Event A occured (07/11/2025, around 21:00-22:00). 2014-12-02"
    found_dates = find_dates(text)
    expected_out = [("2025-11-07 21:00", 3), ("2014-12-02 21:00", 6)]
    print("\nText :", text)
    print("Found:", found_dates)
    print("Expct:", expected_out)

    assert found_dates == expected_out
