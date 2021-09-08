# Copyright 2021 eprbell
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import unittest

from dateutil.tz import tzutc

from rp2.configuration import Configuration
from rp2.entry_types import TransactionType
from rp2.in_transaction import InTransaction
from rp2.out_transaction import OutTransaction
from rp2.rp2_decimal import RP2Decimal
from rp2.rp2_error import RP2TypeError, RP2ValueError


class TestInTransaction(unittest.TestCase):
    _configuration: Configuration

    @classmethod
    def setUpClass(cls) -> None:
        TestInTransaction._configuration = Configuration("./config/test_data.config")

    def setUp(self) -> None:
        self.maxDiff = None

    def test_transaction_type(self) -> None:
        self.assertEqual(TransactionType.BUY, TransactionType.type_check_from_string("transaction_type", "buy"))
        self.assertEqual(TransactionType.DONATE, TransactionType.type_check_from_string("transaction_type", "dOnAtE"))
        self.assertEqual(TransactionType.EARN, TransactionType.type_check_from_string("transaction_type", "Earn"))
        self.assertEqual(TransactionType.GIFT, TransactionType.type_check_from_string("transaction_type", "GIFT"))
        self.assertEqual(TransactionType.MOVE, TransactionType.type_check_from_string("transaction_type", "MoVe"))
        self.assertEqual(TransactionType.SELL, TransactionType.type_check_from_string("transaction_type", "sell"))

        with self.assertRaisesRegex(RP2TypeError, "Parameter name is not a string: .*"):
            TransactionType.type_check_from_string(12, "buy")  # type: ignore
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'transaction_type' has non-string value .*"):
            TransactionType.type_check_from_string("transaction_type", 34.6)  # type: ignore
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'transaction_type' has non-string value .*"):
            TransactionType.type_check_from_string("transaction_type", None)  # type: ignore
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'transaction_type' has invalid transaction type value: .*"):
            TransactionType.type_check_from_string("transaction_type", "Cook")

    def test_taxable_in_transaction(self) -> None:
        in_transaction: InTransaction = InTransaction(
            self._configuration,
            "2021-01-02T08:42:43.882Z",
            "B1",
            "BlockFi",
            "Bob",
            "eaRn",
            RP2Decimal("1000.0"),
            RP2Decimal("2.0002"),
            RP2Decimal("0"),
            usd_in_no_fee=RP2Decimal("2000.2"),
            usd_in_with_fee=RP2Decimal("2000.2"),
            unique_id=19,
        )

        InTransaction.type_check("my_instance", in_transaction)
        self.assertTrue(in_transaction.is_taxable())
        self.assertEqual(RP2Decimal("2000.2"), in_transaction.usd_taxable_amount)
        self.assertEqual("19", in_transaction.unique_id)
        self.assertEqual(2021, in_transaction.timestamp.year)
        self.assertEqual(1, in_transaction.timestamp.month)
        self.assertEqual(2, in_transaction.timestamp.day)
        self.assertEqual(8, in_transaction.timestamp.hour)
        self.assertEqual(42, in_transaction.timestamp.minute)
        self.assertEqual(43, in_transaction.timestamp.second)
        self.assertEqual(882000, in_transaction.timestamp.microsecond)
        self.assertEqual(tzutc(), in_transaction.timestamp.tzinfo)
        self.assertEqual("B1", in_transaction.asset)
        self.assertEqual("BlockFi", in_transaction.exchange)
        self.assertEqual("Bob", in_transaction.holder)
        self.assertEqual(TransactionType.EARN, in_transaction.transaction_type)
        self.assertEqual(RP2Decimal("1000"), in_transaction.spot_price)
        self.assertEqual(RP2Decimal("2.0002"), in_transaction.crypto_in)
        self.assertEqual(RP2Decimal("2000.2"), in_transaction.usd_in_no_fee)
        self.assertEqual(RP2Decimal("2000.2"), in_transaction.usd_in_with_fee)
        self.assertEqual(RP2Decimal("0"), in_transaction.usd_fee)
        self.assertEqual(RP2Decimal("2.0002"), in_transaction.crypto_balance_change)
        self.assertEqual(RP2Decimal("2000.2"), in_transaction.usd_balance_change)

        self.assertEqual(
            str(in_transaction),
            """InTransaction:
  id=19
  timestamp=2021-01-02 08:42:43.882000 +0000
  asset=B1
  exchange=BlockFi
  holder=Bob
  transaction_type=TransactionType.EARN
  spot_price=1000.0000
  crypto_in=2.00020000
  usd_fee=0.0000
  usd_in_no_fee=2000.2000
  usd_in_with_fee=2000.2000
  is_taxable=True
  usd_taxable_amount=2000.2000""",
        )
        self.assertEqual(
            in_transaction.to_string(2, repr_format=False, extra_data=["foobar", "qwerty"]),
            """    InTransaction:
      id=19
      timestamp=2021-01-02 08:42:43.882000 +0000
      asset=B1
      exchange=BlockFi
      holder=Bob
      transaction_type=TransactionType.EARN
      spot_price=1000.0000
      crypto_in=2.00020000
      usd_fee=0.0000
      usd_in_no_fee=2000.2000
      usd_in_with_fee=2000.2000
      is_taxable=True
      usd_taxable_amount=2000.2000
      foobar
      qwerty""",
        )
        self.assertEqual(
            in_transaction.to_string(2, repr_format=True, extra_data=["foobar", "qwerty"]),
            (
                "    InTransaction("
                "id='19', "
                "timestamp='2021-01-02 08:42:43.882000 +0000', "
                "asset='B1', "
                "exchange='BlockFi', "
                "holder='Bob', "
                "transaction_type=<TransactionType.EARN: 'earn'>, "
                "spot_price=1000.0000, "
                "crypto_in=2.00020000, "
                "usd_fee=0.0000, "
                "usd_in_no_fee=2000.2000, "
                "usd_in_with_fee=2000.2000, "
                "is_taxable=True, "
                "usd_taxable_amount=2000.2000, "
                "foobar, "
                "qwerty)"
            ),
        )

    def test_non_taxable_in_transaction(self) -> None:
        in_transaction = InTransaction(
            self._configuration,
            "1841-01-02T15:22:03Z",
            "B2",
            "Coinbase",
            "Alice",
            "BuY",
            RP2Decimal("1000"),
            RP2Decimal("2.0002"),
            RP2Decimal("20"),
            unique_id=19,
        )
        self.assertFalse(in_transaction.is_taxable())
        self.assertEqual(RP2Decimal("0"), in_transaction.usd_taxable_amount)
        self.assertEqual("B2", in_transaction.asset)
        self.assertEqual(TransactionType.BUY, in_transaction.transaction_type)
        self.assertEqual(RP2Decimal("2.0002"), in_transaction.crypto_balance_change)
        self.assertEqual(RP2Decimal("2020.2"), in_transaction.usd_balance_change)

        self.assertEqual(
            str(in_transaction),
            """InTransaction:
  id=19
  timestamp=1841-01-02 15:22:03.000000 +0000
  asset=B2
  exchange=Coinbase
  holder=Alice
  transaction_type=TransactionType.BUY
  spot_price=1000.0000
  crypto_in=2.00020000
  usd_fee=20.0000
  usd_in_no_fee=2000.2000
  usd_in_with_fee=2020.2000
  is_taxable=False
  usd_taxable_amount=0.0000""",
        )

    def test_in_transaction_equality_and_hashing(self) -> None:
        in_transaction: InTransaction = InTransaction(
            self._configuration,
            "2021-01-02T08:42:43.882Z",
            "B1",
            "BlockFi",
            "Bob",
            "eaRn",
            RP2Decimal("1000.0"),
            RP2Decimal("2.0002"),
            RP2Decimal("0"),
            usd_in_no_fee=RP2Decimal("2000.2"),
            usd_in_with_fee=RP2Decimal("2000.2"),
            unique_id=19,
        )
        in_transaction2: InTransaction = InTransaction(
            self._configuration,
            "2021-01-02T08:42:43.882Z",
            "B1",
            "BlockFi",
            "Bob",
            "eaRn",
            RP2Decimal("1000.0"),
            RP2Decimal("2.0002"),
            RP2Decimal("0"),
            usd_in_no_fee=RP2Decimal("2000.2"),
            usd_in_with_fee=RP2Decimal("2000.2"),
            unique_id=19,
        )
        in_transaction3: InTransaction = InTransaction(
            self._configuration,
            "2021-01-02T08:42:43.882Z",
            "B1",
            "BlockFi",
            "Bob",
            "eaRn",
            RP2Decimal("1000.0"),
            RP2Decimal("2.0002"),
            RP2Decimal("0"),
            usd_in_no_fee=RP2Decimal("2000.2"),
            usd_in_with_fee=RP2Decimal("2000.2"),
            unique_id=20,
        )
        self.assertEqual(in_transaction, in_transaction)
        self.assertEqual(in_transaction, in_transaction2)
        self.assertNotEqual(in_transaction, in_transaction3)
        self.assertEqual(hash(in_transaction), hash(in_transaction))
        self.assertEqual(hash(in_transaction), hash(in_transaction2))
        # These hashes would only be equal in case of hash collision (possible but very unlikey)
        self.assertNotEqual(hash(in_transaction), hash(in_transaction3))

    def test_bad_to_string(self) -> None:
        in_transaction: InTransaction = InTransaction(
            self._configuration,
            "2021-01-02T08:42:43.882Z",
            "B1",
            "BlockFi",
            "Bob",
            "eaRn",
            RP2Decimal("1000.0"),
            RP2Decimal("2.0002"),
            RP2Decimal("0"),
            usd_in_no_fee=RP2Decimal("2000.2"),
            usd_in_with_fee=RP2Decimal("2000.2"),
            unique_id=19,
        )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'indent' has non-integer value"):
            in_transaction.to_string(None, repr_format=False, extra_data=["foobar", "qwerty"])  # type: ignore
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'indent' has non-positive value.*"):
            in_transaction.to_string(-1, repr_format=False, extra_data=["foobar", "qwerty"])
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'repr_format' has non-bool value .*"):
            in_transaction.to_string(1, repr_format="False", extra_data=["foobar", "qwerty"])  # type: ignore
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'extra_data' is not of type List"):
            in_transaction.to_string(1, repr_format=False, extra_data="foobar")  # type: ignore

    def test_bad_in_transaction(self) -> None:
        with self.assertRaisesRegex(RP2TypeError, "Parameter name is not a string:.*"):
            InTransaction.type_check(None, None)  # type: ignore
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'my_instance' is not of type InTransaction:.*"):
            InTransaction.type_check("my_instance", None)  # type: ignore
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'my_instance' is not of type InTransaction: OutTransaction"):
            InTransaction.type_check(
                "my_instance",
                OutTransaction(
                    self._configuration,
                    "2021-01-12T11:51:38Z",
                    "B1",
                    "BlockFi",
                    "Bob",
                    "SELL",
                    RP2Decimal("10000"),
                    RP2Decimal("1"),
                    RP2Decimal("0"),
                    unique_id=45,
                ),
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'configuration' is not of type Configuration: .*"):
            # Bad configuration
            InTransaction(
                None,  # type: ignore
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'configuration' is not of type Configuration: .*"):
            # Bad configuration
            InTransaction(
                "config",  # type: ignore
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "EARN",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'unique_id' has non-positive value .*"):
            # Bad unique_id
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "Earn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=-19,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'unique_id' has non-integer .*"):
            # Bad unique_id
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "buy",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id="19",  # type: ignore
            )
        with self.assertRaisesRegex(RP2ValueError, "Error parsing parameter 'timestamp': Unknown string format: .*"):
            # Bad timestamp
            InTransaction(
                self._configuration,
                "abcdefg",
                "B1",
                "BlockFi",
                "Bob",
                "BUY",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'timestamp' value has no timezone info: .*"):
            # Bad timestamp
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43",
                "B1",
                "BlockFi",
                "Bob",
                "eARn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'timestamp' has non-string value .*"):
            # Bad timestamp
            InTransaction(
                self._configuration,
                1111,  # type: ignore
                "B1",
                "BlockFi",
                "Bob",
                "EaRn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'asset' value is not known: .*"):
            # Bad asset
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "yyy",
                "BlockFi",
                "Bob",
                "eArN",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'asset' has non-string value .*"):
            # Bad asset
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                1111,  # type: ignore
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000.0"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'exchange' value is not known: .*"):
            # Bad exchange
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "blockfi",
                "Bob",
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'exchange' has non-string value .*"):
            # Bad exchange
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                1111,  # type: ignore
                "Bob",
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'holder' value is not known: .*"):
            # Bad holder
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "qwerty",
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'holder' has non-string value .*"):
            # Bad holder
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                1111,  # type: ignore
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, ".*InTransaction .*, id.*invalid transaction type.*"):
            # Bad transaction type
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "seLl",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'transaction_type' has invalid transaction type value: .*"):
            # Bad transaction type
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter .* has invalid transaction type value: .*"):
            # Bad transaction type
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "cook",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter .* has non-string value .*"):
            # Bad transaction type
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                1111,  # type: ignore
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, ".*InTransaction .*, id.*parameter 'spot_price' cannot be 0"):
            # Bad spot price
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("0"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, ".*InTransaction .*, id.*parameter 'spot_price' cannot be 0"):
            # Bad spot price
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("0.00000000000001"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'spot_price' has non-positive value .*"):
            # Bad spot price
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("-1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'spot_price' has non-RP2Decimal value .*"):
            # Bad spot price
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                "1000",  # type: ignore
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'crypto_in' has zero value"):
            # Bad crypto in
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("0"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'crypto_in' has non-positive value .*"):
            # Bad crypto in
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("-2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'crypto_in' has non-RP2Decimal value .*"):
            # Bad crypto in
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000.0"),
                "2.0002",  # type: ignore
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'usd_fee' has non-positive value .*"):
            # Bad usd fee
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("-20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'usd_fee' has non-RP2Decimal value .*"):
            # Bad usd fee
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                "20",  # type: ignore
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'usd_in_no_fee' has non-positive value .*"):
            # Bad usd in no fee
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("-2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'usd_in_no_fee' has non-RP2Decimal value .*"):
            # Bad usd in no fee
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000.0"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee="2000.2",  # type: ignore
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'usd_in_with_fee' has non-positive value .*"):
            # Bad usd in with fee
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("-2020.2"),
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'usd_in_with_fee' has non-RP2Decimal value .*"):
            # Bad usd in with fee
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=(1, 2, 3),  # type: ignore
                unique_id=19,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'notes' has non-string value .*"):
            # Bad notes
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000.0"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
                notes=35.6,  # type: ignore
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'notes' has non-string value .*"):
            # Bad notes
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000.0"),
                RP2Decimal("2.0002"),
                RP2Decimal("20"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
                notes=[1, 2, 3],  # type: ignore
            )

        with self.assertLogs(level="WARNING") as log:
            # Crypto in * spot price != USD in (without fee)
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("1000"),
                usd_in_no_fee=RP2Decimal("1900.2"),
                usd_in_with_fee=RP2Decimal("2000.2"),
                unique_id=19,
            )
            self.assertTrue(re.search(".* InTransaction .*, id.*crypto_in.*spot_price != usd_in_no_fee:.*", log.output[0]))  # type: ignore

        with self.assertLogs(level="WARNING") as log:
            # USD in (with fee) != USD in (without fee) + USD fee
            InTransaction(
                self._configuration,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                RP2Decimal("1000"),
                RP2Decimal("2.0002"),
                RP2Decimal("18"),
                usd_in_no_fee=RP2Decimal("2000.2"),
                usd_in_with_fee=RP2Decimal("2020.2"),
                unique_id=19,
            )
            self.assertTrue(re.search(".* InTransaction .*, id.*usd_in_with_fee != usd_in_no_fee.*usd_fee:.*", log.output[0]))  # type: ignore


if __name__ == "__main__":
    unittest.main()