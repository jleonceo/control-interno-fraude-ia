Versión en español: [README.md](README.md)

# Fraud detection in the general ledger

Eight audit tests on a ledger of accounting entries that flag the lines worth reviewing: duplicates, payments
split to avoid the director's signature, suppliers without documents, impossible dates and Benford's law, among
others.

**Result:** on a sample ledger of 116 lines, the tests find the seven planted anomalies and flag none of the
four legitimate cases that look like fraud, such as an invoice and its payment.

```bash
python probar_todo.py
```

Standard Python, nothing to install, no database and no network. The same tests run on GitHub with two Python
versions.

## The starting problem

If purchases over 3,000 € need the director's signature, someone who wants to avoid it can ask for three
invoices of 3,000 € instead of one of 9,000 €. Each invoice, on its own, is correct. The fraud only shows when
the three are looked at together, and in a ledger of thousands of lines nobody does that by hand. These tests
look at the whole ledger and propose candidates. Deciding whether each one is a mistake, an oversight or fraud
is a job for a person with the documents in hand.

## The eight tests

| Test | What it looks for | Use on real data |
|---|---|---|
| Duplicates | The same line repeated: reference, account, debit and credit | Actionable |
| Split payments | Similar amounts to the same supplier within a few days | Actionable |
| Near duplicates | The same payment repeated with one cent or one reference of difference | Actionable |
| Date consistency | A payment or due date earlier than the entry date | Actionable |
| Benford's law | The first digit of the amounts departs from its natural distribution | Actionable, with over 5,000 amounts |
| Round amounts | Too many round amounts in one account | Supporting signal |
| Supplier without documents | A third-party account moving money with no invoice or reference | Informational, data quality |
| Numbering gaps | Gaps in the entry numbering | Informational, data quality |

Each test also has negative controls: normal cases it must not flag. A sales invoice and its payment touch the
same account with the same reference and are not a duplicate. Monthly payroll of similar amounts is not a split
payment either.

## What comes out

- **Split payment:** account 40000009, with three charges of 3,000 € in five days, 9,000 € in total.
- **Duplicate:** invoice `FAC-DUP-91`.
- **Near duplicate:** account 40000011, with two payments of 742.30 € and 742.31 €.
- **Supplier without documents:** account 41000005.
- **Impossible date:** invoice `FAC-INC-01`, paid before its entry date.
- **Round amounts:** account 62900099, with 6 round amounts in 7 lines.
- **Benford:** tells a manipulated sample from a clean one, with a chi-square of 4,724.5 against 3.9.

## Limits

- The data is synthetic and the anomalies were planted knowing what the tests look for. It shows the
  calculation works, not how many frauds it would find in real accounts.
- Benford needs over 5,000 amounts to be reliable. The sample sets have 4,000, and the program itself answers
  that the test does not apply. A small company rarely has enough volume.
- The generator skips entry numbers at random, so there are 112 gaps in 116 entries. On this data that test
  measures nothing; it only makes sense on a ledger with guaranteed consecutive numbering.
- The three 3,000 € charges show up both as a split payment and as a near duplicate. They are left that way so
  as not to fake a precision that is not there.
- A supplier without documents is usually an old, badly filed entry or a migration, not fraud; that is why the
  test is informational. [caso_real.md](caso_real.md) explains the criterion behind each test.
- Of the COSO internal-control framework, only control activities are programmed. The other four components
  are context.

## Data

Everything is synthetic and comes out the same on every run, with seed 20260713. There is no real or personal
data, and the program only reads: it writes to no database.

## Related repositories

- [analisis-contable](https://github.com/jleonceo/analisis-contable): 2024 income statement and cash with
  pandas, checked by a second route.
- [tesoreria-forecast-ia](https://github.com/jleonceo/tesoreria-forecast-ia): cash forecast tested against the
  past, liquidity ratios and ageing.
- [accounting-agent-swarm](https://github.com/jleonceo/accounting-agent-swarm): AI agents that record accounting
  entries with checks at every step.

---

*Part of [Juan Luis León](https://github.com/jleonceo)'s portfolio · [juanluisleon.vercel.app](https://juanluisleon.vercel.app) · Licence [MIT](LICENSE)*
