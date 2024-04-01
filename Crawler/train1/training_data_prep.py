import spacy
from spacy.tokens import DocBin
import pandas as pd
import re

pd.set_option('display.max_colwidth', None)

def massage_data(address):
    cleansed_address1 = re.sub(r'(,)(?!\s)', ', ', address)
    cleansed_address2 = re.sub(r'(\\n)', ', ', cleansed_address1)
    cleansed_address3 = re.sub(r'(?!\s)(-)(?!\s)', ' - ', cleansed_address2)
    cleansed_address = re.sub(r'\.', '', cleansed_address3)
    return cleansed_address

def get_address_span(address=None, address_component=None, label=None):
    span = None
    if pd.isna(address_component) or str(address_component) == 'nan':
        return None
    else:
        address_component1 = re.sub(r'\.', '', address_component)
        address_component2 = re.sub(r'(?!\s)(-)(?!\s)', ' - ', address_component1)
        span = re.search('\\b(' + re.escape(address_component2) + ')\\b', address)
        if span:
            return (span.start(), span.end(), label)
        else:
            return None

def extend_list(entity_list,entity):
    if pd.isna(entity):
        return entity_list
    else:
        entity_list.append(entity)
        return entity_list

def create_entity_spans(df):
    print(df.columns)
    entity_spans = []
    for index, row in df.iterrows():
        text = row.iloc[0]  # Assuming 'Address' contains the text data
        annotations = []
        # Define entity labels and corresponding column names
        entity_labels = ['ROAD', 'ROAD_NUMBERS', 'CITY', 'REGION', 'COUNTRY', 'POSTCODE']
        column_names = ['ROAD', 'ROAD_NUMBERS', 'CITY', 'REGION', 'COUNTRY', 'POSTCODE']
        # Iterate over entity labels and extract annotations from corresponding columns
        for label, column in zip(entity_labels, column_names):
            entity_value = row[column]
            if pd.notna(entity_value):
                # If entity value exists, add it to annotations
                start = text.find(entity_value)
                end = start + len(entity_value)
                annotations.append((start, end, label))
        entity_spans.append((text, {"entities": annotations}))
    print(entity_spans)
    return entity_spans


def get_doc_bin(training_data, nlp):
    db = DocBin()
    for text, annotations in training_data:
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annotations['entities']:
            span = doc.char_span(start, end, label=label)
            if span is not None:
                ents.append(span)
        doc.ents = ents
        db.add(doc)
    return db




# Load blank English model
nlp = spacy.blank("en")

# Define custom entity tag list
tag_list = ["BuildingTag", "BuildingNoTag", "RecipientTag", "StreetNameTag", "ZipCodeTag", "CityTag", "StateTag", "CountryTag"]

# Read the training dataset into pandas
df_train = pd.read_csv(filepath_or_buffer="./corpus/dataset/us-train-dataset.csv", sep=",", dtype=str,skipinitialspace=True)
print(df_train.columns)
# Get entity spans for training data
df_entity_spans_train = create_entity_spans(df_train.astype(str))
training_data = df_entity_spans_train

# Get and persist DocBin to disk for training data
doc_bin_train = get_doc_bin(training_data, nlp)
doc_bin_train.to_disk("./corpus/spacy-docbins/train.spacy")

# Read the validation dataset into pandas
df_test = pd.read_csv(filepath_or_buffer="./corpus/dataset/us-test-dataset.csv", sep=",", dtype=str,skipinitialspace=True)

# Get entity spans for validation data
df_entity_spans_test = create_entity_spans(df_test.astype(str))
validation_data = df_entity_spans_test  # Remove .values.tolist()

# Get and persist DocBin to disk for validation data
doc_bin_test = get_doc_bin(validation_data, nlp)
doc_bin_test.to_disk("./corpus/spacy-docbins/test.spacy")
