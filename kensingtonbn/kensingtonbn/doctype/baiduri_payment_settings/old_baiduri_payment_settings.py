# Copyright (c) 2021, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals

import frappe
from frappe.model.document import Document
from frappe import _
from six.moves.urllib.parse import urlencode
from frappe.utils import get_url, call_hook_method
from frappe.integrations.utils import create_request_log, make_post_request, create_payment_gateway, make_get_request
import json


class BaiduriPaymentSettings(Document):
    supported_currencies = ["BND", "USD"]

    def validate(self):
        create_payment_gateway(self.gateway_name)
        call_hook_method('payment_gateway_enabled', gateway=self.gateway_name)

    def validate_transaction_currency(self, currency):
        if currency not in self.supported_currencies:
            frappe.throw(_(
                "Please select another payment method. This Gateway does not support transactions in currency '{0}'").format(
                currency))

    def get_payment_url(self, **kwargs):
        merchant_id = self.merchant_id
        USER = 'merchant.' + self.merchant_id
        PWD = self.get_password(fieldname="password", raise_exception=False)
        total_amount = kwargs['amount']
        order_id = kwargs['order_id']
        return_url = get_url("./integrations/payment_confirm?order_id=" + str(order_id))
        print('************return_url**************')
        url = "https://baiduri-bpgs.gateway.mastercard.com/api/rest/version/54/merchant/" + merchant_id + "/session"
        auth = (USER, PWD)
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        params = {
            'apiOperation': 'CREATE_CHECKOUT_SESSION',
            'order': {
                'id': order_id,
                'currency': 'BND',
                'amount': total_amount,
                'description': 'Kensingtonbn Payment'

            },
            'interaction': {
                'returnUrl': return_url,
                'operation': 'PURCHASE',
                'displayControl': {
                    'billingAddress': 'HIDE'
                }
            }

        }
        try:
            response = make_post_request(url=url, auth=auth, headers=headers, data=json.dumps(params))
            if response["result"] == "ERROR":
                raise Exception

        except Exception:
            frappe.throw(_("Invalid payment"))

        kwargs.update({
            "merchant_id": merchant_id,
            "session_id": response.get('session', {}).get('id'),
            "session_version": response.get('session', {}).get('version'),
            "result_indicator": response.get('successIndicator'),
            "transaction_id": ''
        })
        self.integration_request = create_request_log(kwargs, "Remote", "Baiduri")
        return get_url("./integrations/baiduri_checkout?{0}".format(urlencode(kwargs)))


def get_transaction_id(order_id):
    doc = frappe.get_doc("Baiduri Payment Settings", "Baiduri Payment Gateway")
    merchant_id = doc.merchant_id
    USER = 'merchant.' + doc.merchant_id
    PWD = doc.get_password(fieldname="password", raise_exception=False)
    url = "https://baiduri-bpgs.gateway.mastercard.com/api/rest/version/54/merchant/" + merchant_id + "/order/" + order_id
    auth = (USER, PWD)
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    try:
        response = make_get_request(url=url, auth=auth, headers=headers)
        if response["result"] == "ERROR":
            raise Exception
    except Exception:
        frappe.throw(_("Invalid payment"))

    return_url = ''
    if response.get('result') == 'SUCCESS':
        # 1- get transaction_id
        transactionId = ''
        transactions = response.get('transaction')
        if transactions:
            for i in transactions:
                if 'acquirer' in i['transaction']:
                    if 'transactionId' in i['transaction']['acquirer']:
                        transactionId = i['transaction']['acquirer']['transactionId']
            if transactionId == '':
                frappe.throw(_("transactionId Not Found"))
        # 2- update transaction_id and status in integration request and get redirect url
        return_url = update_integration_request_status(order_id, {"transaction_id": transactionId}, "Completed")
    else:
        return_url = get_url('./integrations/payment_failed')

    return return_url


def update_integration_request_status(order_id, data, status):
    strQuery = """
		SELECT *
		FROM `tabIntegration Request`
		WHERE reference_docname = %s
		ORDER BY entry_time DESC 
    	Limit 1
	"""
    integration_request = frappe.db.sql(strQuery, order_id, as_dict=True)
    doc = frappe.get_doc("Integration Request", integration_request[0].name)
    doc.update_status(data, status)
    frappe.get_doc(doc.get("reference_doctype"), doc.get("reference_docname")).run_method("on_payment_authorized",
                                                                                          "Completed")
    frappe.db.commit()
    return_url = get_url('./integrations/payment_success')
    return return_url
