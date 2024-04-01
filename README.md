# AddressesCrawler

Read a parquet file which contains page domains and crawl for addresses ( geographical location )  and export them to a nice format as following:
country, region, city, postcode, road, and road numbers. 

Main tools:
* python 3.12.2 
* Spacy
* pyap

Encountered issues:
* Addresses could exist on different pages so we should cover all the pages ( went only for home, about and contact pages )
* Pyap is focused mostly on us addresses so Spacy helped a lot to process the addresses


How to run:
cd Crawler
python Crawler.py

To crawl more rows modify the next line:
first_100_rows = next(df.iter_batches(batch_size = 100)) 

To use a different trained model modify the following line:
custom_ner_model_path = "mymodel"  # Update with your model path

To train a model you can use Train1 folder or train2.py

Train1:
  `cd Train1`
  `python training_data_prep.py`
  `python -m spacy train config\config.cfg --paths.train corpus\spacy-docbins\train.spacy --paths.dev corpus\spacy-docbins\test.spacy --output output\models -- 
 training.eval_frequency 10 --training.max_steps 300`

Then must use the new generated model in the output folder
You can add more data to corpus/dataset csv files and retrain the model

Train2:
`python train2.py`
To add more training data edit the file and append to train_data.




