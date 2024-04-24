import pytest
import tempfile
import os
from main import Invoice, InvoiceHandler


def test_write_data_to_header_and_read_header(create_invoice_handler):
    example_simplified_header = '01     Name         Surname         Patronymics            Address\n'
    create_invoice_handler.write_data_to_header("Name", "Surname", "Patronymics", "Address")
    header = create_invoice_handler.read_header()
    assert header.split() == example_simplified_header.split()


def test_write_data_to_transaction_and_read_transactions(prepare_full_invoice_with_data):
    transactions = prepare_full_invoice_with_data.read_transactions()
    assert transactions == ['02000001000000000200PLN\n', '02000002000000000300USD\n']


def test_write_data_to_footer_and_read_footer(prepare_full_invoice_with_data):
    footer = prepare_full_invoice_with_data.read_footer()
    assert footer.split() == ["03000002000000000500"]


def test_read_invoice(prepare_full_invoice_with_data):
    invoice = prepare_full_invoice_with_data.read_invoice()
    assert invoice == ['01                        Name                       '
                       'Surname                   Patronymics                       Address\n',
                       '02000001000000000200PLN                                                                       '
                       '                          \n',
                       '02000002000000000300USD                                                                       '
                       '                          \n',
                       '03000002000000000500                                                                          '
                       '                          ']


def test_read_transaction(prepare_full_invoice_with_data):
    transaction = prepare_full_invoice_with_data.read_transaction(1)
    assert transaction.split() == ['02000001000000000200PLN']


def test_modify_header(prepare_full_invoice_with_data):
    new_header = {"name": "Jacob", "surname": "Grela", "patronymic": "Peterson", "address": "Cracow"}
    prepare_full_invoice_with_data.modify_header(new_header)
    assert prepare_full_invoice_with_data.read_header().split() == '01     Jacob       Grela         Peterson      ' \
                                                                   '   Cracow\n'.split()


# ----- FIXTURES -----
@pytest.fixture()
def create_invoice():
    path_to_file = "testfile.txt"
    assert not os.path.exists(path_to_file)
    Invoice(path_to_file)
    yield path_to_file
    assert os.path.exists(path_to_file)
    os.remove(path_to_file)


@pytest.fixture()
def create_invoice_handler(create_invoice):
    handler = InvoiceHandler(create_invoice)
    return handler


@pytest.fixture()
def prepare_full_invoice_with_data(create_invoice_handler):
    create_invoice_handler.write_data_to_header("Name", "Surname", "Patronymics", "Address")
    create_invoice_handler.add_transaction("200", "PLN")
    create_invoice_handler.add_transaction("300", "USD")
    create_invoice_handler.commit()
    return create_invoice_handler
