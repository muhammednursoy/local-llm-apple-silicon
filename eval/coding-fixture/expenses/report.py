def format_amount(amount):
    return f"{amount:,.2f}"


def print_list(records, out):
    for r in sorted(records, key=lambda r: r.date):
        out.write(f"{r.date.isoformat()}  {r.category:<10} {format_amount(r.amount)}\n")
