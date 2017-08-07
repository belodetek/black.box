from nose.tools import ok_, eq_, assert_is_not_none
from mock import patch
from uuid import uuid4

from bitcoin import (get_last_payment_date, get_last_payment_amount,
                     get_daily_amount, check_active_bitcoin_payment)


@patch('bitcoin.get_last_payment_date', return_value='2017-06-21T00:00:00Z')
@patch('bitcoin.get_last_payment_amount', return_value=float(1247000.0))
@patch('bitcoin.get_daily_amount', return_value=float(17861.0))
def test_check_active_bitcoin_payment_ok(mock_date, mock_amount, mock_daily_amount):
    result = check_active_bitcoin_payment(guid=uuid4().get_hex())
    assert_is_not_none(result)
    eq_(result, True)


@patch('bitcoin.get_last_payment_date', return_value='2017-06-21T00:00:00Z')
@patch('bitcoin.get_last_payment_amount', return_value=float(1000.0))
@patch('bitcoin.get_daily_amount', return_value=float(17861.0))
def test_check_active_bitcoin_payment_expired(mock_date, mock_amount, mock_daily_amount):
    result = check_active_bitcoin_payment(guid=uuid4().get_hex())
    assert_is_not_none(result)
    eq_(result, False)
