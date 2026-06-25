# server.py

import socket
import pickle
import time

from elgamal_signature import verify
from hash_utils import sha256_hash, sha384_hash, ripemd256_hash


HOST = "127.0.0.1"
PORT = 5000


def compute_hash(message, hash_algo):

    if hash_algo == "SHA256":
        return sha256_hash(message)

    elif hash_algo == "RIPEMD256":
        return ripemd256_hash(message)

    elif hash_algo == "SHA384":
        return sha384_hash(message)

    else:
        raise ValueError(f"Unsupported hash: {hash_algo}")


def start_server():

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"[SERVER] Listening on {HOST}:{PORT}")

    while True:

        conn, addr = server_socket.accept()

        try:

            data = conn.recv(65536)

            if not data:
                conn.close()
                continue

            packet = pickle.loads(data)

            message = packet["message"]
            signature = packet["signature"]
            public_key = packet["public_key"]
            hash_algo = packet["hash_algo"]

            start_verify = time.perf_counter()

            message_hash = compute_hash(
                message,
                hash_algo
            )

            is_valid = verify(
                message_hash,
                signature,
                public_key
            )

            verify_delay = (
                time.perf_counter()
                - start_verify
            ) * 1000

            response = {
                "valid": is_valid,
                "verify_delay_ms": verify_delay
            }

            conn.sendall(
                pickle.dumps(response)
            )

        except Exception as e:

            # print(f"[SERVER ERROR] {e}")
            import traceback

            print("\n===== SERVER ERROR =====")
            traceback.print_exc()
            print("========================")

        finally:

            conn.close()


if __name__ == "__main__":
    start_server()