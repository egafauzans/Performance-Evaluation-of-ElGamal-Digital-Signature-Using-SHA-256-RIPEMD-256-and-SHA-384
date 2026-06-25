# benchmark.py

import os
import csv
from datetime import datetime

from client import run_client

from config import (
    KEY_SIZES,
    MESSAGE_SIZES,
    HASH_ALGORITHMS,
    ITERATIONS
)


RESULT_DIR = "results"
CSV_FILE = os.path.join(
    RESULT_DIR,
    "benchmark.csv"
)

os.makedirs(
    RESULT_DIR,
    exist_ok=True
)


def main():

    header = [
        "timestamp",
        "hash_algorithm",
        "key_size",
        "message_size",
        "iteration",
        "sign_delay_ms",
        "verify_delay_ms",
        "transmission_delay_ms",
        "valid"
    ]

    with open(
        CSV_FILE,
        mode="w",
        newline=""
    ) as f:

        writer = csv.writer(f)

        writer.writerow(header)

        total_runs = (
            len(HASH_ALGORITHMS)
            * len(KEY_SIZES)
            * len(MESSAGE_SIZES)
            * ITERATIONS
        )

        current_run = 0

        for hash_algo in HASH_ALGORITHMS:

            for key_size in KEY_SIZES:

                for message_size in MESSAGE_SIZES:

                    for iteration in range(
                        1,
                        ITERATIONS + 1
                    ):

                        current_run += 1

                        result = run_client(
                            message_size=message_size,
                            key_size=key_size,
                            hash_algo=hash_algo
                        )

                        writer.writerow([
                            datetime.now(),
                            hash_algo,
                            key_size,
                            message_size,
                            iteration,
                            result["sign_delay_ms"],
                            result["verify_delay_ms"],
                            result["transmission_delay_ms"],
                            result["valid"]
                        ])

                        print(
                            f"[{current_run}/{total_runs}] "
                            f"{hash_algo} | "
                            f"{key_size} bit | "
                            f"{message_size} B | "
                            f"Iter {iteration}"
                        )

    print("\nBenchmark selesai.")
    print(f"Hasil tersimpan di: {CSV_FILE}")


if __name__ == "__main__":
    main()