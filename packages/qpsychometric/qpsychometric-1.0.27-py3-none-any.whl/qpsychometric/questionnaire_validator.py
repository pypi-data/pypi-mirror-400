#!/usr/bin/env python
# coding: utf-8

"""
General Questionnaire Validation Module

This module provides validation capabilities for psychometric questionnaires
including linguistic acceptability, internal consistency, Cronbach's alpha,
and correlation analysis.

Usage:
    from questionnaire_validator import QuestionnaireValidator

    validator = QuestionnaireValidator(
        questionnaire_name="CS",
        questions=cs_questions,
        factors=["Kindness", "Common Humanity", ...],
        index=["index"],
        scales=["frequency"],
        result_path="results/",
        mnli_pipelines=["typeform/distilbert-base-uncased-mnli"]
    )

    validator.run_validation()
"""

import torch
import pandas as pd
from pathlib import Path
import gc
import json
import os
import time
import numpy as np
from tqdm.auto import tqdm
import warnings
import pingouin as pg
from functools import partial
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
from collections import defaultdict
from qlatent.qmnli.qmnli import *
from qlatent.qmnli.qmnli import _QMNLI, QMNLI


class QuestionnaireValidator:
    """
    A general validation framework for psychometric questionnaires.

    Parameters
    ----------
    questionnaire_name : str
        Short name/abbreviation of the questionnaire (e.g., "CS", "ASI", "GAD7")
    questions : list
        List of question objects from the questionnaire
    factors : list
        List of factor names in the questionnaire
    index : list, optional
        Index dimensions for the questionnaire (default: ["index"])
    scales : list, optional
        Scale dimensions for the questionnaire (default: ["frequency"])
    result_path : str or Path, optional
        Path to save results (default: "results/")
    mnli_pipelines : list, optional
        List of MNLI model identifiers to use for validation
    softmax_settings : list, optional
        Softmax settings (default: [True, False])
    filters : dict, optional
        Filter configurations for questions
    device : int or str, optional
        Device to use for computation (default: auto-detect GPU)
    q_range : list, optional
        Question score range (default: [5, 0])
    """

    def __init__(
        self,
        questionnaire_name,
        questions,
        factors,
        index=None,
        scales=None,
        result_path="results/",
        mnli_pipelines=None,
        softmax_settings=None,
        filters=None,
        device=None,
        q_range=None,
        update=True
    ):
        self.questionnaire_name = questionnaire_name
        self.raw_questions = questions
        self.factors = factors
        self.index = index if index is not None else ["index"]
        self.scales = scales if scales is not None else ["frequency"]
        self.result_path = Path(result_path)
        self.update = update

        # Default MNLI pipelines if not provided
        if mnli_pipelines is None:
            self.mnli_pipelines = [
                'typeform/distilbert-base-uncased-mnli', # 0.8211920529801324
                'typeform/mobilebert-uncased-mnli', # 0.8354559347936832
                #'cross-encoder/nli-roberta-base',
                'MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli', # 0.91207335710647
                'cross-encoder/nli-deberta-base', # 0.8824248599083037
                #'cross-encoder/nli-distilroberta-base',
                'MoritzLaurer/mDeBERTa-v3-base-mnli-xnli', # 0.875802343352012
                'cross-encoder/nli-MiniLM2-L6-H768', # 0.8660213958227203
                'navteca/bart-large-mnli', # 0.901782985226694
                'digitalepidemiologylab/covid-twitter-bert-v2-mnli', # 0.8748853795211411
                'joeddav/bart-large-mnli-yahoo-answers', # 0.8097809475292919
                'Narsil/deberta-large-mnli-zero-cls', # 0.9125827814569536
                #'microsoft/deberta-large-mnli',
                "joeddav/xlm-roberta-large-xnli", # 0.878043810494142
                #'microsoft/deberta-base-mnli',
                'katanemo/bart-large-mnli', # 0.901782985226694
                #'Alireza1044/albert-base-v2-mnli',
                'mjwong/e5-large-mnli', #  0.856342333163525
                #'yoshitomo-matsubara/bert-large-uncased-mnli',
                'mjwong/multilingual-e5-large-xnli', # 0.870402445236882
                #'yoshitomo-matsubara/bert-base-uncased-mnli',
                'navteca/nli-deberta-v3-large', # 0.901884870096791
                #'yoshitomo-matsubara/bert-base-uncased-mnli_from_bert-large-uncased-mnli',
                'symanto/mpnet-base-snli-mnli', # 0.875700458481916
                'valhalla/distilbart-mnli-12-6', # 0.8919001528273052
                'facebook/bart-large-mnli', # 0.901782985226694,
                'utahnlp/mnli_microsoft_deberta-v3-large_seed-3', # 0.915741212429954
                'FacebookAI/roberta-large-mnli', # 0.905960264900662
            ]
        else:
            self.mnli_pipelines = mnli_pipelines

        # Softmax settings
        self.softmax_settings = softmax_settings if softmax_settings is not None else [True, False]

        # Default filters if not provided
        if filters is None:
            self.filters = self._get_default_filters()
        else:
            self.filters = filters

        # Device configuration
        if device is None:
            self.device = 0 if torch.cuda.is_available() else -1
        else:
            self.device = device

        # Question range
        self.q_range = q_range if q_range is not None else [5, 0]

        # Initialize models
        self._init_models()

        # Create result directory
        if not self.result_path.exists():
            os.makedirs(self.result_path)

        # Split questions with filters
        self.split_questions = self._split_all_questions()

        print(f"Initialized {questionnaire_name} Validator:")
        print(f"  - Questions: {len(self.raw_questions)}")
        print(f"  - Factors: {self.factors}")
        print(f"  - Scales: {self.scales}")
        print(f"  - Index: {self.index}")
        print(f"  - Device: {self.device}")
        print(f"  - Result path: {self.result_path}")

    def _get_default_filters(self):
        """Get default filter configuration based on scales."""
        return {
            'unfiltered': {},
            'positiveonly': lambda q: q.get_filter_for_postive_keywords(self.scales)
        }

    def _init_models(self):
        """Initialize sentence embedding and COLA models."""
        print("Loading validation models...")
        self.sentence_embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.cola = pipeline(
            "text-classification",
            "mrm8488/deberta-v3-small-finetuned-cola",
            device=self.device
        )
        print("Models loaded successfully.")

    def _split_question(self, Q, verbose=False):
        """
        Split a question into multiple variants with different softmax strategies and filters.

        Parameters
        ----------
        Q : callable
            Question class constructor
        verbose : bool
            Whether to print splitting progress

        Returns
        -------
        list
            List of filtered question variants
        """
        result = []
        for s in self.scales:
            q = QCACHE(Q())
            for sf in self.softmax_settings:
                for filter_name, filter_func in self.filters.items():
                    # Get filter value
                    if callable(filter_func):
                        filter_val = filter_func(Q())
                    else:
                        filter_val = filter_func

                    if sf:
                        # Apply softmax with both index and scale
                        qsf = QSOFTMAX(q, dim=[self.index[0], s])
                        qsf_f = QFILTER(qsf, filter_val, filtername=filter_name)
                        if verbose:
                            print((self.index, s), sf, filter_name)
                        result.append(qsf_f)

                        # Apply softmax with scale only
                        qsf = QSOFTMAX(q, dim=s)
                        qsf_f = QFILTER(qsf, filter_val, filtername=filter_name)
                        if verbose:
                            print(s, sf, filter_name)
                        result.append(qsf_f)

                        # Apply softmax with index only
                        qsf = QSOFTMAX(q, dim=self.index[0])
                        qsf_f = QFILTER(qsf, filter_val, filtername=filter_name)
                        if verbose:
                            print(self.index[0], sf, filter_name)
                        result.append(qsf_f)
                    else:
                        # No softmax
                        qsf = QPASS(q, descupdate={'softmax': ''})
                        qsf_f = QFILTER(qsf, filter_val, filtername=filter_name)
                        if verbose:
                            print(s, sf, filter_name)
                        result.append(qsf_f)
        return result

    def _split_all_questions(self, verbose=False):
        """Split all questions into variants."""
        print(f"Splitting {len(self.raw_questions)} questions...")
        all_split = []
        for Q in self.raw_questions:
            all_split.append(self._split_question(Q, verbose=verbose))
        print(f"Generated {sum(len(qs) for qs in all_split)} question variants.")
        return all_split

    def _linguistic_acceptabilities(self, q, index, scale, question_name,
                                   student_id, output_path=None, save_to_file=False):
        """
        Calculate linguistic acceptability metrics for a question.

        Metrics include COLA score, semantic similarity, and silhouette score.
        """
        if output_path is None:
            output_path = self.result_path
        else:
            output_path = Path(output_path)

        description = q._descriptor
        strFactor = description['Factor']
        strOrdinal = str(description.get('Ordinal', 0))

        # Clean the string to get the original question
        strOriginal = description['Original']
        strOriginal = 'none' if strOriginal is None else strOriginal
        strOriginal = strOriginal.replace(strFactor, '', 1)
        strOriginal = strOriginal.replace(strOrdinal, '', 1)
        strOriginal = strOriginal.replace('.', '', 1)
        strOriginal = strOriginal.strip()

        rows = []

        # Calculate silhouette score
        partial_internal_consistency = partial(
            q.internal_consistency,
            filter={},
            index=index,
            scale=scale
        )
        try:
            silhouette_score = partial_internal_consistency(
                measure='silhouette_score',
                metric='correlation'
            )
        except Exception as e:
            print(e)
            print('silhouette_score is set to -1')
            silhouette_score = -1

        # Check if already calculated
        if hasattr(q, 'linguistic_acceptability'):
            q.linguistic_acceptability['silhouette_score'] = silhouette_score
            return q.linguistic_acceptability

        # Calculate for each keyword permutation
        for kmap in q._keywords_map:
            score = {}
            score['question_name'] = question_name
            context = q._context_template.format_map(kmap)
            answer = q._answer_template.format_map(kmap)
            score['original_question'] = strOriginal

            # COLA score
            cola_score = self.cola(context + " " + answer)[0].get('score')
            score['cola_score'] = cola_score
            score['param'] = kmap
            strPermutation = context + " " + answer
            score['question_permutation'] = strPermutation

            # Semantic similarity
            embeddings1 = self.sentence_embedding_model.encode(strOriginal, convert_to_tensor=True)
            #embeddings2 = self.sentence_embedding_model.encode(strPermutation, convert_to_tensor=True)
            embeddings2 = self.sentence_embedding_model.encode(context, convert_to_tensor=True)
            cosine_scores = util.cos_sim(embeddings1, embeddings2)
            score['semantic_similarity'] = cosine_scores.item()

            score['silhouette_score'] = silhouette_score
            rows.append(score)

        # Create DataFrame
        filename = output_path / 'linguistic_acceptabilities.csv'
        df = pd.DataFrame(rows)
        df['student_id'] = student_id
        df = df[[
            'student_id', 'question_name', 'original_question', 'param',
            'question_permutation', 'cola_score', 'semantic_similarity', 'silhouette_score'
        ]]

        if save_to_file:
            if filename.exists():
                df.to_csv(filename, index=False, header=None, mode='a', encoding='utf-8-sig')
            else:
                df.to_csv(filename, index=False, encoding='utf-8-sig')

        q.linguistic_acceptability = df
        return df

    def _question_attributes(self, q):
        """Extract attributes from a question."""
        score = {}
        score['questionnair'] = q._descriptor['Questionnair']
        score['factor'] = q._descriptor['Factor']
        score['ordinal'] = q._descriptor['Ordinal']
        score['scale'] = q._descriptor['scale']
        score['index'] = q._descriptor['index']
        score['filter'] = q._descriptor['filter']
        score['softmax'] = q._descriptor['softmax']
        score["original"] = q._descriptor['Original']
        score['Q'] = f"{score['questionnair']}{score['factor']}{score['ordinal']}"
        score['context_template'] = q._context_template
        score['answer_template'] = q._answer_template
        score['dimensions'] = q._dimensions
        score['model'] = q.model.model_identifier if q.model else ""
        return score

    def _get_question_features(self, q, student_id='student_id', output_path=None, save_to_file=False):
        """Get all features for a question including linguistic metrics."""
        if output_path is None:
            output_path = self.result_path

        score = self._question_attributes(q)
        score['mean_score'] = q.mean_score()
        index = q._index
        scale = q._scale
        linguistic_df = self._linguistic_acceptabilities(
            q, index=index, scale=scale, question_name=score['Q'],
            student_id=student_id, output_path=output_path, save_to_file=save_to_file
        )
        row = linguistic_df[['cola_score', 'silhouette_score']].mean(axis=0)
        row_dict = dict(row)
        row_dict['semantic_similarity'] = linguistic_df['semantic_similarity'].quantile(0.75)
        score = score | row_dict
        return score

    @staticmethod
    def _extract_epoch(model_path):
        """Extract epoch number from model path."""
        if 'epoch-' in model_path.name:
            i = model_path.name.find('epoch-')
            j = model_path.name.find('_', i)
            if j > 0:
                epoch = int(model_path.name[i + len('epoch-'):j])
            else:
                epoch = int(model_path.name[i + len('epoch-'):])
        elif 'checkpoint-' in model_path.name:
            i = model_path.name.find('checkpoint-')
            j = model_path.name.find('_', i)
            if j > 0:
                epoch = int(model_path.name[i + len('checkpoint-'):j])
            else:
                epoch = int(model_path.name[i + len('checkpoint-'):])
        else:
            epoch = 0
        return epoch

    @staticmethod
    def _extract_run(model_path):
        """Extract run number from model path."""
        try:
            if 'run' in model_path.name:
                for part in model_path.name.split('_'):
                    if 'run' in part:
                        return int(part.replace('run', ''))
            else:
                return -1
        except Exception as e:
            print(e)
            return -1

    @staticmethod
    def _get_mnli_score(checkpoint_path):
        """Get MNLI score from checkpoint if available."""
        mnli_score_path = checkpoint_path / 'all_results.json'
        if not mnli_score_path.exists():
            mnli_score_path = checkpoint_path.parent / (checkpoint_path.name + '_mnli_eval') / 'all_results.json'
        if mnli_score_path.exists():
            with open(mnli_score_path) as f:
                return json.load(f)["eval_accuracy"]
        else:
            return -1

    def _run_questions(self, questions, mnli_checkpoint, train_process, finetune_dataset):
        """Run validation on a list of questions."""
        rows = []
        checkpoint = Path(mnli_checkpoint.model_identifier)
        for q_raw in tqdm(questions, desc="Processing questions"):
            q = q_raw.run(mnli_checkpoint)
            score = self._get_question_features(q)
            score['epoch'] = self._extract_epoch(checkpoint)
            score['train_process'] = train_process
            score['dataset'] = finetune_dataset
            score['run'] = self._extract_run(checkpoint.parent)
            score['mnli_score'] = self._get_mnli_score(checkpoint)
            score['range'] = (q._weights_flat.min(), q._weights_flat.max())
            score['score'] = np.interp(
                score['mean_score'],
                [q._weights_flat.min(), q._weights_flat.max()],
                self.q_range
            )
            rows.append(score)
            gc.collect()
            torch.cuda.empty_cache()
        return rows

    def _calc_scores(self, questions, checkpoint, train_process, finetune_dataset):
        """Calculate scores for questions using a specific checkpoint."""
        mnli_checkpoint = pipeline("zero-shot-classification", str(checkpoint), device=self.device)
        mnli_checkpoint.model_identifier = str(checkpoint)
        rows = self._run_questions(questions, mnli_checkpoint, train_process, finetune_dataset)
        return rows

    @staticmethod
    def _add_epochs_to_rows(rows, mlm_epoch, mnli_checkpoint):
        """Add epoch information to result rows."""
        for score in rows:
            score['mlm_epoch'] = mlm_epoch
            score['mnli_checkpoint'] = mnli_checkpoint
        return rows

    @staticmethod
    def _write_to_csv(rows, output_path):
        """Write results to CSV file."""
        df = pd.DataFrame(rows)
        if output_path.exists():
            df.to_csv(output_path, index=False, header=None, mode='a')
        else:
            df.to_csv(output_path, index=False)

    def run_model_evaluation(self, output_filename=None):
        """
        Run the questionnaire evaluation on all configured MNLI pipelines.

        Parameters
        ----------
        output_filename : str, optional
            Name of the output CSV file (default: "{questionnaire_name}_mnli_results.csv")

        Returns
        -------
        Path
            Path to the output CSV file
        """
        if output_filename is None:
            output_filename = f'{self.questionnaire_name.lower()}_mnli_results.csv'

        output_path = self.result_path / output_filename

        # Flatten all split questions
        questions = []
        for qs in self.split_questions:
            questions.extend(qs)

        print(f"\nRunning model evaluation with {len(questions)} question variants...")

        # Check for existing results
        if output_path.exists():
            temp_df = pd.read_csv(output_path)
            indexes = temp_df.groupby(['model', 'Q']).count().index.values
            used_models = defaultdict(set)
            for k, v in indexes:
                used_models[k].add(v)
        else:
            used_models = {}

        # Run evaluation for each pipeline
        for p in tqdm(self.mnli_pipelines, desc="Evaluating models"):
            print(f"\nEvaluating model: {p}")
            with warnings.catch_warnings():
                try:
                    warnings.simplefilter("ignore")

                    # Skip already evaluated questions if not updating
                    if p in used_models and not self.update:
                        pipeline_questions = []
                        for q in questions:
                            if self._question_attributes(q)['Q'] not in used_models[p]:
                                pipeline_questions.append(q)
                            else:
                                print('skip', p, self._question_attributes(q)['Q'])
                    else:
                        pipeline_questions = questions

                    if len(pipeline_questions) == 0:
                        print(f"All questions already evaluated for {p}, skipping...")
                        continue

                    rows = self._calc_scores(
                        pipeline_questions,
                        Path(p),
                        'base',
                        'evaluation'
                    )
                    rows = self._add_epochs_to_rows(rows, 0, 0)
                    self._write_to_csv(rows, output_path)

                    gc.collect()
                    torch.cuda.empty_cache()
                except Exception as e:
                    print(f"Error evaluating {p}: {e}")

        # Remove duplicates
        df = pd.read_csv(output_path)
        df = df.drop_duplicates(subset=['filter', 'softmax', 'model', 'Q'], keep='last')
        df.to_csv(output_path, index=False)

        print(f"\n✓ Model evaluation complete. Results saved to: {output_path}")
        return output_path

    def load_results(self, csv_path, softmax, positiveonly, value='score', index='model', columns='Q'):
        """
        Load and filter results from CSV.

        Parameters
        ----------
        csv_path : str or Path
            Path to results CSV
        softmax : str or list
            Softmax filter setting
        positiveonly : bool
            Whether to filter for positive-only results
        value : str
            Column to use as values in pivot table
        index : str
            Column to use as index in pivot table
        columns : str
            Column to use as columns in pivot table

        Returns
        -------
        DataFrame
            Pivot table of results
        """
        df = pd.read_csv(csv_path)

        # Filter by softmax
        if df['softmax'].isna().sum() > 0:
            softmax_filter = df['softmax'].isna()
        else:
            softmax_filter = df['softmax'] == ''

        if softmax:
            df = df[df['softmax'] == str(softmax)]
        else:
            df = df[softmax_filter]

        # Filter silhouette scores
        if value != 'silhouette_score':
            pass
        else:
            df = df[df['silhouette_score'] > -1]

        # Filter by positiveonly
        if positiveonly:
            df = df[df['filter'] == "positiveonly"]
        else:
            df = df[df['filter'] == "unfiltered"]

        results_df = pd.pivot_table(df, values=value, index=index, columns=columns, aggfunc='mean')
        return results_df

    def calc_content_validity(self, results_csv, softmax=None, output_filename=None):
        """
        Calculate content validity metrics.

        Parameters
        ----------
        results_csv : str or Path
            Path to results CSV
        softmax : str or list, optional
            Softmax setting to use (default: uses self.index + self.scales)
        output_filename : str, optional
            Name for output file (default: "linguistic_acceptability.csv")

        Returns
        -------
        DataFrame
            Content validity metrics
        """
        if softmax is None:
            softmax = self.index + self.scales

        if output_filename is None:
            output_filename = "linguistic_acceptability.csv"

        cols = ['semantic_similarity', 'cola_score', 'silhouette_score']

        results = []
        for softmax_filter in [softmax]:
            q_res = [
                self.load_results(results_csv, softmax=softmax_filter, positiveonly=False, value=v).mean(axis=0)
                for v in cols
            ]
            results.append(pd.concat(q_res, axis=1))

        linguistic_acceptability_df = pd.concat(results, axis=0)
        linguistic_acceptability_df.columns = ['semantic_similarity', 'cola_score', 'silhouette_score']

        output_path = self.result_path / output_filename
        linguistic_acceptability_df.to_csv(output_path, index=True)

        print(f"\n✓ Content validity metrics saved to: {output_path}")
        return linguistic_acceptability_df.sort_values('silhouette_score')

    def calc_cronbach_alpha(self, results_csv, softmax=None, positiveonly=True):
        """
        Calculate Cronbach's alpha for internal consistency.

        Parameters
        ----------
        results_csv : str or Path
            Path to results CSV
        softmax : str or list, optional
            Softmax setting to use
        positiveonly : bool
            Whether to use positive-only filter

        Returns
        -------
        dict
            Dictionary with overall alpha and alpha per factor
        """
        if softmax is None:
            softmax = self.index + self.scales

        value = 'mean_score'

        results = []
        for softmax_filter in [softmax]:
            results.append(
                self.load_results(results_csv, softmax=softmax_filter, positiveonly=positiveonly, value=value)
            )

        data_df = pd.concat(results, axis=1)

        print('\nCronbach Alpha:')
        factor_alphas = {}
        for subset in self.factors:
            feature_subset = [c for c in data_df.columns if subset in c]
            if len(feature_subset) > 1:
                alpha = pg.cronbach_alpha(data=data_df[feature_subset])
                print(f'{subset}: {alpha}')
                factor_alphas[subset] = alpha
            else:
                print(f'{subset}: Insufficient items (n={len(feature_subset)})')

        # Overall alpha
        all_feature_subset = self._get_factor_sub_features(self.factors, data_df)
        if len(all_feature_subset) > 1:
            alpha = pg.cronbach_alpha(data=data_df[all_feature_subset])
            print(f'\n{self.questionnaire_name} Overall: {alpha}')
            overall_alpha = alpha
        else:
            print(f'\n{self.questionnaire_name} Overall: Insufficient items')
            overall_alpha = None

        return {
            'data_df': data_df,
            'overall': overall_alpha,
            'factors': factor_alphas
        }
    
    def test_question_affect_on_cronbach_alpha(self, data_df, specific_factors=None):
        if specific_factors is None:
            # Analyze all questions together without grouping by factors
            subset_df = data_df
            alpha = pg.cronbach_alpha(data=subset_df)
            print('All Questions Alpha:', alpha)
            for feature in subset_df.columns:
                sub = [c for c in subset_df.columns if c != feature]
                alpha = pg.cronbach_alpha(data=subset_df[sub])
                print('without:', feature, 'Alpha:', alpha)
        else:
            # If "all", use all factors; otherwise use the provided list
            if specific_factors == "all":
                specific_factors = self.factors

            # Analyze by specific factors
            for subset in specific_factors:
                feature_subset = [c for c in data_df.columns if subset in c]
                subset_df = data_df[feature_subset]
                alpha = pg.cronbach_alpha(data=subset_df)
                print(subset, 'Alpha:', alpha)
                for feature in subset_df.columns:
                    sub = [c for c in subset_df.columns if c != feature]
                    alpha = pg.cronbach_alpha(data=subset_df[sub])
                    print('without:', feature, 'Alpha:', alpha)

    def get_semantic_similarity(self, q=None):
        """
        Calculate semantic similarity score for a question or all questions.

        Compares each question permutation against the original question
        using sentence embeddings and cosine similarity.

        Parameters
        ----------
        q : Question object, optional
            A question object with _descriptor, _context_template, _answer_template,
            and _keywords_map attributes. If None, calculates for all raw questions.

        Returns
        -------
        float or DataFrame
            If q is provided: 75th percentile semantic similarity score
            If q is None: DataFrame with index as question names and single column 'semantic_similarity'
        """
        # If no question provided, calculate for all raw questions
        if q is None:
            results = {}
            for Q in tqdm(self.raw_questions, desc="Calculating semantic similarity"):
                q_instance = Q()
                description = q_instance._descriptor
                strFactor = description['Factor']
                strOrdinal = str(description.get('Ordinal', 0))

                # Clean the string to get the original question
                strOriginal = description['Original']
                strOriginal = 'none' if strOriginal is None else strOriginal
                strOriginal = strOriginal.replace(strFactor, '', 1)
                strOriginal = strOriginal.replace(strOrdinal, '', 1)
                strOriginal = strOriginal.replace('.', '', 1)
                strOriginal = strOriginal.strip()

                scores = []

                # Calculate for each keyword permutation
                for kmap in q_instance._keywords_map:
                    context = q_instance._context_template.format_map(kmap)
                    answer = q_instance._answer_template.format_map(kmap)
                    strPermutation = context + " " + answer

                    # Semantic similarity
                    embeddings1 = self.sentence_embedding_model.encode(strOriginal, convert_to_tensor=True)
                    embeddings2 = self.sentence_embedding_model.encode(context, convert_to_tensor=True)
                    cosine_scores = util.cos_sim(embeddings1, embeddings2)

                    scores.append(cosine_scores.item())

                question_name = f"{description['Questionnair']}{description['Factor']}{description['Ordinal']}"
                results[question_name] = np.percentile(scores, 75)

            df = pd.DataFrame.from_dict(results, orient='index', columns=['semantic_similarity'])
            return df

        # Single question calculation
        description = q._descriptor
        strFactor = description['Factor']
        strOrdinal = str(description.get('Ordinal', 0))

        # Clean the string to get the original question
        strOriginal = description['Original']
        strOriginal = 'none' if strOriginal is None else strOriginal
        strOriginal = strOriginal.replace(strFactor, '', 1)
        strOriginal = strOriginal.replace(strOrdinal, '', 1)
        strOriginal = strOriginal.replace('.', '', 1)
        strOriginal = strOriginal.strip()

        scores = []

        # Calculate for each keyword permutation
        for kmap in q._keywords_map:
            context = q._context_template.format_map(kmap)
            answer = q._answer_template.format_map(kmap)
            strPermutation = context + " " + answer

            # Semantic similarity
            embeddings1 = self.sentence_embedding_model.encode(strOriginal, convert_to_tensor=True)
            embeddings2 = self.sentence_embedding_model.encode(strPermutation, convert_to_tensor=True)
            cosine_scores = util.cos_sim(embeddings1, embeddings2)

            scores.append(cosine_scores.item())

        # Return 75th percentile (used in validation)
        return np.percentile(scores, 75)

    def get_cola_score(self, q=None):
        """
        Calculate COLA (linguistic acceptability) score for a question or all questions.

        Evaluates the grammaticality/linguistic acceptability of each
        question permutation.

        Parameters
        ----------
        q : Question object, optional
            A question object with _context_template, _answer_template,
            and _keywords_map attributes. If None, calculates for all raw questions.

        Returns
        -------
        float or DataFrame
            If q is provided: Mean COLA score across all permutations
            If q is None: DataFrame with index as question names and single column 'cola_score'
        """
        # If no question provided, calculate for all raw questions
        if q is None:
            results = {}
            for Q in tqdm(self.raw_questions, desc="Calculating COLA scores"):
                q_instance = Q()
                description = q_instance._descriptor

                scores = []

                # Calculate for each keyword permutation
                for kmap in q_instance._keywords_map:
                    context = q_instance._context_template.format_map(kmap)
                    answer = q_instance._answer_template.format_map(kmap)
                    strPermutation = context + " " + answer

                    # COLA score
                    cola_result = self.cola(strPermutation)[0]
                    cola_score = cola_result.get('score')

                    scores.append(cola_score)

                question_name = f"{description['Questionnair']}{description['Factor']}{description['Ordinal']}"
                results[question_name] = np.mean(scores)

            df = pd.DataFrame.from_dict(results, orient='index', columns=['cola_score'])
            return df

        # Single question calculation
        scores = []

        # Calculate for each keyword permutation
        for kmap in q._keywords_map:
            context = q._context_template.format_map(kmap)
            answer = q._answer_template.format_map(kmap)
            strPermutation = context + " " + answer

            # COLA score
            cola_result = self.cola(strPermutation)[0]
            cola_score = cola_result.get('score')

            scores.append(cola_score)

        # Return mean (used in validation)
        return np.mean(scores)


    def calc_correlations(self, results_csv, softmax=None, positiveonly=True, method='spearman'):
        """
        Calculate correlations between factors.

        Parameters
        ----------
        results_csv : str or Path
            Path to results CSV
        softmax : str or list, optional
            Softmax setting to use
        positiveonly : bool
            Whether to use positive-only filter
        method : str
            Correlation method ('spearman' or 'pearson')

        Returns
        -------
        DataFrame
            Correlation matrix
        """
        if softmax is None:
            softmax = self.index + self.scales

        value = 'mean_score'

        results = []
        for softmax_filter in [softmax]:
            results.append(
                self.load_results(results_csv, softmax=softmax_filter, positiveonly=positiveonly, value=value)
            )

        data_df = pd.concat(results, axis=1)
        filtered_df = pd.DataFrame()

        for factor in self.factors:
            feature_subset = self._get_factor_sub_features([factor], data_df)
            if len(feature_subset) > 0:
                filtered_df[factor] = data_df[feature_subset].mean(axis=1)

        # Overall score
        all_feature_subset = self._get_factor_sub_features(self.factors, data_df)
        filtered_df[self.questionnaire_name] = data_df[all_feature_subset].mean(axis=1)

        corr_df = filtered_df.rcorr(method=method)
        print(f"\n✓ Factor correlations ({method}):")
        print(corr_df)

        return corr_df

    @staticmethod
    def _get_factor_sub_features(factor_list, data_df):
        """Get column names that match any factor in the list."""
        feature_subset = []
        for subset in factor_list:
            feature_subset += [c for c in data_df.columns if subset in c]
        return list(set(feature_subset))

    def run_validation(self, output_filename=None):
        """
        Run complete validation pipeline.

        This includes:
        1. Model evaluation on all MNLI pipelines
        2. Content validity analysis
        3. Cronbach's alpha calculation
        4. Factor correlation analysis

        Parameters
        ----------
        output_filename : str, optional
            Base name for output files

        Returns
        -------
        dict
            Dictionary containing all validation results
        """
        print(f"\n{'='*70}")
        print(f"Running Complete Validation for {self.questionnaire_name} Questionnaire")
        print(f"{'='*70}")

        # Step 1: Model evaluation
        results_csv = self.run_model_evaluation(output_filename)

        # Step 2: Content validity
        print(f"\n{'='*70}")
        print("Calculating Content Validity Metrics")
        print(f"{'='*70}")
        content_validity = self.calc_content_validity(results_csv)
        print("\nContent Validity Results:")
        print(content_validity)

        # Step 3: Cronbach's alpha
        print(f"\n{'='*70}")
        print("Calculating Internal Consistency (Cronbach's Alpha)")
        print(f"{'='*70}")
        alpha_results = self.calc_cronbach_alpha(results_csv)

        # Step 4: Correlations
        print(f"\n{'='*70}")
        print("Calculating Factor Correlations")
        print(f"{'='*70}")
        correlations = self.calc_correlations(results_csv)

        print(f"\n{'='*70}")
        print("Validation Complete!")
        print(f"{'='*70}")
        print(f"Results saved in: {self.result_path}")

        return {
            'results_csv': results_csv,
            'content_validity': content_validity,
            'cronbach_alpha': alpha_results,
            'correlations': correlations
        }
