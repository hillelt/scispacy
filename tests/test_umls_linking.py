# pylint: disable=no-self-use,invalid-name
import unittest
import tempfile

import spacy

from scispacy.candidate_generation import CandidateGenerator, create_tfidf_ann_index
from scispacy.umls_linking import UmlsEntityLinker
from scispacy.umls_utils import UmlsKnowledgeBase
from scispacy.abbreviation import AbbreviationDetector

class TestUmlsLinker(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.nlp = spacy.load("en_core_web_sm")

        umls_fixture = UmlsKnowledgeBase("tests/fixtures/umls_test_fixture.json")
        with tempfile.TemporaryDirectory() as dir_name:
            umls_concept_aliases, tfidf_vectorizer, ann_index = create_tfidf_ann_index(dir_name, umls_fixture)
        candidate_generator = CandidateGenerator(ann_index, tfidf_vectorizer, umls_concept_aliases, umls_fixture)

        self.linker = UmlsEntityLinker(candidate_generator)

    def test_naive_entity_linking(self):

        doc = self.nlp("There was a lot of (131)I-Macroaggregated Albumin.")

        # Ents are completely wrong from the web spacy model, correct them manually.
        doc.ents = [doc[5:10]]
        doc = self.linker(doc)

        id_with_score = doc.ents[0]._.umls_ent[0]

        assert id_with_score == ("C0000005", 1.0)
        umls_entity = self.linker.umls.cui_to_entity[id_with_score[0]]
        assert umls_entity.concept_id == "C0000005"
        assert umls_entity.types == ["T116", "T121", "T130"]


    def test_linker_resolves_abbreviations(self):

        detector = AbbreviationDetector(self.nlp)
        self.nlp.add_pipe(detector)
        text = "1-Methyl-4-phenylpyridinium (MPP+) is an abbreviation which doesn't exist in the baby index."
        doc = self.nlp(text)
        # Set abbreviated text (MPP+) to be the only entity, which is also not in the toy umls index.
        doc.ents = (doc[2:3],)
        doc = self.linker(doc)

        id_with_score = doc.ents[0]._.umls_ent[0]
        assert id_with_score == ("C0000098", 1.0)
        umls_entity = self.linker.umls.cui_to_entity[id_with_score[0]]
        assert umls_entity.concept_id == "C0000098"
