import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from invoice_metadata import checked_metadata,FIELDS,valid_iban,observed_amounts,dates_in

TEXT='Rechnung Nr. RE-0001\nKundennummer 00123\nBelegdatum 30.10.2026\nFällig am 14.11.2026\nNetto EUR20,00\nUmsatzsteuer 19%: EUR3,80\nGesamtbetrag EUR23,80\nIBAN DE89 3704 0044 0532 0130 00'
def metadata():
    result={'title':'Rechnung','issuer':'Example GmbH','document_type':'Rechnung','issue_date':'2026-10-30','issue_date_evidence':'Belegdatum 30.10.2026','tags':[],'warnings':[],'invoice_fields':{k:{'value':None,'evidence':None} for k in FIELDS}}
    for key,value,quote in [('invoice_number','RE-0001','Rechnung Nr. RE-0001'),('customer_number','00123','Kundennummer 00123'),('due_date','2026-11-14','Fällig am 14.11.2026'),('net_amount','20.00','Netto EUR20,00'),('tax_amount','3.80','Umsatzsteuer 19%: EUR3,80'),('gross_amount','23.80','Gesamtbetrag EUR23,80'),('currency','EUR','Gesamtbetrag EUR23,80'),('iban','DE89370400440532013000','IBAN DE89 3704 0044 0532 0130 00')]:
        result['invoice_fields'][key]={'value':value,'evidence':quote}
    return result

class InvoiceMetadataTests(unittest.TestCase):
    def test_explicit_fields_survive_repeat_validation_without_inventing_missing_values(self):
        result=checked_metadata(metadata(),TEXT)
        self.assertEqual(result['invoice_fields']['gross_amount']['value'],'23.80')
        self.assertEqual(result['invoice_fields']['currency']['value'],'EUR')
        self.assertIsNone(result['invoice_fields']['order_number']['value'])
        self.assertEqual(checked_metadata(result,TEXT),result)

    def test_invented_quotes_amounts_dates_and_stripped_customer_zeroes_are_not_applied(self):
        for key,value,quote in [('invoice_number','FAKE','Rechnung Nr. FAKE'),('gross_amount','99.00','Gesamtbetrag EUR23,80'),('due_date','2030-11-14','Fällig am 14.11.2026'),('customer_number','123','Kundennummer 00123')]:
            with self.subTest(key=key):
                raw=metadata();raw['invoice_fields'][key]={'value':value,'evidence':quote}
                result=checked_metadata(raw,TEXT)
                self.assertIsNone(result['invoice_fields'][key]['value'])
                self.assertTrue(result['warnings'])

    def test_iban_checksum_and_evidence_are_both_required(self):
        self.assertTrue(valid_iban('DE89370400440532013000'))
        self.assertFalse(valid_iban('DE88370400440532013000'))
        raw=metadata();raw['invoice_fields']['iban']['value']='DE88370400440532013000'
        self.assertIsNone(checked_metadata(raw,TEXT)['invoice_fields']['iban']['value'])

    def test_unlabelled_dollars_do_not_become_us_dollars(self):
        raw=metadata();raw['invoice_fields']['currency']={'value':'USD','evidence':'Total $23.80'}
        result=checked_metadata(raw,TEXT+'\nTotal $23.80')
        self.assertIsNone(result['invoice_fields']['currency']['value'])

    def test_localized_amounts_and_written_dates_are_supported(self):
        from decimal import Decimal
        self.assertIn(Decimal('1234.56'),observed_amounts('EUR1.234,56'))
        self.assertIn('2026-10-30',dates_in('October 30, 2026'))
        self.assertIn('2026-10-30',dates_in('30. Okt. 2026'))

    def test_inconsistent_printed_totals_are_preserved_with_a_review_warning(self):
        raw=metadata();raw['invoice_fields']['gross_amount']={'value':'24.80','evidence':'Gesamtbetrag EUR24,80'}
        result=checked_metadata(raw,TEXT.replace('23,80','24,80'))
        self.assertEqual(result['invoice_fields']['gross_amount']['value'],'24.80')
        self.assertTrue(any('rechnerisch' in x for x in result['warnings']))

if __name__=='__main__':unittest.main()
