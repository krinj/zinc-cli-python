import unittest
import uuid

from test.testing_utils import redirect_output
from zinc_cli.commands.create.domain.domain_manager import DomainManager


class TestDomainManager(unittest.TestCase):

    OWNED_DOMAIN = "zinccli.com"
    UNOWNED_DOMAIN = "google.com"
    UNIQUE_DOMAIN = "krintest" + uuid.uuid4().hex[:10] + ".com"

    @classmethod
    def setUpClass(cls) -> None:
        redirect_output()

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def test_user_owns_domain_true(self):
        result = DomainManager.user_owns_domain(self.OWNED_DOMAIN)
        print('result', result)
        self.assertTrue(result)

    def test_user_owns_domain_false(self):
        result = DomainManager.user_owns_domain(self.UNOWNED_DOMAIN)
        print('result', result)
        self.assertFalse(result)

    def test_domain_availability_true(self):
        result = DomainManager.is_domain_available(self.UNIQUE_DOMAIN)
        self.assertTrue(result)

    def test_domain_availability_false(self):
        result = DomainManager.is_domain_available(self.UNOWNED_DOMAIN)
        self.assertFalse(result)

    def test_domain_validation_true(self):
        valid_domains = ["google.com", "hello.net", "amazon.io", "stripe123.com.au"]
        for domain in valid_domains:
            result = DomainManager.validate(domain)
            self.assertTrue(result)

    def test_domain_validation_false(self):
        valid_domains = ["google", "http://hello.net", "amaz-$on.io", "stripe123.com.au.what"]
        for domain in valid_domains:
            result = DomainManager.validate(domain)
            self.assertFalse(result)

