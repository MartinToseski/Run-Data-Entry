"""
Full project pipeline runner.

Executes:
1. Aggregation
2. Storage

Intended to be run daily.
"""

import sys
from datetime import date, datetime, timedelta
from .aggregator import aggregate_all
from .storage import save_row


def run_backfill(start_date: date, end_date: date):
    current = start_date

    while current <= end_date:
        try:
            main(current)
        except Exception as e:
            print(f"Failed for {current}: {e}")

        current += timedelta(days=1)


def main(target_date: date) -> None:
    """
    Execute full pipeline.
    """
    print("- - - Running Data Pipeline - - -")
    print(f"(for {target_date})")
    row = aggregate_all(target_date)
    print(row)
    save_row(row)
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    try:
        if len(sys.argv) == 3:
            start = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
            end = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()
            run_backfill(start, end)
        elif len(sys.argv) == 2:
            input_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
            main(input_date)
        else:
            main(date.today())
    except KeyboardInterrupt:
        print("Pipeline interrupted.")
    except Exception as e:
        print("Pipeline failed:", e)