# SemaPhoR
Code for SemaPhoR, an automated system for cognate set identification based on semantic, phonetic, and regular correspondence information.

See the Src/ directory Readme for instructions on how to run.

If you use this system as part of your research, please cite:
Adam St Arnaud, David Beck, Grzegorz Kondrak. Identifying Cognate Sets Across Dictionaries of Related Languages. EMNLP 2017

bibtex:
@InProceedings{starnaud-beck-kondrak:2017:EMNLP2017,
  author    = {St Arnaud, Adam  and  Beck, David  and  Kondrak, Grzegorz},
  title     = {Identifying Cognate Sets Across Dictionaries of Related Languages},
  booktitle = {Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing},
  month     = {September},
  year      = {2017},
  address   = {Copenhagen, Denmark},
  publisher = {Association for Computational Linguistics},
  pages     = {2509--2518},
  abstract  = {We present a system for identifying cognate sets across dictionaries of related
	languages. The likelihood of a cognate relationship is calculated on the basis
	of a rich set of features that capture both phonetic and semantic similarity,
	as well as the presence of regular sound correspondences. The similarity scores
	are used to cluster words from different languages that may originate from a
	common proto-word. When tested on the Algonquian language family, our system
	detects 63% of cognate sets while maintaining cluster purity of 70%.},
  url       = {https://www.aclweb.org/anthology/D17-1266}
}
