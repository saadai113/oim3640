"""
PO Matching System — 2-way and 3-way matching
Flags discrepancies for human review, auto-approves within tolerance.
"""

import csv
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class MatchStatus(Enum):
    APPROVED = "APPROVED"
    FLAGGED = "FLAGGED"
    REJECTED = "REJECTED"


@dataclass
class LineItem:
    description: str
    quantity: float
    unit_price: float

    @property
    def total(self) -> float:
        return round(self.quantity * self.unit_price, 2)


@dataclass
class PurchaseOrder:
    po_number: str
    vendor: str
    items: list[LineItem]

    @property
    def total(self) -> float:
        return round(sum(item.total for item in self.items), 2)


@dataclass
class Invoice:
    invoice_number: str
    po_number: str  # reference back to PO
    vendor: str
    items: list[LineItem]

    @property
    def total(self) -> float:
        return round(sum(item.total for item in self.items), 2)


@dataclass
class GoodsReceipt:
    """Optional — only needed for 3-way matching."""
    receipt_number: str
    po_number: str
    items: list[LineItem]  # what was actually received

    @property
    def total(self) -> float:
        return round(sum(item.total for item in self.items), 2)


@dataclass
class MatchResult:
    status: MatchStatus
    flags: list[str] = field(default_factory=list)
    po_total: float = 0.0
    invoice_total: float = 0.0
    receipt_total: Optional[float] = None
    match_type: str = "2-way"

    def summary(self) -> str:
        lines = [
            f"Match Type : {self.match_type}",
            f"Status     : {self.status.value}",
            f"PO Total   : ${self.po_total:,.2f}",
            f"Inv Total  : ${self.invoice_total:,.2f}",
        ]
        if self.receipt_total is not None:
            lines.append(f"Rcpt Total : ${self.receipt_total:,.2f}")
        if self.flags:
            lines.append("Flags:")
            for f in self.flags:
                lines.append(f"  ⚠ {f}")
        return "\n".join(lines)


def match_po(
    po: PurchaseOrder,
    invoice: Invoice,
    receipt: Optional[GoodsReceipt] = None,
    price_tolerance: float = 0.02,   # 2% price variance allowed
    qty_tolerance: float = 0.0,      # 0% quantity variance — must be exact
) -> MatchResult:
    """
    Core matching logic.
    price_tolerance: fraction (e.g. 0.02 = 2%) price can deviate before flagging
    qty_tolerance:   fraction quantity can deviate before flagging
    """
    flags = []
    match_type = "3-way" if receipt else "2-way"

    # --- Header checks ---
    if invoice.po_number != po.po_number:
        flags.append(
            f"PO number mismatch: PO is '{po.po_number}', "
            f"invoice references '{invoice.po_number}'"
        )

    if invoice.vendor.lower() != po.vendor.lower():
        flags.append(
            f"Vendor mismatch: PO vendor '{po.vendor}', "
            f"invoice vendor '{invoice.vendor}'"
        )

    # --- Line-item checks (PO vs Invoice) ---
    po_items = {item.description.lower(): item for item in po.items}
    inv_items = {item.description.lower(): item for item in invoice.items}

    for desc, inv_item in inv_items.items():
        if desc not in po_items:
            flags.append(f"Invoice line '{desc}' not found in PO")
            continue

        po_item = po_items[desc]

        # Quantity check
        qty_diff = abs(inv_item.quantity - po_item.quantity) / po_item.quantity
        if qty_diff > qty_tolerance:
            flags.append(
                f"Quantity mismatch on '{desc}': "
                f"PO={po_item.quantity}, Invoice={inv_item.quantity}"
            )

        # Price check
        price_diff = abs(inv_item.unit_price - po_item.unit_price) / po_item.unit_price
        if price_diff > price_tolerance:
            flags.append(
                f"Unit price mismatch on '{desc}': "
                f"PO=${po_item.unit_price:.2f}, Invoice=${inv_item.unit_price:.2f} "
                f"({price_diff:.1%} variance)"
            )

    for desc in po_items:
        if desc not in inv_items:
            flags.append(f"PO line '{desc}' missing from invoice")

    # --- 3-way: Receipt vs PO ---
    if receipt:
        if receipt.po_number != po.po_number:
            flags.append(
                f"Receipt PO number mismatch: '{receipt.po_number}' vs '{po.po_number}'"
            )

        rcpt_items = {item.description.lower(): item for item in receipt.items}

        for desc, po_item in po_items.items():
            if desc not in rcpt_items:
                flags.append(f"PO line '{desc}' not in goods receipt")
                continue

            rcpt_item = rcpt_items[desc]
            qty_diff = abs(rcpt_item.quantity - po_item.quantity) / po_item.quantity
            if qty_diff > qty_tolerance:
                flags.append(
                    f"Receipt quantity mismatch on '{desc}': "
                    f"PO={po_item.quantity}, Received={rcpt_item.quantity}"
                )

    # --- Determine status ---
    if not flags:
        status = MatchStatus.APPROVED
    elif any(("not found" in f) or ("mismatch" in f.lower() and "vendor" in f.lower()) for f in flags):
        status = MatchStatus.REJECTED
    else:
        status = MatchStatus.FLAGGED

    return MatchResult(
        status=status,
        flags=flags,
        po_total=po.total,
        invoice_total=invoice.total,
        receipt_total=receipt.total if receipt else None,
        match_type=match_type,
    )


