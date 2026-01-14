#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import json
import logging
import os
import re

from nltk.corpus import wordnet

_curr_dir = os.path.dirname(os.path.abspath(__file__))


class Synonym:
    def __init__(self):
        self.dictionary = None
        path = _curr_dir + "/dictionary/synonym.json"
        with open(path, "r") as f:
            try:
                self.dictionary = json.load(f)
                self.dictionary = {
                    (k.lower() if isinstance(k, str) else k): v
                    for k, v in self.dictionary.items()
                }
            except Exception:
                logging.warning("Missing synonym.json")
                self.dictionary = {}

        if not len(self.dictionary.keys()):
            logging.warning("Fail to load synonym")

    def lookup(self, tk, topn=8):
        if not tk or not isinstance(tk, str):
            return []

        # Check the custom dictionary (both keys and tk are already lowercase)
        key = re.sub(r"[ \t]+", " ", tk.strip())
        res = self.dictionary.get(key, [])
        if isinstance(res, str):
            res = [res]
        if res:  # Found in dictionary → return directly
            return res[:topn]

        # If not found and tk is purely alphabetical → fallback to WordNet
        if re.fullmatch(r"[a-z]+", tk):
            wn_set = {
                re.sub("_", " ", syn.name().split(".")[0])
                for syn in wordnet.synsets(tk)
            }
            wn_set.discard(tk)  # Remove the original token itself
            wn_res = [t for t in wn_set if t]
            return wn_res[:topn]

        # Nothing found in either source
        return []

    def add_syn(self, word: str, synonyms: str) -> None:
        """
        Add a synonym for a word to the dictionary.

        Args:
            word: The word to add synonyms for
            synonyms: A single synonym string
        """
        if not word or not isinstance(word, str):
            logging.warning("Invalid word provided to add_syn")
            return

        if not synonyms:
            logging.warning("No synonyms provided to add_syn")
            return

        # Convert to lowercase for consistency
        word = word.lower()

        # Get existing synonyms for the word
        existing_syns = self.dictionary.get(word, [])

        # Convert existing synonyms to list if it's a string
        if isinstance(existing_syns, str):
            existing_syns = [existing_syns]

        # Convert new synonym to lowercase
        new_synonym = synonyms.lower()

        # Create a set of existing synonyms for quick lookup
        existing_set = {s.lower() for s in existing_syns}

        # Add new synonym if it doesn't already exist
        if new_synonym not in existing_set:
            existing_syns.append(new_synonym)

        # Update the dictionary
        self.dictionary[word] = existing_syns

        logging.info(f"Added synonym '{synonyms}' for '{word}'")


if __name__ == "__main__":
    dl = Synonym()
    print(dl.dictionary)