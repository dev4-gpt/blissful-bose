"""Synthetic tests of population matching, unresolved labels and aggregate privacy."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from analyze_comprehension_selection import summarize


class SelectionTests(unittest.TestCase):
    def fixture(self):
        arms=('P_txt','P_img','S_txt','S_img');key=[];labels={}
        for i in range(8):
            for c in arms:
                rid=f'PRIVATE_ID_{i}_{c}';key.append(dict(uid=f'PRIVATE_UID_{i}',condition=c,row_id=rid))
                yes=i<{'P_txt':4,'P_img':5,'S_txt':5,'S_img':8}[c]
                comp='UNCERTAIN' if (c=='P_img' and yes) or (c=='S_txt' and i<2) or (c=='S_img' and i<5) else 'UNDERSTANDING'
                labels[rid]=dict(refusal='YES' if yes else 'NO',comprehension=comp)
        return key,labels

    def test_naive_change_is_not_a_paired_crossover(self):
        key,labels=self.fixture();out=summarize(key,labels)
        raw,naive,joint=out['methods']
        self.assertEqual(raw['descriptive_pattern'],'no_crossover_pattern')
        self.assertEqual(naive['descriptive_pattern'],'crossover_pattern')
        self.assertFalse(naive['same_items_across_four_conditions'])
        self.assertEqual(joint['descriptive_pattern'],'no_crossover_pattern')
        self.assertEqual(joint['cells'][0]['valid'],3)
        self.assertNotIn('PRIVATE_',json.dumps(out))

    def test_missing_labels_are_unresolved(self):
        key,labels=self.fixture();labels[key[0]['row_id']]['refusal']=''
        self.assertEqual(summarize(key,labels)['methods'][0]['descriptive_pattern'],'unresolved')

    def test_duplicate_and_incomplete_identity_rejected(self):
        key,labels=self.fixture()
        for bad in (key+[key[0]],key[:-1]):
            with self.assertRaises(ValueError):summarize(bad,labels)
        labels[key[0]['row_id']]['comprehension']='INVALID'
        with self.assertRaises(ValueError):summarize(key,labels)

if __name__=='__main__':unittest.main()
