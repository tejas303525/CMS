# AED to INR Changes

These are the source changes needed to switch the financial display from AED to INR.

## 1. Backend contribution currency

In `backend/server.py`, store new contribution records with `INR`:

```python
doc["currency"] = "INR"
```

## 2. Backend receipt PDF

In `backend/server.py`, print INR on receipts:

```python
[Paragraph(f"INR {c['amount']:,.2f}", big_amount)]
```

And set the receipt detail row:

```python
["Currency", "INR"]
```

## 3. Backend report exports

In `backend/server.py`, update exported report headers:

```python
headers = ["Date", "Receipt #", "Member ID", "Member", "Type", "Amount (INR)", "Payment Mode", "Reference"]
```

```python
headers = ["Month", "Tithe (INR)", "Offering (INR)", "Other (INR)", "Total (INR)"]
```

## 4. Frontend formatter

In `frontend/src/lib/constants.js`, use Indian number formatting and the INR label:

```javascript
export const formatINR = (n) =>
  `INR ${Number(n || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
```

## 5. Frontend labels and reports text

Use the formatter everywhere amounts are displayed:

```javascript
{formatINR(total)}
{formatINR(c.amount)}
{formatINR(summary.annual_total)}
```

Use INR in form and report labels:

```jsx
<label className="field-label">Amount (INR) *</label>
```

```jsx
All financial figures in <strong>INR</strong>.
```

## 6. Backend test expectation

In `backend/tests/test_cms_backend.py`, expect INR for new contributions:

```python
assert d["currency"] == "INR"
```