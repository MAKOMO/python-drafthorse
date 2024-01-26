import os
from datetime import date
from decimal import Decimal

from drafthorse.models.accounting import ApplicableTradeTax
from drafthorse.models.document import Document
from drafthorse.models.note import IncludedNote
from drafthorse.models.tradelines import LineItem
from drafthorse.models.party import TaxRegistration
from drafthorse.models.payment import PaymentTerms
from drafthorse.pdf import attach_xml


def test_EN16931_Einfach_example():
    doc = Document()
    doc.context.guideline_parameter.id = "urn:cen.eu:en16931:2017"
    doc.header.id = "471102"
    doc.header.type_code = "380"
    doc.header.issue_date_time = date.fromisoformat("20180305")

    note = IncludedNote()
    note.content.add("Rechnung gemäß Bestellung vom 01.03.2018.")
    doc.header.notes.add(note)

    note = IncludedNote()
    # BT-21
    note.subject_code = "REG"  # REG=Regulatory information; code list: UNTDID 4451 "Text subject code qualifier"
    # BT-22 Kommentarfeld
    note.content.add(
        "Lieferant GmbH\nLieferantenstraße 20\n80333 München\nDeutschland\nGeschäftsführer: Hans Muster\nHandelsregisternummer: H A 123"
    )
    doc.header.notes.add(note)

    li = LineItem()
    li.document.line_id = "1"
    li.product.global_id = ("0160", "4012345001235")
    li.product.seller_assigned_id = "TB100A4"
    li.product.name = "Trennblätter A4"
    li.agreement.gross.amount = Decimal("9.9000")
    li.agreement.net.amount = Decimal("9.9000")
    li.delivery.billed_quantity = (Decimal("20.0000"), "H87")
    li.settlement.trade_tax.type_code = "VAT"
    li.settlement.trade_tax.category_code = "S"
    li.settlement.trade_tax.rate_applicable_percent = Decimal("19.00")
    li.settlement.monetary_summation.total_amount = Decimal("198.00")
    doc.trade.items.add(li)

    li = LineItem()
    li.document.line_id = "2"
    li.product.global_id = ("0160", "4000050986428")
    li.product.seller_assigned_id = "ARNR2"
    li.product.name = "Joghurt Banane"
    li.agreement.gross.amount = Decimal("5.5000")
    li.agreement.net.amount = Decimal("5.5000")
    li.delivery.billed_quantity = (Decimal("50.0000"), "H87")
    li.settlement.trade_tax.type_code = "VAT"
    li.settlement.trade_tax.category_code = "S"
    li.settlement.trade_tax.rate_applicable_percent = Decimal("7.00")
    li.settlement.monetary_summation.total_amount = Decimal("275.00")
    doc.trade.items.add(li)

    doc.trade.agreement.seller.id = "549910"
    doc.trade.agreement.seller.global_id.add(("0088", "4000001123452"))
    doc.trade.agreement.seller.name = "Lieferant GmbH"
    doc.trade.agreement.seller.address.postcode = "80333"
    doc.trade.agreement.seller.address.line_one = "Lieferantenstraße 20"
    doc.trade.agreement.seller.address.city_name = "München"
    doc.trade.agreement.seller.address.country_id = "DE"
    seller_tr_fc = TaxRegistration()
    seller_tr_fc.id = ("FC", "201/113/40209")
    doc.trade.agreement.seller.tax_registrations.add(seller_tr_fc)
    seller_tr_va = TaxRegistration()
    seller_tr_va.id = ("VA", "DE123456789")
    doc.trade.agreement.seller.tax_registrations.add(seller_tr_va)

    doc.trade.agreement.buyer.id = "GE2020211"
    doc.trade.agreement.buyer.name = "Kunden AG Mitte"
    doc.trade.agreement.buyer.address.postcode = "69876"
    doc.trade.agreement.buyer.address.line_one = "Kundenstraße 15"
    doc.trade.agreement.buyer.address.city_name = "Frankfurt"
    doc.trade.agreement.buyer.address.country_id = "DE"

    doc.trade.delivery.event.occurrence = date.fromisoformat("20180305")

    doc.trade.settlement.currency_code = "EUR"
    trade_tax = ApplicableTradeTax()
    trade_tax.calculated_amount = Decimal("19.25")
    trade_tax.type_code = "VAT"
    trade_tax.basis_amount = Decimal("275.00")
    trade_tax.category_code = "S"
    trade_tax.rate_applicable_percent = Decimal("7.00")
    doc.trade.settlement.trade_tax.add(trade_tax)
    trade_tax = ApplicableTradeTax()
    trade_tax.calculated_amount = Decimal("37.62")
    trade_tax.type_code = "VAT"
    trade_tax.basis_amount = Decimal("198.00")
    trade_tax.category_code = "S"
    trade_tax.rate_applicable_percent = Decimal("19.00")
    doc.trade.settlement.trade_tax.add(trade_tax)

    pt = PaymentTerms()
    pt.description = "Zahlbar innerhalb 30 Tagen netto bis 04.04.2018, 3% Skonto innerhalb 10 Tagen bis 15.03.2018"
    doc.trade.settlement.terms.add(pt)

    doc.trade.settlement.monetary_summation.line_total = Decimal("473.00")
    doc.trade.settlement.monetary_summation.charge_total = Decimal("0.00")
    doc.trade.settlement.monetary_summation.allowance_total = Decimal("0.00")
    doc.trade.settlement.monetary_summation.tax_basis_total = Decimal("473.00")
    doc.trade.settlement.monetary_summation.tax_total = (Decimal("56.87"), "EUR")
    doc.trade.settlement.monetary_summation.grand_total = Decimal("529.87")
    doc.trade.settlement.monetary_summation.prepaid_total = Decimal("0.00")
    doc.trade.settlement.monetary_summation.due_amount = Decimal("529.87")

    ### Serialization and PDF Generation

    xml = doc.serialize(schema="FACTUR-X_EN16931")
    with open("factur-x.xml", "wb") as f:
        f.write(xml)
    with open(
        os.path.join(
            os.path.dirname(__file__), "tests", "samples", "invoice_pdf17.pdf"
        ),
        "rb",
    ) as original_file:
        new_pdf_bytes = attach_xml(original_file.read(), xml, "EN 16931")

    with open("EN16931_Einfach.pdf", "wb") as f:
        f.write(new_pdf_bytes)


test_EN16931_Einfach_example()
