from nose.tools import ok_, eq_, assert_is_not_none
from mock import patch
from uuid import uuid4

from paypal import (check_active_paypal_subscription,
                    get_paypal_billing_agreement,
                    get_paypal_billing_agreement_id_for_guid)


@patch('paypal.get_paypal_billing_agreement_id_for_guid', return_value='I-EJWG5K0RPNJP')
@patch('paypal.get_paypal_billing_agreement', return_value='{"agreement_state": "active"}')
def test_check_active_paypal_subscription_with_valid_guid_returns_active(mock_baid, mock_result):
    result = check_active_paypal_subscription(guid=uuid4().get_hex())
    assert_is_not_none(result)
    eq_(result, 'I-EJWG5K0RPNJP')


@patch('paypal.get_paypal_billing_agreement_id_for_guid', return_value='I-OSKQBX1CWVSJ')
@patch('paypal.get_paypal_billing_agreement', return_value='{"agreement_state": "active"}')
def test_check_active_paypal_subscription_with_valid_baid(mock_baid, mock_result):
    result = check_active_paypal_subscription(baid='I-OSKQBX1CWVSJ')
    assert_is_not_none(result)
    eq_(result, 'I-OSKQBX1CWVSJ')


@patch('paypal.get_paypal_billing_agreement_id_for_guid', return_value='I-RUE3FCPF10P5')
@patch('paypal.get_paypal_billing_agreement', return_value=None)
def test_check_active_paypal_subscription_with_valid_guid_returs_false(mock_baid, mock_result):
    result = check_active_paypal_subscription(guid=uuid4().get_hex())
    assert_is_not_none(result)
    eq_(result, False)


@patch('paypal.get_paypal_billing_agreement_id_for_guid', return_value=None)
@patch('paypal.get_paypal_billing_agreement', return_value=None)
def test_check_active_paypal_subscription_with_invalid_baid_returns_false(mock_baid, mock_result):
    result = check_active_paypal_subscription(baid='I-RUE3FCPF10P5')
    assert_is_not_none(result)
    eq_(result, False)
