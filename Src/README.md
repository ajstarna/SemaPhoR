This directory contains the code needed to run the system.

There are a few script_* files, which are used to run the python commands for each corresponding stage of the system. 
To get an idea of what commands will be run, use any script with a -d (debug) argument.

The scripts should be run in this order:

./script_Config.py [-d]
- Creates the Output/ subdirectories

./script_Baselines.py [-d]
- Creates and evaluates some simple baseline clusterings, such as putting together words with identical definitions and first letters.

./script_AlignmentValues.py [-d]
- Creates alignment value files for each pair of Alongquian languages. They will be read in later on, when featurizing the pairs.

./script_GeneralModel.py [-d]
- Creates the general SVM model, using the Polynesian file as training data.

./script_GeneralFeatures.py [-d] [-p]
- Featurizes and classifies the Algonquian language pairs based on the general features and model.
- Use the -p argument for parallelizing. Otherwise, it is run sequentially and takes longer. 

./script_GeneralClusters.py [-d] [-e]
- Creates the output clusters from the classified Algonquian pairs.
- Use the -e argument to evaluate the clusters afterwards

./script_SubstringModels.py [-d] [-p]
- Creates the specific substring SVM models for each Algonquian language pair
- Use the -p argument for parallelizing. Otherwise, it is run sequential and takes longer.

./script_SubstringFeatures.py [-d] [-p]
- Featurizes and classifies the Algonquian language pairs based on the substring features and specific pairwise models.
- Use the -p argument for parallelizing. Otherwise, it is run sequential and takes longer.

./script_SubstringClusters.py [-d] [-e]
- Creates the output clusters from the substring classified Algonquian pairs.
- These clusters are based on a combination of the general and specific model scores.
- Use the -e argument to evaluate the clusters afterwards