# ---------------------------------------------------------------------------
# CSV loader — test with real data
# ---------------------------------------------------------------------------
# CSV format (all three files use the same columns):
#   description,quantity,unit_price
# Example po.csv:
#   Laptop,20,800.00
#   Mouse,50,25.00

def load_items_from_csv(filepath: str) -> list[LineItem]:
    items = []
    with open(filepath, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            items.append(LineItem(
                description=row["description"],
                quantity=float(row["quantity"]),
                unit_price=float(row["unit_price"]),
            ))
    return items


def match_from_csvs(
    po_number: str, vendor: str,
    po_csv: str, invoice_csv: str, receipt_csv: str = None,
    price_tolerance: float = 0.02, qty_tolerance: float = 0.0,
) -> MatchResult:
    po = PurchaseOrder(po_number, vendor, load_items_from_csv(po_csv))
    inv_number = f"INV-{po_number}"
    inv = Invoice(inv_number, po_number, vendor, load_items_from_csv(invoice_csv))
    receipt = None
    if receipt_csv:
        receipt = GoodsReceipt(f"GR-{po_number}", po_number, load_items_from_csv(receipt_csv))
    return match_po(po, inv, receipt, price_tolerance, qty_tolerance)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 55)
    print("SCENARIO 1: Clean 2-way match (should APPROVE)")
    print("=" * 55)

    po1 = PurchaseOrder(
        po_number="PO-1001",
        vendor="Acme Supplies",
        items=[
            LineItem("Widget A", quantity=100, unit_price=10.00),
            LineItem("Widget B", quantity=50,  unit_price=25.00),
        ]
    )
    inv1 = Invoice(
        invoice_number="INV-5001",
        po_number="PO-1001",
        vendor="Acme Supplies",
        items=[
            LineItem("Widget A", quantity=100, unit_price=10.00),
            LineItem("Widget B", quantity=50,  unit_price=25.00),
        ]
    )
    print(match_po(po1, inv1).summary())

    print("\n" + "=" * 55)
    print("SCENARIO 2: Price variance + missing line (should FLAG/REJECT)")
    print("=" * 55)

    po2 = PurchaseOrder(
        po_number="PO-1002",
        vendor="Beta Corp",
        items=[
            LineItem("Steel Rod", quantity=200, unit_price=5.50),
            LineItem("Steel Plate", quantity=10, unit_price=120.00),
        ]
    )
    inv2 = Invoice(
        invoice_number="INV-5002",
        po_number="PO-1002",
        vendor="Beta Corp",
        items=[
            LineItem("Steel Rod", quantity=200, unit_price=5.90),  # price up ~7%
            # Steel Plate missing from invoice
        ]
    )
    print(match_po(po2, inv2).summary())

    print("\n" + "=" * 55)
    print("SCENARIO 3: 3-way match with receipt quantity short")
    print("=" * 55)

    po3 = PurchaseOrder(
        po_number="PO-1003",
        vendor="Gamma Ltd",
        items=[
            LineItem("Laptop", quantity=20, unit_price=800.00),
        ]
    )
    inv3 = Invoice(
        invoice_number="INV-5003",
        po_number="PO-1003",
        vendor="Gamma Ltd",
        items=[
            LineItem("Laptop", quantity=20, unit_price=800.00),
        ]
    )
    receipt3 = GoodsReceipt(
        receipt_number="GR-9001",
        po_number="PO-1003",
        items=[
            LineItem("Laptop", quantity=18, unit_price=800.00),  # only 18 received
        ]
    )
    print(match_po(po3, inv3, receipt=receipt3).summary())