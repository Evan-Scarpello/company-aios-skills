# Build order: overdue-invoice report for the front desk (COO brief, Mon 9:00 AM)

> **Synthetic example.** The company, people, tools and dates are made up. It shows the shape of a coordinator-to-lane brief: one outcome, a done-condition, numbered steps, gates, don'ts and a report line.

Owner's words: "every morning I want to know who is more than 14 days late, without opening the accounting app."

## Today
- Invoices live in the accounting app; we have a read-only API key in the secret store (never print it). Nobody looks at the aging report until month end.
- The front desk reads one shared inbox each morning.

## Goal (done-condition)
A plain report, ready by 7:30 AM each weekday, listing every invoice more than 14 days past due: customer, amount, days late, last reminder date. Nothing is sent to customers.
1. Build it in `<builds>/overdue-report` (new private repo). Read-only against the accounting API.
2. $0: run on the server we already have. Any new paid service goes to the COO first.
3. Output: one markdown file in the front-desk folder, plus a one-line summary in the room ("7 overdue, $4,180 total").
4. Test against a fixture export with fake customers: an invoice at 13, 14 and 15 days late, a paid one, a credit note, and an empty day.
5. Second-model review of the packet before the timer is switched on.
6. The timer is switched on only after the PASS and the COO's go.

## Don'ts
- No emails or texts to customers. Drafting reminders is a separate brief.
- Don't write to the accounting app. Don't store customer data outside the report folder.

## Report
Plan and ETA to the COO within 30 min. Target: packet to the reviewer by Wed 6 PM.
