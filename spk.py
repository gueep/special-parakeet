import hashlib
import argparse
import concurrent.futures

SUPPORTED_ALGORITHMS = ['md5', 'sha1', 'sha256', 'sha512', 'blake2b', 'blake2s', 'sha3_256']

def hash_string(algorithm, text):
    if algorithm in SUPPORTED_ALGORITHMS:
        try:
            return hashlib.new(algorithm, text.encode()).hexdigest()
        except Exception as e:
            print(f"Error hashing '{text}': {e}")
    return None

def compare_hashes(target_hash, hash_list):
    for text, hash_value in hash_list.items():
        if hash_value == target_hash:
            return text
    return None

def process_word(word, hash_type):
    hashed_word = hash_string(hash_type, word)
    return word, hashed_word

def main():
    banner = r"""
     _                               _       
    (_) ___  ___  ___ _ __ ___  __ _| |_ ___ 
    | |/ _ \/ __|/ __| '__/ _ \/ _` | __/ _ \
    | | (_) \__ \ (__| | |  __/ (_| | ||  __/
    |_|\___/|___/\___|_|  \___|\__,_|\__\___|
    """
    print(banner)

    parser = argparse.ArgumentParser(description="Hash comparison tool")
    parser.add_argument("-w", "--wordlist", type=str, help="Path to wordlist file (hashes)")
    parser.add_argument("-d", "--definitions", type=str, help="Path to definitions file (plain passwords)")
    parser.add_argument("-t", "--target_hash", type=str, help="Target hash to compare")
    parser.add_argument("-c", "--hash_type", choices=SUPPORTED_ALGORITHMS, help="Type of hash")
    parser.add_argument("-m", "--multithread", action="store_true", help="Enable multithreading")

    args = parser.parse_args()

    if args.wordlist and args.definitions and args.target_hash and args.hash_type:
        try:
            hash_list = {}
            with open(args.wordlist, 'r') as f:
                wordlist = [line.strip() for line in f]

            if args.multithread:
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(process_word, word, args.hash_type) for word in wordlist]

                    for future in concurrent.futures.as_completed(futures):
                        word, hashed_word = future.result()
                        if word and hashed_word:
                            hash_list[word] = hashed_word
            else:
                for word in wordlist:
                    hashed_word = hash_string(args.hash_type, word)
                    if hashed_word:
                        hash_list[word] = hashed_word

            definitions = {}
            with open(args.definitions, 'r') as f:
                for line in f:
                    parts = line.strip().split(":")
                    word = parts[0]
                    definition = ":".join(parts[1:])
                    definitions[word] = definition

            result = compare_hashes(args.target_hash, hash_list)
            if result:
                if definitions.get(result) is not None:
                    print(f"Found a match: {result}:{definitions[result]}")
                else:
                    print(f"Found a match: {result}")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
