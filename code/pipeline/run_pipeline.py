"""
Full project pipeline runner.

Executes:
1. Aggregation
2. Storage

Intended to be run daily.
"""

import sys
from datetime import date, datetime
from .aggregator import aggregate_all
from .storage import save_row


def main(target_date) -> None:
    """
    Execute full pipeline.
    """
    print("- - - Running Data Pipeline - - -")
    print(f"(for {target_date})")
    row = aggregate_all(target_date)
    print(row)
    #save_row(row)
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            input_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
        else:
            input_date = date.today()
        main(input_date)
    except KeyboardInterrupt:
        print("Pipeline interrupted.")
    except Exception as e:
        print("Pipeline failed:", e)