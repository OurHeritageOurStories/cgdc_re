## Overview
This repo contains named entity (NE), entity linking (EL) and relation extraction (RE) annotations of the textual metadata of items drawn from community-generated digital content (CGDC): digital-born historical/cultural archive collections that have been developed by communities. The dataset consists of annotation files (in .ann format) produced by the [Brat annotation tool](https://brat.nlplab.org). The annotation files correspond to 237 CGDC items, 50 of which were collected from the [Morrab Library](https://morrablibrary.org.uk/) and the other 187 from [The People's Collection Wales (PCW)](https://www.peoplescollection.wales/). In addition, this repository also includes the files needed to replicate the experiment conducted for the paper "Relation Extraction for Constructing Knowledge Graphs: Enhancing the Searchability of Community-Generated Digital Content ({CGDC}) Collections".

## Usage
Researchers and practitioners can utilise this dataset in testing and evaluating Entity Linking and Relation Extraction models on CGDC metadata. It provides a set of annotations that can serve as a benchmark for assessing EL / RE model performance. As we are still in the process of seeking permission to directly share and distribute the raw textual metadata that was anntotated, for now we can provide only the annotations. Interested users of the dataset will thus have to reconstruct the text themselves, following the instructions below.

## Dataset Description
- **Annotations**: Each annotation file corresponds to a CGDC item and has a filename that starts with the collection name abbreviation ("morrab" or "pcw") followed by an underscore and the item ID within the collection. For example, the annotation file `morrab_10286.ann` contains the annotations for the item with ID `10286` in the Morrab Library. 
- **Text reconstruction**: The original text for each item can be reconstructed by creating a plain text file whose filename should bear a similar prefix as the corresponding annotation file, but with ".txt" as file extension. For instance, to create the corresponding plain text file for `morrab_10286.ann`, one has to create a file called `morrab_10286.txt`. The content of the text file should be a concatenation of the title and description of each item, with a newline in between them. The titles and descriptions of items can be retrieved by accessing the following URLs, where `item_ID` should be replaced with the item ID of interest:
  - for Morrab Library items: `https://photoarchive.morrablibrary.org.uk/items/show/<item_ID>`
  - for PCW items: `https://www.peoplescollection.wales/items/<item_ID>`

## Experiment files
- `create_dataset_from_brat_annotations.py`: script to create the dataset used for the experiments. Both the ".txt" and ".ann" files are needed for each document in order to generate the dataset.
- `mapping_of_relation_types.csv`: table with relations of interest.
- `relation_types_priorities.txt`: list of priorities for relations of interest in case of a tie.
- `nli_for_re.ipynb`: main notebook which runs the experiment and generates the Cypher code to populate a knowledge graph in Neo4j.

## Citation
If you use this dataset in your research or work, please cite the following paper:
```
@inproceedings{marinov2024relation,
  title={Relation Extraction for Constructing Knowledge Graphs: Enhancing the Searchability of Community-Generated Digital Content ({CGDC}) Collections},
  author={Martin Marinov and Youcef Benkhedda and Ewan Hannaford and Marc Alexander and Goran Nenadic and Riza Batista-Navarro},
  booktitle={Workshop on Deep Learning and Large Language Models for Knowledge Graphs},
  year={2024},
  url={https://openreview.net/forum?id=ZOKivqqTjg}
}
```

