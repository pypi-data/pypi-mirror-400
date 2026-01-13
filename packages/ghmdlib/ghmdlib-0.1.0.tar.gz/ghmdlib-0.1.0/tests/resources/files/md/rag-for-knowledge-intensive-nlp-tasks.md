Table 1: Open-Domain QA Test Scores. For TQA, left column uses the standard test set for OpenDomain QA, right column uses the TQA-Wiki test set. See Appendix D for further details.

|             | Model          |   NQ | TQA             |   WQ | CT   |
|-------------|----------------|------|-----------------|------|------|
| Closed Book | T5-11B [52]    | 34.5 | - /50.1 - /60.5 | 37.4 | - -  |
|             | T5-11B+SSM[52] | 36.6 |                 | 44.7 |      |
| Open        | REALM [20]     | 40.4 | - / -           | 40.7 | 46.8 |
| Book        | DPR [26]       | 41.5 | 57.9 / -        | 41.1 | 50.6 |
|             | RAG-Token      | 44.1 | 55.2/66.1       | 45.5 | 50.0 |
|             | RAG-Seq.       | 44.5 | 56.8/ 68.0      | 45.2 | 52.2 |

Table 2: Generation and classification Test Scores. MS-MARCO SotA is [4], FEVER-3 is [68] and FEVER-2 is [57] *Uses gold context/evidence. Best model without gold access underlined.

| Model             | Jeopardy   | Jeopardy   | MSMARCO   | MSMARCO   | FVR3   | FVR2 Acc.   |
|-------------------|------------|------------|-----------|-----------|--------|-------------|
| Model             | B-1        | QB-1       | R-L       | B-1       | Label  | Label       |
| SotA              | -          | -          | 49.8 *    | 49.9 *    | 76.8   | 92.2 *      |
| BART              | 15.1       | 19.7       | 38.2      | 41.6      | 64.0   | 81.1        |
| RAG-Tok. RAG-Seq. | 17.3       | 22.2       | 40.1      | 41.5      | 72.5   | 89.5        |
|                   | 14.7       | 21.4       | 40.8      | 44.2      | 72.5   | 89.5        |

to more effective marginalization over documents. Furthermore, RAG can generate correct answers even when the correct answer is not in any retrieved document, achieving 11.8% accuracy in such cases for NQ, where an extractive model would score 0%.

## 4.2 Abstractive Question Answering

As shown in Table 2, RAG-Sequence outperforms BART on Open MS-MARCO NLG by 2.6 Bleu points and 2.6 Rouge-L points. RAG approaches state-of-the-art model performance, which is impressive given that (i) those models access gold passages with specific information required to generate the reference answer , (ii) many questions are unanswerable without the gold passages, and (iii) not all questions are answerable from Wikipedia alone. Table 3 shows some generated answers from our models. Qualitatively, we find that RAG models hallucinate less and generate factually correct text more often than BART. Later, we also show that RAG generations are more diverse than BART generations (see §4.5).

## 4.3 Jeopardy Question Generation

Table 2 shows that RAG-Token performs better than RAG-Sequence on Jeopardy question generation, with both models outperforming BART on Q-BLEU-1. 4 shows human evaluation results, over 452 pairs of generations from BART and RAG-Token. Evaluators indicated that BART was more factual than RAG in only 7.1% of cases, while RAG was more factual in 42.7% of cases, and both RAG and BART were factual in a further 17% of cases, clearly demonstrating the effectiveness of RAG on the task over a state-of-the-art generation model. Evaluators also find RAG generations to be more specific by a large margin. Table 3 shows typical generations from each model.

Jeopardy questions often contain two separate pieces of information, and RAG-Token may perform best because it can generate responses that combine content from several documents. Figure 2 shows an example. When generating 'Sun', the posterior is high for document 2 which mentions 'The Sun Also Rises'. Similarly, document 1 dominates the posterior when 'A Farewell to Arms' is generated. Intriguingly, after the first token of each book is generated, the document posterior flattens. This observation suggests that the generator can complete the titles without depending on specific documents. In other words, the model's parametric knowledge is sufficient to complete the titles. We find evidence for this hypothesis by feeding the BART-only baseline with the partial decoding "The Sun . BART completes the generation "The Sun Also Rises" is a novel by this author of "The Sun Also Rises" indicating the title "The Sun Also Rises" is stored in BART's parameters. Similarly, BART will complete the partial decoding "The Sun Also Rises" is a novel by this author of "A with "The Sun Also Rises" is a novel by this author of "A Farewell to Arms" . This example shows how parametric and non-parametric memories work together -the non-parametric component helps to guide the generation, drawing out specific knowledge stored in the parametric memory.

## 4.4 Fact Verification

Table 2 shows our results on FEVER. For 3-way classification, RAG scores are within 4.3% of state-of-the-art models, which are complex pipeline systems with domain-specific architectures and substantial engineering, trained using intermediate retrieval supervision, which RAG does not require.