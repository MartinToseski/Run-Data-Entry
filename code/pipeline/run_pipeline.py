"""
Full project pipeline runner.

Executes:
1. Aggregation
2. Storage

Intended to be run daily.
"""

from .aggregator import aggregate_all
from .storage import save_row


def main() -> None:
    """
    Execute full pipeline.
    """
    print("- - - Running Data Pipeline - - -")
    row = aggregate_all()
    #print(row)
    save_row(row)
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Pipeline interrupted.")
    except Exception as e:
        print("Pipeline failed:", e)