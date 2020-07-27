import argparse
import firebase_admin
from firebase_admin import credentials, firestore

SERVICE_ACCOUNT_PATH = "./firebase-admin-sdk.json"


class WordsModel:
    def __init__(self, db):
        self.db = db

    def insert_new(self, word, meaning, context="none"):
        word_ref = self.db.collection("words").document(word)
        data = {context: meaning}
        if word_ref.get().exists:
            return word_ref.update(data)
        else:
            word_ref = self.db.collection("words").document(word)
            return word_ref.set(data)

    def get_meanings(self, word):
        word_ref = self.db.collection("words").document(word)
        if word_ref.get().exists:
            return word_ref.get().to_dict()
        else:
            return {}

    def get_all(self):
        words = self.db.collection("words").stream()
        return words


if __name__ == "__main__":
    # Argparser to help interact using the command line
    parser = argparse.ArgumentParser(description="add word to cloud firestore")

    parser.add_argument("-i", help="major args, new word happen to be seen")
    parser.add_argument("-s", help="major args, see word's meanings")
    parser.add_argument("-l", action='store_true', help="major args, see all words and its meaning")
    parser.add_argument("-m", nargs="*", help="minor args, requires -i, meaning of the word")
    parser.add_argument("-c", nargs="*", help="minor args, requires -i, context of the word")

    # Load the args as dict like data structure
    # args = parser.parse_args(["-s", "fixations"])
    args = parser.parse_args()
    major_args = [args.i, args.s, args.l]
    selected_major_args = [0 if args.i is None else 1, 0 if args.s is None else 1, int(args.l)]

    # print(selected_major_args)

    # Check if arguments inputted by user is correct
    # If arguments is none
    if sum(selected_major_args) == 0:
        parser.error("no major args selected")
    # If major arguments is more than 1
    if sum(selected_major_args) > 1:
        parser.error("choose only 1 major args")
    # If major argument -i is inputted but not minor argument -m or -c
    if args.i and (args.m is None or args.c is None):
        parser.error("-i requires -m and -c")

    # Get the firebase credentials and connection ready
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
    words_model = WordsModel(firestore.client())

    # Do work according to major arguments that is inputted
    if args.i:
        words_model.insert_new(args.i, args.m, args.c)
    if args.s:
        for context, meaning in words_model.get_meanings(args.s).items():
            print(f"{context} => {meaning}")
    if args.l:
        words = words_model.get_all()
        for word in words:
            print(f"{word.id} =>")
            for context, meaning in word.to_dict().items():
                print(f"\t{context} => {meaning}")