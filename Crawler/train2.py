import spacy
from spacy.training import Example
import random

# Load a blank English model
nlp = spacy.blank("en")

# Define entity labels
labels = ["ROAD", "ROAD_NUMBERS", "CITY", "REGION", "COUNTRY", "POSTCODE"]

# Add entity recognizer to the pipeline
ner = nlp.add_pipe("ner", last=True)

# Add labels to the entity recognizer
for label in labels:
    ner.add_label(label)

# Define training data (annotated examples)
train_data = [
    ("1600 Amphitheatre Parkway, Mountain View, CA 94043, USA", {"entities": [(0, 4, "ROAD_NUMBERS"), (5, 25, "ROAD"), (27, 40, "CITY"), (42, 50, "POSTCODE"), (52, 55, "COUNTRY")]}),
("503 Maurice St, Monroe, NC 28112", 
{"entities": [(0, 3, "ROAD_NUMBERS"),
 (4, 14, "ROAD"),
 (16, 22, "CITY"),
 (24, 32, "POSTCODE")]}),
    
    ("400 North Broadway Street, Medina, OH, USA", 
{"entities": [(0, 3, "ROAD_NUMBERS"),
 (4, 25, "ROAD"),
 (27, 33, "CITY"),
 (35, 37,"REGION"),
 (39, 42, "COUNTRY")]}),
    ("295 Mahoney Drive, Unit K Telluride, CO 81432", 
{"entities": [(0, 3, "ROAD_NUMBERS"),
 (4, 17,"ROAD"),
 (19, 35,"CITY"),
 (37, 45,"POSTCODE")]}),
]


# Convert training data to Example objects
examples = []
for text, annotations in train_data:
    examples.append(Example.from_dict(nlp.make_doc(text), annotations))

# Check alignment using offsets_to_biluo_tags
for text, annotations in train_data:
    biluo_tags = spacy.training.offsets_to_biluo_tags(nlp.make_doc(text), annotations['entities'])
    print("Text:", text)
    print("BILUO tags:", biluo_tags)

# Train the NER model
nlp.begin_training()
for i in range(10):  # Adjust number of iterations as needed
    random.shuffle(examples)  # Shuffle the examples
    for batch in spacy.util.minibatch(examples, size=2):
        nlp.update(batch)

# Save the trained model
nlp.to_disk("custom_ner_model")

# Test the trained model
test_text = "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA"
doc = nlp(test_text)
for ent in doc.ents:
    print(ent.text, ent.label_)
test_text = "503 Maurice St, Monroe, NC 28112"
doc = nlp(test_text)
for ent in doc.ents:
    print(ent.text, ent.label_)


    
