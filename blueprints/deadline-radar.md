# Deadline Radar

## The idea in plain language

Deadline Radar reads documents and proposes calendar actions that a person may
otherwise overlook. It does not decide what the law or a contract requires.
Every proposal shows the original sentence and waits for confirmation before
anything is exported.

### Concrete example

A contract says:

> The agreement renews on 31 December unless cancellation is received at least
> 60 days earlier.

The radar proposes:

- **Action:** send cancellation, if desired;
- **calculated date:** 1 November;
- **event being calculated from:** renewal on 31 December;
- **rule:** 60 calendar days before;
- **source:** contract.pdf, page 7, highlighted sentence;
- **confidence:** high;
- **status:** needs human confirmation.

After checking the source, the user can correct the date, choose reminders, and
export a standard `.ics` calendar file. The app does not write to an online
calendar in the first release.

## Other examples

- “Submit the report by 15 September” — explicit date.
- “Reply within 30 days of receipt” — the app asks for the receipt date because
  the document alone does not contain the required anchor.
- “Payment on the last working day of each month” — recurring rule, with
  holidays left for human confirmation unless a selected local calendar exists.
- “Parents’ meeting next Friday” — ambiguous relative language, always flagged.
- “Notice period: three months” — not itself a deadline until the event and
  direction of calculation are known.

This makes it useful for teachers (calls, projects, meetings, submissions) and
professionals (renewals, tenders, invoices, response periods, certifications).

## First useful release

1. Import individual PDFs, DOCX, email exports, and plain text.
2. Extract explicit dates, relative periods, recurrences, and notice clauses.
3. Represent each proposal as action + date + anchor + rule + source evidence.
4. Ask for missing anchors instead of inventing them.
5. Handle locale, time zone, calendar days versus working days, and year
   rollover explicitly.
6. Detect conflicting dates in the same document set.
7. Confirm/edit/reject workflow followed by local `.ics` export.

## Safe technical approach

Start with deterministic date parsers and rules. A small local language model
may normalize difficult wording, but it must return a constrained structure and
cannot be the date calculator. The calculator should be independently tested
with leap years, daylight-saving transitions, end-of-month rules, and negative
offsets.

The interface must never say “you are compliant” or “this is the legal
deadline.” It should say “candidate date extracted from this passage.” Source
evidence and uncertainty are part of the product, not optional diagnostics.
