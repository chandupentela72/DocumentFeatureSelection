from document_feature_selection.common import data_converter_python3
from document_feature_selection.pmi import PMI_python3
from scipy.sparse import csr_matrix
import unittest
import numpy
import logging


class TestDataConverter(unittest.TestCase):
    def setUp(self):
        self.input_dict = {
            "label_a": [
                ["I", "aa", "aa", "aa", "aa", "aa"],
                ["bb", "aa", "aa", "aa", "aa", "aa"],
                ["I", "aa", "hero", "some", "ok", "aa"]
            ],
            "label_b": [
                ["bb", "bb", "bb"],
                ["bb", "bb", "bb"],
                ["hero", "ok", "bb"],
                ["hero", "cc", "bb"],
            ],
            "label_c": [
                ["cc", "cc", "cc"],
                ["cc", "cc", "bb"],
                ["xx", "xx", "cc"],
                ["aa", "xx", "cc"],
            ]
        }

    def test_check_same_csr_matrix(self):
        """複数回の変換を実施して、同一のcsr_matrixになることを確認する
        """
        n_joblib_tasks = 2

        csr_matrix_1, label_group_dict_1, vocabulary_1 = data_converter_python3.convert_data(
            labeled_structure=self.input_dict,
            ngram=1,
            n_jobs=n_joblib_tasks
        )
        dense_matrix_1 = csr_matrix_1.toarray()

        csr_matrix_2, label_group_dict_2, vocabulary_2 = data_converter_python3.convert_data(
            labeled_structure=self.input_dict,
            ngram=1,
            n_jobs=n_joblib_tasks
        )
        dense_matrix_2 = csr_matrix_2.toarray()

        csr_matrix_3, label_group_dict_3, vocabulary_3 = data_converter_python3.convert_data(
            labeled_structure=self.input_dict,
            ngram=1,
            n_jobs=n_joblib_tasks
        )
        dense_matrix_3 = csr_matrix_3.toarray()

        assert numpy.array_equal(dense_matrix_1, dense_matrix_2)
        assert numpy.array_equal(dense_matrix_2, dense_matrix_3)
        assert numpy.array_equal(dense_matrix_1, dense_matrix_3)

        assert vocabulary_1 == vocabulary_2
        assert vocabulary_2 == vocabulary_3
        assert vocabulary_1 == vocabulary_3



    def test_basic_convert_data(self):
        """checks it works of not when n_jobs=1, n_process=1

        data convert過程のミスが疑われるので、整合性のチェックをする

        :return:
        """

        csr_matrix_, label_group_dict, vocabulary = data_converter_python3.convert_data(
            labeled_structure=self.input_dict,
            ngram=1,
            n_jobs=1
        )

        assert isinstance(csr_matrix_, csr_matrix)
        assert isinstance(label_group_dict, dict)
        assert isinstance(vocabulary, dict)

        n_correct_sample = 3
        n_correct_featute = 8

        assert csr_matrix_.shape[0] == n_correct_sample
        assert csr_matrix_.shape[1] == n_correct_featute

        dense_matrix_constructed_matrix = csr_matrix_.toarray()

        # vocaburary id of correct matrix is {'cc': 3, 'aa': 1, 'some': 6, 'xx': 7, 'I': 0, 'ok': 5, 'hero': 4, 'bb': 2}
        # label id of correct matrix is {'label_c': 2, 'label_a': 0, 'label_b': 1}
        correct_array_numpy = numpy.array(
            [[2, 3, 1, 0, 1, 1, 1, 0],
             [0, 0, 4, 1, 2, 1, 0, 0],
             [0, 1, 1, 4, 0, 0, 0, 2]
         ]).astype(numpy.int64)
        assert numpy.array_equal(correct_array_numpy, dense_matrix_constructed_matrix)



    def test_multi_process_convert_data(self):
        """checks if it works or not when n_process is more than 1

        :return:
        """

        csr_matrix_, label_group_dict, vocabulary = data_converter_python3.convert_data(
            labeled_structure=self.input_dict,
            ngram=1,
            n_jobs=5
        )

        assert isinstance(csr_matrix_, csr_matrix)
        assert isinstance(label_group_dict, dict)
        assert isinstance(vocabulary, dict)

    def test_n_gram_multi_process_convert_data(self):
        """checks if it works or not when n_process is more than 1, and 3-gram

        :return:
        """

        csr_matrix_, label_group_dict, vocabulary = data_converter_python3.convert_data(
            labeled_structure=self.input_dict,
            ngram=3,
            n_jobs=5
        )

        assert isinstance(csr_matrix_, csr_matrix)
        assert isinstance(label_group_dict, dict)
        assert isinstance(vocabulary, dict)


    def test_get_pmi_feature_dictionary(self):
        """checks if it works or not, that getting scored dictionary object from scored_matrix

        :return:
        """
        csr_matrix_, label_group_dict, vocabulary = data_converter_python3.convert_data(
            labeled_structure=self.input_dict,
            ngram=1,
            n_jobs=5
        )

        assert isinstance(csr_matrix_, csr_matrix)
        assert isinstance(label_group_dict, dict)
        assert isinstance(vocabulary, dict)

        pmi_scored_matrix = PMI_python3.PMI().fit_transform(X=csr_matrix_, n_jobs=5)

        # main part of test
        # when sort is True, cut_zero is True, outformat is dict
        pmi_scored_dictionary_objects = data_converter_python3.get_weight_feature_dictionary(
            scored_matrix=pmi_scored_matrix,
            label_id_dict=label_group_dict,
            feature_id_dict=vocabulary,
            outformat='dict',
            sort_desc=True,
            n_jobs=5
        )
        assert isinstance(pmi_scored_dictionary_objects, dict)
        logging.debug(pmi_scored_dictionary_objects)

        # when sort is True, cut_zero is True, outformat is items
        pmi_scored_dictionary_objects = data_converter_python3.get_weight_feature_dictionary(
            scored_matrix=pmi_scored_matrix,
            label_id_dict=label_group_dict,
            feature_id_dict=vocabulary,
            outformat='items',
            sort_desc=True,
            n_jobs=5
        )
        assert isinstance(pmi_scored_dictionary_objects, list)
        for d in pmi_scored_dictionary_objects: assert isinstance(d, dict)
        logging.debug(pmi_scored_dictionary_objects)

        # when sort is True, cut_zero is False, outformat is dict
        pmi_scored_dictionary_objects = data_converter_python3.get_weight_feature_dictionary(
            scored_matrix=pmi_scored_matrix,
            label_id_dict=label_group_dict,
            feature_id_dict=vocabulary,
            outformat='dict',
            sort_desc=True,
            n_jobs=5
        )
        assert isinstance(pmi_scored_dictionary_objects, dict)
        logging.debug(pmi_scored_dictionary_objects)

        # when sort is True, cut_zero is False, outformat is items
        pmi_scored_dictionary_objects = data_converter_python3.get_weight_feature_dictionary(
            scored_matrix=pmi_scored_matrix,
            label_id_dict=label_group_dict,
            feature_id_dict=vocabulary,
            outformat='items',
            sort_desc=True,
            n_jobs=5
        )
        assert isinstance(pmi_scored_dictionary_objects, list)
        for d in pmi_scored_dictionary_objects: assert isinstance(d, dict)
        logging.debug(pmi_scored_dictionary_objects)


if __name__ == '__main__':
    unittest.main()